from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Host(Base):
    """主机模型"""
    __tablename__ = "hosts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="主机名")
    business_node_id = Column(Integer, ForeignKey("business_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    ip_internal = Column(String(45), nullable=True, comment="内网IP")
    ip_external = Column(String(45), nullable=True, comment="外网IP")
    ip_preference = Column(String(20), nullable=False, default="internal", comment="IP偏好")
    ssh_port = Column(Integer, nullable=False, default=22, comment="SSH端口")
    cloud_provider = Column(String(50), nullable=True, comment="云厂商")
    system_user_id = Column(Integer, ForeignKey("system_users.id", ondelete="SET NULL"), nullable=True, index=True)
    gateway_id = Column(Integer, ForeignKey("gateways.id", ondelete="SET NULL"), nullable=True, index=True)
    is_enabled = Column(Boolean, nullable=False, default=True, comment="是否启用")
    last_connection_status = Column(String(20), nullable=True, default="unknown", comment="最后连接状态")
    last_connected_at = Column(DateTime(timezone=True), nullable=True, comment="最后连接时间")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    business_node = relationship("BusinessNode", foreign_keys=[business_node_id])
    system_user = relationship("SystemUser", foreign_keys=[system_user_id])
    gateway = relationship("Gateway", foreign_keys=[gateway_id])
    creator = relationship("User", foreign_keys=[created_by])
