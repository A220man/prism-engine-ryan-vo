from datetime import datetime
from sqlalchemy import String, Text, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0.0")
    author: Mapped[str] = mapped_column(String(255), nullable=True)
    tags: Mapped[str] = mapped_column(Text, nullable=True)  # JSON array as string
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_agents_name_slug", "name", "slug"),
    )

    def to_dict(self) -> dict:
        import json
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "content": self.content,
            "version": self.version,
            "author": self.author,
            "tags": json.loads(self.tags) if self.tags else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

