from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Playbook(Base):
    """剧本模型"""
    __tablename__ = "playbooks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="剧本名称")
    description = Column(Text, nullable=True, comment="描述")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    versions = relationship("PlaybookVersion", back_populates="playbook", cascade="all, delete-orphan", order_by="PlaybookVersion.version.desc()")

    @property
    def latest_version(self):
        """获取最新版本"""
        return self.versions[0] if self.versions else None


class PlaybookVersion(Base):
    """剧本版本模型"""
    __tablename__ = "playbook_versions"

    id = Column(Integer, primary_key=True, index=True)
    playbook_id = Column(Integer, ForeignKey("playbooks.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False, comment="版本号")
    content = Column(Text, nullable=False, comment="剧本内容")
    change_description = Column(Text, nullable=True, comment="变更说明")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    playbook = relationship("Playbook", back_populates="versions")
    creator = relationship("User", foreign_keys=[created_by])

    __table_args__ = (
        {"sqlite_autoincrement": True},
    )
