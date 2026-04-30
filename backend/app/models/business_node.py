from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class BusinessNode(Base):
    """业务节点模型"""
    __tablename__ = "business_nodes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="节点名称")
    description = Column(Text, nullable=True, comment="描述")
    parent_id = Column(Integer, ForeignKey("business_nodes.id", ondelete="CASCADE"), nullable=True, index=True, comment="父节点ID")
    sort_order = Column(Integer, default=0, comment="排序")
    gateway_id = Column(Integer, ForeignKey("gateways.id", ondelete="SET NULL"), nullable=True, index=True, comment="绑定的网关ID")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, comment="创建者ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")

    # 自引用关系
    parent = relationship("BusinessNode", remote_side=[id], back_populates="children")
    children = relationship("BusinessNode", back_populates="parent", cascade="all, delete-orphan")

    # 其他关系
    creator = relationship("User", foreign_keys=[created_by])
    permissions = relationship("BusinessNodePermission", back_populates="business_node", cascade="all, delete-orphan")
    gateway = relationship("Gateway", foreign_keys=[gateway_id])
