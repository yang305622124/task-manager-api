from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 数据库配置（实际项目中建议用配置文件）
DB_CONFIG = {
    "host": "10.211.55.20",
    "port": 3306,
    "user": "root",
    "password": "58fTm6Li*",
    "db": "task-manager-api"
}

# 初始化基础类
Base = declarative_base()


# 数据库连接类（单例模式）
class DBConnection:
    engine = None
    session = None

    def get_engine(self):
        """获取数据库引擎（单例模式）"""
        if not self.engine:
            db_url = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['db']}?charset=utf8mb4"
            self.engine = create_engine(
                db_url,
                pool_size=100,
                max_overflow=200,
                pool_recycle=3600,
                pool_pre_ping=True,
                echo=True
            )
        return self.engine

    def get_session(self):
        """获取数据库会话（每次调用返回新会话）"""
        if not self.session:
            self.session = sessionmaker(bind=self.get_engine())
        return self.session()


# 初始化数据库(建表) - 启动时执行一次 如果数据库里没有表，则创建表
def init_tables():
    # MySql - user 数据库 - 创建数据库表(首次运行时执行)
    from user.daos.db_init import Base, DBConnection
    # 添加对象 from user.models.t_user_apps import T_user_apps
    db = DBConnection()
    Base.metadata.create_all(bind=db.get_engine())