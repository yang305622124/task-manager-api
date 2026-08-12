
import json
import random
import time
import threading
from sqlalchemy import text
from user.daos.db_init import DBConnection
from user.models.t_user_users import TUserUsers
from user.core.redis_client import redis_client  # 全局redis单例

# ==================== 缓存常量配置（统一管理）====================
CACHE_KEY_USER = "user:info:{}"      # 用户详情Key
CACHE_EXPIRE_USER = 3600             # 基础过期时间 1小时
CACHE_EMPTY_EXPIRE = 60              # 空数据缓存（防穿透）60秒
CACHE_WARM_BATCH_SIZE = 200          # 预热分批大小
CACHE_EXPIRE_RANDOM_RANGE = 300      # 过期随机偏移 0~300秒（防雪崩）
CACHE_DELAY_DELETE_SECONDS = 0.5     # 延迟双删延迟时间

# ==================== 工具方法（统一封装）====================
def get_random_expire() -> int:
    """获取随机过期时间，解决缓存集体雪崩"""
    return CACHE_EXPIRE_USER + random.randint(0, CACHE_EXPIRE_RANDOM_RANGE)

def safe_redis_delete(key: str):
    """Redis安全删除（异常降级，删缓存失败不影响主业务）"""
    try:
        redis_client.delete(key)
    except Exception:
        pass

def delay_double_delete(key: str):
    """延迟双删（异步执行，不阻塞接口），解决高并发脏数据问题"""
    def _delay_task():
        time.sleep(CACHE_DELAY_DELETE_SECONDS)
        safe_redis_delete(key)
    # 异步线程执行延迟删除
    threading.Thread(target=_delay_task, daemon=True).start()

class TUserUsersDao:

    @staticmethod
    def create(item: TUserUsers) -> str:
        """创建用户 + 自动写缓存（异常降级）"""
        session = DBConnection().get_session()
        try:
            session.add(item)
            session.commit()
            # 新增写入缓存，随机过期防雪崩，Redis异常降级不阻塞业务
            try:
                redis_client.setex(
                    CACHE_KEY_USER.format(item.user_id),
                    get_random_expire(),
                    json.dumps(item.to_dict(), ensure_ascii=False)
                )
            except Exception:
                pass
            return item.user_id
        except Exception as e:
            session.rollback()
            print(f"创建用户失败: {str(e)}")
            return ""
        finally:
            session.close()

    @staticmethod
    def modify(item: TUserUsers) -> bool:
        """修改用户 + 延迟双删缓存（解决高并发脏数据）"""
        session = DBConnection().get_session()
        try:
            session.merge(item)
            session.commit()
            cache_key = CACHE_KEY_USER.format(item.user_id)
            # 1. 立即删旧缓存
            safe_redis_delete(cache_key)
            # 2. 延迟二次删除，兜底高并发回写脏数据
            delay_double_delete(cache_key)
            return True
        except Exception as e:
            session.rollback()
            print(f"修改用户失败: {str(e)}")
            return False
        finally:
            session.close()

    @staticmethod
    def delete_physical(user_id: str) -> bool:
        """物理删除 + 延迟双删缓存"""
        session = DBConnection().get_session()
        try:
            item = session.query(TUserUsers).get(user_id)
            if not item:
                return False
            session.delete(item)
            session.commit()
            cache_key = CACHE_KEY_USER.format(user_id)
            safe_redis_delete(cache_key)
            delay_double_delete(cache_key)
            return True
        except Exception as e:
            session.rollback()
            print(f"用户物理删除失败: {str(e)}")
            return False
        finally:
            session.close()

    @staticmethod
    def delete_logic(user_id: str) -> bool:
        """逻辑删除 + 延迟双删缓存"""
        session = DBConnection().get_session()
        try:
            item = session.query(TUserUsers).get(user_id)
            if not item:
                return False
            item.del_flag = 0
            session.commit()
            cache_key = CACHE_KEY_USER.format(user_id)
            safe_redis_delete(cache_key)
            delay_double_delete(cache_key)
            return True
        except Exception as e:
            session.rollback()
            print(f"用户逻辑删除失败: {str(e)}")
            return False
        finally:
            session.close()

    @staticmethod
    def getbyid(user_id: str) -> TUserUsers | None:
        """
        【核心缓存查询】
        1. Redis异常自动降级直连DB
        2. 随机过期防雪崩
        3. 空缓存防穿透
        """
        cache_key = CACHE_KEY_USER.format(user_id)
        # 1. Redis异常降级：Redis挂了直接走DB，不报错、不阻塞
        try:
            cache_data = redis_client.get(cache_key)
            if cache_data:
                json_data = json.loads(cache_data)
                # 构造临时模型对象返回（不查库）
                model = TUserUsers()
                for k, v in json_data.items():
                    if hasattr(model, k):
                        setattr(model, k, v)
                return model
        except Exception:
            pass

        # 2. 缓存未命中/Redis异常，直接查数据库
        session = DBConnection().get_session()
        try:
            item = session.query(TUserUsers).get(user_id)
            # Redis正常才回写缓存，异常直接放弃回写，保证可用性
            try:
                if item:
                    # 随机过期时间，杜绝缓存雪崩
                    redis_client.setex(
                        cache_key,
                        get_random_expire(),
                        json.dumps(item.to_dict(), ensure_ascii=False)
                    )
                else:
                    # 防穿透：空数据短期缓存60s
                    redis_client.setex(cache_key, CACHE_EMPTY_EXPIRE, "")
            except Exception:
                pass
            return item
        finally:
            session.close()

    @staticmethod
    def cache_warm_up() -> int:
        """
        【缓存预热】生产可用
        批量预热所有正常有效用户，随机过期防雪崩
        """
        session = DBConnection().get_session()
        try:
            # 查询所有有效用户
            user_list = session.query(TUserUsers).filter(
                TUserUsers.del_flag == 1,
                TUserUsers.status == 1
            ).all()

            count = 0
            for user in user_list:
                cache_key = CACHE_KEY_USER.format(user.user_id)
                # 已存在缓存则跳过（避免重复刷缓存）
                try:
                    if redis_client.exists(cache_key):
                        continue
                    # 随机过期时间写入预热缓存
                    redis_client.setex(
                        cache_key,
                        get_random_expire(),
                        json.dumps(user.to_dict(), ensure_ascii=False)
                    )
                    count += 1
                except Exception:
                    continue

            print(f"【用户缓存预热完成】本次预热 {count} 条热点用户数据")
            return count
        except Exception as e:
            print(f"【用户缓存预热失败】{str(e)}")
            return 0
        finally:
            session.close()

    @staticmethod
    def tolist4all() -> list[TUserUsers]:
        """查询全部（列表不做缓存，实时查询）"""
        session = DBConnection().get_session()
        try:
            return session.query(TUserUsers).all()
        except Exception as e:
            print(f"查询所有用户失败: {str(e)}")
            return []
        finally:
            session.close()

    @staticmethod
    def tolist4sql(sql: str) -> list[TUserUsers]:
        """自定义SQL查询（不缓存）"""
        session = DBConnection().get_session()
        try:
            return session.query(TUserUsers).from_statement(text(sql)).all()
        except Exception as e:
            print(f"用户SQL查询失败: {str(e)}")
            return []
        finally:
            session.close()

    @staticmethod
    def tolist4page(page: int, page_size: int, insql: str, insortname: str, insort: str) -> tuple[list[TUserUsers], int]:
        """分页查询（不缓存）"""
        session = DBConnection().get_session()
        try:
            sql1 = f" SELECT COUNT(1) FROM ( {insql} ) AS _myResults "
            total = session.execute(text(sql1)).scalar() or 0

            i_current = (page - 1) * page_size
            sql2 = f" SELECT * FROM ( {insql} ORDER BY {insortname} {insort} ) AS _myResults LIMIT {page_size} OFFSET {i_current} "
            items = session.query(TUserUsers).from_statement(text(sql2)).all()

            return items, total
        except Exception as e:
            print(f"用户分页查询失败: {str(e)}")
            return [], 0
        finally:
            session.close()

    @staticmethod
    def getcount4sql(insql: str) -> int:
        """统计数量（不缓存）"""
        session = DBConnection().get_session()
        try:
            sql1 = f" SELECT COUNT(1) FROM ( {insql} ) AS _myResults "
            total = session.execute(text(sql1)).scalar() or 0
            return total
        except Exception as e:
            print(f"用户数据统计失败: {str(e)}")
            return 0
        finally:
            session.close()

    @staticmethod
    def is_exist(field: str, value: str) -> bool:
        """唯一性校验（不缓存，实时校验）"""
        session = DBConnection().get_session()
        try:
            count = session.query(TUserUsers).filter(getattr(TUserUsers, field) == value).count()
            return count > 0
        except Exception as e:
            print(f"用户字段唯一性校验失败: {str(e)}")
            return False
        finally:
            session.close()