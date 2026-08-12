from sqlalchemy import Column, String, DateTime
from datetime import datetime
from task_manager_api.daos.db_init import Base


class Task(Base):
    """任务表"""
    __tablename__ = "task"

    id = Column(String(50), primary_key=True, nullable=False, comment="主键ID")
    title = Column(String(200), nullable=True, comment="任务标题")
    description = Column(String(500), nullable=True, comment="任务描述")
    status = Column(String(20), nullable=True, comment="状态(todo | in_progress | done)")
    created_at = Column(DateTime, nullable=True, default=datetime.now, comment="行创建时间")
    updated_at = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment="修改时间")

    def to_dict(self):
        """全字段转字典，适配接口返回，时间标准ISO格式化"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
