from sqlalchemy import text
from task_manager_api.daos.db_init import DBConnection
from task_manager_api.models.task import Task


class TaskDao:
    @staticmethod
    def create(item: Task) -> str:
        """创建任务数据"""
        session = DBConnection().get_session()
        try:
            session.add(item)
            session.commit()
            return item.id
        except Exception as e:
            session.rollback()
            print(f"创建任务数据失败: {str(e)}")
            return ""
        finally:
            session.close()

    @staticmethod
    def modify(item: Task) -> bool:
        """根据主键更新任务数据"""
        session = DBConnection().get_session()
        try:
            session.merge(item)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"修改任务数据失败: {str(e)}")
            return False
        finally:
            session.close()

    @staticmethod
    def delete_physical(id: str) -> bool:
        """物理删除：彻底删除数据库数据"""
        session = DBConnection().get_session()
        try:
            item = session.query(Task).get(id)
            if not item:
                return False
            session.delete(item)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"物理删除任务数据失败: {str(e)}")
            return False
        finally:
            session.close()

    @staticmethod
    def getbyid(id: str) -> Task:
        """根据id查询单条任务数据"""
        session = DBConnection().get_session()
        try:
            return session.query(Task).get(id)
        finally:
            session.close()

    @staticmethod
    def tolist4all() -> list[Task]:
        """查询所有任务数据"""
        session = DBConnection().get_session()
        try:
            queryall = session.query(Task).all()
            return queryall
        except Exception as e:
            print(f"查询所有任务数据失败: {str(e)}")
            return []
        finally:
            session.close()

    @staticmethod
    def tolist4sql(sql: str) -> list[Task]:
        """自定义SQL查询任务列表"""
        session = DBConnection().get_session()
        try:
            result = session.query(Task).from_statement(text(sql)).all()
            return result
        except Exception as e:
            print(f"任务SQL查询失败: {str(e)}")
            return []
        finally:
            session.close()

    @staticmethod
    def tolist4page(page: int, page_size: int, insql: str, insortname: str, insort: str) -> tuple[list[Task], int]:
        """任务数据分页查询"""
        session = DBConnection().get_session()
        try:
            # 统计总条数
            sql1 = f" SELECT COUNT(1) FROM ( {insql} ) AS _myResults "
            total = session.execute(text(sql1)).scalar() or 0

            # 分页查询数据
            i_current = (page - 1) * page_size
            sql2 = f" SELECT * FROM ( {insql} ORDER BY {insortname} {insort} ) AS _myResults LIMIT {page_size} OFFSET {i_current} "
            items = session.query(Task).from_statement(text(sql2)).all()

            return items, total
        except Exception as e:
            print(f"任务分页查询失败: {str(e)}")
            return [], 0
        finally:
            session.close()

    @staticmethod
    def getcount4sql(insql: str) -> int:
        """根据自定义SQL统计任务数据量"""
        session = DBConnection().get_session()
        try:
            sql1 = f" SELECT COUNT(1) FROM ( {insql} ) AS _myResults "
            total = session.execute(text(sql1)).scalar() or 0
            return total
        except Exception as e:
            print(f"任务数据统计失败: {str(e)}")
            return 0
        finally:
            session.close()

    @staticmethod
    def is_exist(field: str, value: str) -> bool:
        """判断任务字段值是否存在（唯一性校验）"""
        session = DBConnection().get_session()
        try:
            count = session.query(Task).filter(getattr(Task, field) == value).count()
            return count > 0
        except Exception as e:
            print(f"任务字段唯一性校验失败: {str(e)}")
            return False
        finally:
            session.close()
