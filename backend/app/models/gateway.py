from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Gateway(Base):
    """网关模型"""
    __tablename__ = "gateways"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="网关名称")
    ip = Column(String(45), nullable=False, comment="网关IP")
    port = Column(Integer, nullable=False, default=22, comment="SSH端口")
    system_user_id = Column(Integer, ForeignKey("system_users.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    system_user = relationship("SystemUser", foreign_keys=[system_user_id])
    creator = relationship("User", foreign_keys=[created_by])
