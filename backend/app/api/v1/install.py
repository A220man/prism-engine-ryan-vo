from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, TokenData, require_operator
from app.models.agent import Agent
from app.services.agent_service import AgentService
from app.services import installer as installer_module
from app.services.installer import InstallTarget, AgentInstaller

router = APIRouter(prefix="/install", tags=["install"])


class InstallRequest(BaseModel):
    agent_id: Optional[str] = Field(default=None, description="Agent ID to install")
    agent_slug: Optional[str] = Field(default=None, description="Agent slug to install")
    targets: List[InstallTarget] = Field(..., description="List of installation targets")
    identifier: str = Field(default="", description="Optional identifier for Qwen/ZCode targets")
    overwrite: bool = Field(default=False, description="Overwrite existing files")

    def model_post_init(self, __context):
        if not self.agent_id and not self.agent_slug:
            raise ValueError("Either agent_id or agent_slug must be provided")


class InstallResponse(BaseModel):
    overall_success: bool
    results: List[dict]


@router.post("", response_model=InstallResponse)
async def install_agent(
    request: InstallRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
    _: None = Depends(require_operator),
):
    """Install an agent to one or more targets."""
    service = AgentService(db)
    installer = installer_module.get_installer()

    # Resolve agent
    agent = None
    if request.agent_id:
        agent = await service.get_by_id(request.agent_id)
    elif request.agent_slug:
        agent = await service.get_by_slug(request.agent_slug)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    # Validate slug for Qwen/ZCode targets
    needs_slug_validation = any(
        t in (InstallTarget.QWEN, InstallTarget.ZCODE) for t in request.targets
    )
    if needs_slug_validation and not AgentInstaller.validate_slug(agent.slug):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid slug for Qwen/ZCode targets: {agent.slug}",
        )

    # Perform installation
    install_results = await installer.install(
        agent_content=agent.content,
        agent_name=agent.name,
        agent_slug=agent.slug,
        targets=request.targets,
        identifier=request.identifier,
        overwrite=request.overwrite,
    )

    return InstallResponse(
        overall_success=install_results.overall_success,
        results=[
            {
                "target": r.target.value,
                "success": r.success,
                "path": r.path,
                "error": r.error,
            }
            for r in install_results.results
        ],
    )


@router.get("/targets", response_model=List[str])
async def list_targets(
    current_user: TokenData = Depends(get_current_user),
    _: None = Depends(require_operator),
):
    """List available installation targets."""
    return [t.value for t in InstallTarget]

