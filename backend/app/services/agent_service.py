from datetime import datetime
from typing import Optional, List
from uuid import uuid4
import json

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent


class AgentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        name: str,
        slug: str,
        content: str,
        description: Optional[str] = None,
        version: str = "1.0.0",
        author: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Agent:
        existing = await self.db.execute(select(Agent).where(Agent.slug == slug))
        if existing.scalar_one_or_none():
            raise ValueError(f"Agent with slug '{slug}' already exists")

        agent = Agent(
            id=str(uuid4()),
            name=name,
            slug=slug,
            content=content,
            description=description,
            version=version,
            author=author,
            tags=json.dumps(tags) if tags else None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(agent)
        await self.db.flush()
        return agent

    async def get_by_id(self, agent_id: str) -> Optional[Agent]:
        result = await self.db.execute(select(Agent).where(Agent.id == agent_id))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Agent]:
        result = await self.db.execute(select(Agent).where(Agent.slug == slug))
        return result.scalar_one_or_none()

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> tuple[List[Agent], int]:
        query = select(Agent)
        count_query = select(func.count(Agent.id))

        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Agent.name.ilike(search_term),
                    Agent.description.ilike(search_term),
                    Agent.slug.ilike(search_term),
                )
            )
            count_query = count_query.where(
                or_(
                    Agent.name.ilike(search_term),
                    Agent.description.ilike(search_term),
                    Agent.slug.ilike(search_term),
                )
            )

        if tag:
            query = query.where(Agent.tags.like(f"%{tag}%"))
            count_query = count_query.where(Agent.tags.like(f"%{tag}%"))

        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(Agent.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        agents = result.scalars().all()

        return list(agents), total

    async def update(
        self,
        agent_id: str,
        name: Optional[str] = None,
        slug: Optional[str] = None,
        content: Optional[str] = None,
        description: Optional[str] = None,
        version: Optional[str] = None,
        author: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Optional[Agent]:
        agent = await self.get_by_id(agent_id)
        if not agent:
            return None

        if slug and slug != agent.slug:
            existing = await self.db.execute(select(Agent).where(Agent.slug == slug))
            if existing.scalar_one_or_none():
                raise ValueError(f"Agent with slug '{slug}' already exists")

        if name is not None:
            agent.name = name
        if slug is not None:
            agent.slug = slug
        if content is not None:
            agent.content = content
        if description is not None:
            agent.description = description
        if version is not None:
            agent.version = version
        if author is not None:
            agent.author = author
        if tags is not None:
            agent.tags = json.dumps(tags) if tags else None

        agent.updated_at = datetime.utcnow()
        await self.db.flush()
        return agent

    async def delete(self, agent_id: str) -> bool:
        agent = await self.get_by_id(agent_id)
        if not agent:
            return False
        await self.db.delete(agent)
        await self.db.flush()
        return True

