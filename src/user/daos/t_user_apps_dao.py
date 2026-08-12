
from sqlalchemy import text
from user.daos.db_init import DBConnection
from user.models.t_user_apps import TUserApps


class TUserAppsDao:
    @staticmethod
    def create(item: TUserApps) -> str:
        """创建渠道数据"""
        session = DBConnection().get_session()
        try:
            session.add(item)
            session.commit()
            return item.app_id
        except Exception as e:
            session.rollback()
            print(f"创建渠道数据失败: {str(e)}")
            return ""
        finally:
            session.close()

    @staticmethod
    def modify(item: TUserApps) -> bool:
        """根据主键更新渠道数据"""
        session = DBConnection().get_session()
        try:
            session.merge(item)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"修改渠道数据失败: {str(e)}")
            return False
        finally:
            session.close()

    @staticmethod
    def delete_physical(app_id: str) -> bool:
        """物理删除：彻底删除数据库数据"""
        session = DBConnection().get_session()
        try:
            item = session.query(TUserApps).get(app_id)
            if not item:
                return False
            session.delete(item)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"物理删除渠道数据失败: {str(e)}")
            return False
        finally:
            session.close()

    @staticmethod
    def delete_logic(app_id: str) -> bool:
        """逻辑删除：修改删除标志 del_flag=0，保留数据"""
        session = DBConnection().get_session()
        try:
            item = session.query(TUserApps).get(app_id)
            if not item:
                return False
            item.del_flag = 0
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"逻辑删除渠道数据失败: {str(e)}")
            return False
        finally:
            session.close()

    @staticmethod
    def getbyid(app_id: str) -> TUserApps:
        """根据app_id查询单条渠道数据"""
        session = DBConnection().get_session()
        try:
            return session.query(TUserApps).get(app_id)
        finally:
            session.close()

    @staticmethod
    def tolist4all() -> list[TUserApps]:
        """查询所有渠道数据"""
        session = DBConnection().get_session()
        try:
            queryall = session.query(TUserApps).all()
            return queryall
        except Exception as e:
            print(f"查询所有渠道数据失败: {str(e)}")
            return []
        finally:
            session.close()

    @staticmethod
    def tolist4sql(sql: str) -> list[TUserApps]:
        """自定义SQL查询渠道列表"""
        session = DBConnection().get_session()
        try:
            result = session.query(TUserApps).from_statement(text(sql)).all()
            return result
        except Exception as e:
            print(f"渠道SQL查询失败: {str(e)}")
            return []
        finally:
            session.close()

    @staticmethod
    def tolist4page(page: int, page_size: int, insql: str, insortname: str, insort: str) -> tuple[list[TUserApps], int]:
        """渠道数据分页查询"""
        session = DBConnection().get_session()
        try:
            # 统计总条数
            sql1 = f" SELECT COUNT(1) FROM ( {insql} ) AS _myResults "
            total = session.execute(text(sql1)).scalar() or 0

            # 分页查询数据
            i_current = (page - 1) * page_size
            sql2 = f" SELECT * FROM ( {insql} ORDER BY {insortname} {insort} ) AS _myResults LIMIT {page_size} OFFSET {i_current} "
            items = session.query(TUserApps).from_statement(text(sql2)).all()

            return items, total
        except Exception as e:
            print(f"渠道分页查询失败: {str(e)}")
            return [], 0
        finally:
            session.close()

    @staticmethod
    def getcount4sql(insql: str) -> int:
        """根据自定义SQL统计渠道数据量"""
        session = DBConnection().get_session()
        try:
            sql1 = f" SELECT COUNT(1) FROM ( {insql} ) AS _myResults "
            total = session.execute(text(sql1)).scalar() or 0
            return total
        except Exception as e:
            print(f"渠道数据统计失败: {str(e)}")
            return 0
        finally:
            session.close()

    @staticmethod
    def is_exist(field: str, value: str) -> bool:
        """判断渠道字段值是否存在（唯一性校验）"""
        session = DBConnection().get_session()
        try:
            count = session.query(TUserApps).filter(getattr(TUserApps, field) == value).count()
            return count > 0
        except Exception as e:
            print(f"渠道字段唯一性校验失败: {str(e)}")
            return False
        finally:
            session.close()
