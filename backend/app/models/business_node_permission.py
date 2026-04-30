from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class BusinessNodePermission(Base):
    """Business node permission model"""
    __tablename__ = "business_node_permissions"

    id = Column(Integer, primary_key=True, index=True)
    business_node_id = Column(Integer, ForeignKey("business_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    permission_type = Column(String(50), nullable=False)  # view, execute, manage
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Unique constraint: one permission per user per node
    __table_args__ = (
        UniqueConstraint('business_node_id', 'user_id', name='_node_user_uc'),
    )

    # Relationships
    business_node = relationship("BusinessNode", foreign_keys=[business_node_id], back_populates="permissions")
    user = relationship("User", foreign_keys=[user_id])
    creator = relationship("User", foreign_keys=[created_by])
