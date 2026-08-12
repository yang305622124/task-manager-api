from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime
from user.daos.db_init import Base


class TUserUsers(Base):
    """用户信息表"""
    __tablename__ = "t_user_users"

    user_id = Column(String(50), primary_key=True, nullable=False, comment="主键ID")
    app_id = Column(String(50), nullable=True, comment="外键,渠道表ID")
    username = Column(String(50), nullable=True, comment="用户名")
    password = Column(String(50), nullable=True, comment="密码")
    tel = Column(String(50), nullable=True, comment="电话")
    sex = Column(Integer, nullable=True, default=1, comment="性别(0 女, 1 男)")
    status = Column(Integer, nullable=True, default=1, comment="状态(0 冻结, 1 激活)")
    del_flag = Column(Integer, nullable=True, default=1, comment="删除标志(0 删除, 1 存在)")
    create_by = Column(String(50), nullable=True, comment="创建者")
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment="创建时间")
    update_by = Column(String(50), nullable=True, comment="修改者")
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment="修改时间")

    def to_dict(self):
        """全字段转字典，适配接口返回，时间标准ISO格式化"""
        return {
            "user_id": self.user_id,
            "app_id": self.app_id,
            "username": self.username,
            #"password": self.password,
            "tel": self.tel,
            "sex": self.sex,
            "status": self.status,
            "del_flag": self.del_flag,
            "create_by": self.create_by,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "update_by": self.update_by,
            "update_time": self.update_time.isoformat() if self.update_time else None
        }
