from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class SystemUser(Base):
    """系统用户模型"""
    __tablename__ = "system_users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="名称")
    username = Column(String(100), nullable=False, comment="SSH用户名")
    auth_type = Column(String(20), nullable=False, comment="认证类型: private_key/password")
    private_key_cipher = Column(Text, nullable=True, comment="加密的私钥")
    password_cipher = Column(Text, nullable=True, comment="加密的密码")
    become_method = Column(String(20), nullable=True, default="sudo", comment="提权方式: sudo/su")
    become_username = Column(String(100), nullable=True, comment="提权用户名")
    become_password_cipher = Column(Text, nullable=True, comment="加密的提权密码")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
