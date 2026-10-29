from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_operator, TokenData
from app.services.agent_service import AgentService
from pydantic import BaseModel, Field, validator
import re


router = APIRouter(prefix="/agents", tags=["agents"])


class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255, pattern=r"^[a-z0-9-]+$")
    description: Optional[str] = None
    content: str = Field(..., min_length=1)
    version: str = Field(default="1.0.0", max_length=50)
    author: Optional[str] = Field(default=None, max_length=255)
    tags: Optional[List[str]] = Field(default=None)

    @validator("slug")
    def validate_slug(cls, v):
        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError("Slug must contain only lowercase letters, numbers, and hyphens")
        if v.startswith("-") or v.endswith("-"):
            raise ValueError("Slug cannot start or end with hyphen")
        if "--" in v:
            raise ValueError("Slug cannot contain consecutive hyphens")
        return v


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    slug: Optional[str] = Field(default=None, min_length=1, max_length=255, pattern=r"^[a-z0-9-]+$")
    description: Optional[str] = None
    content: Optional[str] = Field(default=None, min_length=1)
    version: Optional[str] = Field(default=None, max_length=50)
    author: Optional[str] = Field(default=None, max_length=255)
    tags: Optional[List[str]] = None

    @validator("slug")
    def validate_slug(cls, v):
        if v is not None and not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError("Slug must contain only lowercase letters, numbers, and hyphens")
        if v and (v.startswith("-") or v.endswith("-")):
            raise ValueError("Slug cannot start or end with hyphen")
        if v and "--" in v:
            raise ValueError("Slug cannot contain consecutive hyphens")
        return v


class AgentResponse(AgentBase):
    id: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class AgentListResponse(BaseModel):
    items: List[AgentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_operator),
):
    service = AgentService(db)
    try:
        agent = await service.create(
            name=agent_data.name,
            slug=agent_data.slug,
            content=agent_data.content,
            description=agent_data.description,
            version=agent_data.version,
            author=agent_data.author,
            tags=agent_data.tags,
        )
        return agent.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=AgentListResponse)
async def list_agents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_operator),
):
    service = AgentService(db)
    agents, total = await service.list(page=page, page_size=page_size, search=search, tag=tag)
    total_pages = (total + page_size - 1) // page_size
    return {
        "items": [agent.to_dict() for agent in agents],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_operator),
):
    service = AgentService(db)
    agent = await service.get_by_id(agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent.to_dict()


@router.get("/slug/{slug}", response_model=AgentResponse)
async def get_agent_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_operator),
):
    service = AgentService(db)
    agent = await service.get_by_slug(slug)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent.to_dict()


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_operator),
):
    service = AgentService(db)
    try:
        agent = await service.update(
            agent_id=agent_id,
            name=agent_data.name,
            slug=agent_data.slug,
            content=agent_data.content,
            description=agent_data.description,
            version=agent_data.version,
            author=agent_data.author,
            tags=agent_data.tags,
        )
        if not agent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
        return agent.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_operator),
):
    service = AgentService(db)
    deleted = await service.delete(agent_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

