from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
import json
import re
from pathlib import Path


class InstallTarget(str, Enum):
    CLAUDE_CODE = "claude_code"
    CURSOR = "cursor"
    AIDER = "aider"
    QWEN = "qwen"
    ZCODE = "zcode"


@dataclass
class InstallResult:
    target: InstallTarget
    success: bool
    path: Optional[str] = None
    error: Optional[str] = None


@dataclass
class InstallResults:
    results: List[InstallResult]
    overall_success: bool

    @property
    def successful_targets(self) -> List[InstallTarget]:
        return [r.target for r in self.results if r.success]

    @property
    def failed_targets(self) -> List[InstallTarget]:
        return [r.target for r in self.results if not r.success]


class AgentInstaller:
    """Handles agent installation to multiple target IDEs/tools."""

    TARGET_CONFIGS = {
        InstallTarget.CLAUDE_CODE: {
            "file_name": "CLAUDE.md",
            "sanitize_identifier": False,
        },
        InstallTarget.CURSOR: {
            "file_name": ".cursor/rules/agent.mdc",
            "sanitize_identifier": False,
        },
        InstallTarget.AIDER: {
            "file_name": ".aider/agent.md",
            "sanitize_identifier": False,
        },
        InstallTarget.QWEN: {
            "file_name": ".qwen/agent.md",
            "sanitize_identifier": True,
        },
        InstallTarget.ZCODE: {
            "file_name": ".zcode/agent.md",
            "sanitize_identifier": True,
        },
    }

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path.cwd()

    @staticmethod
    def sanitize_identifier(identifier: str) -> str:
        """Sanitize identifier for Qwen/ZCode targets.
        Replaces non-alphanumeric characters with underscore, collapses multiple underscores.
        """
        if not identifier:
            return "agent"
        sanitized = re.sub(r"[^a-zA-Z0-9]+", "_", identifier)
        sanitized = re.sub(r"_+", "_", sanitized)
        sanitized = sanitized.strip("_")
        return sanitized.lower() or "agent"

    @staticmethod
    def validate_slug(slug: str) -> bool:
        """Validate slug is not empty and contains valid characters (lowercase, numbers, hyphen, underscore)."""
        if not slug or not slug.strip():
            return False
        return bool(re.match(r"^[a-z0-9_-]+$", slug))

    def get_target_path(self, target: InstallTarget, identifier: str = "") -> Path:
        """Get the target installation path for a given target and identifier."""
        config = self.TARGET_CONFIGS[target]
        file_name = config["file_name"]

        if config["sanitize_identifier"] and identifier:
            sanitized = self.sanitize_identifier(identifier)
            parts = file_name.rsplit(".", 1)
            if len(parts) == 2:
                file_name = f"{parts[0]}.{sanitized}.{parts[1]}"
            else:
                file_name = f"{file_name}.{sanitized}"

        return self.base_dir / file_name

    def generate_content(self, agent_content: str, target: InstallTarget, agent_name: str, agent_slug: str) -> str:
        """Generate target-specific content from agent content."""
        header = f"# {agent_name} ({agent_slug})\n\n"
        return header + agent_content

    async def install_to_target(
        self,
        target: InstallTarget,
        agent_content: str,
        agent_name: str,
        agent_slug: str,
        identifier: str = "",
        overwrite: bool = False,
    ) -> InstallResult:
        """Install agent to a single target."""
        try:
            target_path = self.get_target_path(target, identifier)

            if target_path.exists() and not overwrite:
                return InstallResult(
                    target=target,
                    success=False,
                    path=str(target_path),
                    error=f"File already exists: {target_path}",
                )

            target_path.parent.mkdir(parents=True, exist_ok=True)

            content = self.generate_content(agent_content, target, agent_name, agent_slug)

            target_path.write_text(content, encoding="utf-8")

            return InstallResult(
                target=target,
                success=True,
                path=str(target_path),
            )
        except Exception as e:
            return InstallResult(
                target=target,
                success=False,
                path=str(target_path) if "target_path" in locals() else None,
                error=str(e),
            )

    async def install(
        self,
        agent_content: str,
        agent_name: str,
        agent_slug: str,
        targets: List[InstallTarget],
        identifier: str = "",
        overwrite: bool = False,
    ) -> InstallResults:
        """Install agent to multiple targets in parallel."""
        import asyncio

        tasks = [
            self.install_to_target(
                target=target,
                agent_content=agent_content,
                agent_name=agent_name,
                agent_slug=agent_slug,
                identifier=identifier,
                overwrite=overwrite,
            )
            for target in targets
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        install_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                install_results.append(
                    InstallResult(
                        target=targets[i],
                        success=False,
                        error=str(result),
                    )
                )
            else:
                install_results.append(result)

        overall_success = all(r.success for r in install_results)
        return InstallResults(results=install_results, overall_success=overall_success)


def get_installer(base_dir: Optional[Path] = None) -> AgentInstaller:
    """Get installer instance."""
    return AgentInstaller(base_dir)

