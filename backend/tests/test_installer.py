import os
os.environ["DEMO_MODE"] = "true"

import pytest
import tempfile
from pathlib import Path
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.models.agent import Agent
from app.services.installer import AgentInstaller, InstallTarget, InstallResults


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()



async def init_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def create_token(roles: list[str]) -> str:
    return create_access_token({"sub": "test-user", "email": "test@example.com", "roles": roles})


class TestInstallerService:
    """Test the AgentInstaller service class."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        import asyncio
        asyncio.run(init_test_db())
        yield
        asyncio.run(drop_test_db())

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def installer(self, temp_dir):
        return AgentInstaller(base_dir=temp_dir)

    @pytest.mark.asyncio
    async def test_sanitize_identifier(self):
        assert AgentInstaller.sanitize_identifier("My Agent") == "my_agent"
        assert AgentInstaller.sanitize_identifier("Test@Agent#1") == "test_agent_1"
        assert AgentInstaller.sanitize_identifier("  spaces  ") == "spaces"
        assert AgentInstaller.sanitize_identifier("") == "agent"
        assert AgentInstaller.sanitize_identifier("___") == "agent"
        assert AgentInstaller.sanitize_identifier("already_clean") == "already_clean"

    @pytest.mark.asyncio
    async def test_validate_slug(self):
        assert AgentInstaller.validate_slug("valid-slug") is True
        assert AgentInstaller.validate_slug("valid_slug") is True
        assert AgentInstaller.validate_slug("valid123") is True
        assert AgentInstaller.validate_slug("") is False
        assert AgentInstaller.validate_slug("  ") is False
        assert AgentInstaller.validate_slug("Invalid Slug") is False
        assert AgentInstaller.validate_slug("UPPERCASE") is False

    @pytest.mark.asyncio
    async def test_get_target_path_claude_code(self, installer):
        path = installer.get_target_path(InstallTarget.CLAUDE_CODE)
        assert path.name == "CLAUDE.md"

    @pytest.mark.asyncio
    async def test_get_target_path_cursor(self, installer):
        path = installer.get_target_path(InstallTarget.CURSOR)
        assert path.name == "agent.mdc"
        assert ".cursor/rules" in str(path)

    @pytest.mark.asyncio
    async def test_get_target_path_qwen_with_identifier(self, installer):
        path = installer.get_target_path(InstallTarget.QWEN, identifier="my-agent")
        assert "my_agent" in path.name
        assert path.name == "agent.my_agent.md"

    @pytest.mark.asyncio
    async def test_get_target_path_zcode_with_identifier(self, installer):
        path = installer.get_target_path(InstallTarget.ZCODE, identifier="Test Agent")
        assert "test_agent" in path.name
        assert path.name == "agent.test_agent.md"

    @pytest.mark.asyncio
    async def test_install_single_target(self, installer):
        result = await installer.install_to_target(
            target=InstallTarget.CLAUDE_CODE,
            agent_content="# Test Agent\n\nContent here",
            agent_name="Test Agent",
            agent_slug="test-agent",
        )
        assert result.success is True
        assert result.path is not None
        assert Path(result.path).exists()
        content = Path(result.path).read_text()
        assert "Test Agent (test-agent)" in content
        assert "Content here" in content

    @pytest.mark.asyncio
    async def test_install_prevents_overwrite_by_default(self, installer):
        await installer.install_to_target(
            target=InstallTarget.CLAUDE_CODE,
            agent_content="First",
            agent_name="Test",
            agent_slug="test",
        )

        result = await installer.install_to_target(
            target=InstallTarget.CLAUDE_CODE,
            agent_content="Second",
            agent_name="Test",
            agent_slug="test",
        )
        assert result.success is False
        assert "already exists" in result.error

    @pytest.mark.asyncio
    async def test_install_allows_overwrite(self, installer):
        await installer.install_to_target(
            target=InstallTarget.CLAUDE_CODE,
            agent_content="First",
            agent_name="Test",
            agent_slug="test",
        )

        result = await installer.install_to_target(
            target=InstallTarget.CLAUDE_CODE,
            agent_content="Second",
            agent_name="Test",
            agent_slug="test",
            overwrite=True,
        )
        assert result.success is True
        content = Path(result.path).read_text()
        assert "Second" in content

    @pytest.mark.asyncio
    async def test_install_multiple_targets_parallel(self, installer):
        targets = [
            InstallTarget.CLAUDE_CODE,
            InstallTarget.CURSOR,
            InstallTarget.AIDER,
        ]
        results = await installer.install(
            agent_content="Multi-target content",
            agent_name="Multi Agent",
            agent_slug="multi-agent",
            targets=targets,
        )
        assert results.overall_success is True
        assert len(results.results) == 3
        assert all(r.success for r in results.results)
        assert len(results.successful_targets) == 3

    @pytest.mark.asyncio
    async def test_install_qwen_zcode_requires_valid_slug(self, installer):
        targets = [InstallTarget.QWEN, InstallTarget.ZCODE]
        results = await installer.install(
            agent_content="Content",
            agent_name="Bad Slug",
            agent_slug="Bad Slug!",
            targets=targets,
        )
        assert all(r.success for r in results.results)
        for r in results.results:
            assert r.path is not None
            assert Path(r.path).exists()


class TestInstallEndpoints:
    """Test the install API endpoints."""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        import asyncio
        asyncio.run(init_test_db())
        yield
        asyncio.run(drop_test_db())

    @pytest.fixture
    def client(self):
        app.dependency_overrides[get_db] = override_get_db
        transport = ASGITransport(app=app)
        ac = AsyncClient(transport=transport, base_url="http://test")
        yield ac
        app.dependency_overrides.clear()

    @pytest.fixture
    def operator_headers(self):
        token = create_token(["operator"])
        return {"Authorization": f"Bearer {token}"}

    async def _create_test_agent(self, client, operator_headers):
        """Helper to create a test agent."""
        response = await client.post(
            "/api/v1/agents",
            json={
                "name": "Test Agent",
                "slug": "test-agent",
                "content": "# Test Agent\n\nThis is test content.",
                "description": "A test agent",
            },
            headers=operator_headers,
        )
        return response.json()

    @pytest.mark.asyncio
    async def test_list_targets(self, client, operator_headers):
        response = await client.get("/api/v1/install/targets", headers=operator_headers)
        assert response.status_code == 200
        data = response.json()
        assert "claude_code" in data
        assert "cursor" in data
        assert "aider" in data
        assert "qwen" in data
        assert "zcode" in data

    @pytest.mark.asyncio
    async def test_install_agent_by_id(self, client, operator_headers, tmp_path):
        test_agent = await self._create_test_agent(client, operator_headers)

        from app.services.installer import get_installer
        import app.services.installer as installer_module
        test_installer = AgentInstaller(base_dir=tmp_path)
        original_get_installer = get_installer
        installer_module.get_installer = lambda base_dir=None: test_installer

        try:
            response = await client.post(
                "/api/v1/install",
                json={
                    "agent_id": test_agent["id"],
                    "targets": ["claude_code", "cursor"],
                },
                headers=operator_headers,
            )
            assert response.status_code == 200
            data = response.json()
            assert data["overall_success"] is True
            assert len(data["results"]) == 2
            assert all(r["success"] for r in data["results"])
        finally:
            installer_module.get_installer = original_get_installer

    @pytest.mark.asyncio
    async def test_install_agent_by_slug(self, client, operator_headers, tmp_path):
        await self._create_test_agent(client, operator_headers)

        from app.services.installer import get_installer
        import app.services.installer as installer_module
        test_installer = AgentInstaller(base_dir=tmp_path)
        original_get_installer = get_installer
        installer_module.get_installer = lambda base_dir=None: test_installer

        try:
            response = await client.post(
                "/api/v1/install",
                json={
                    "agent_slug": "test-agent",
                    "targets": ["aider"],
                },
                headers=operator_headers,
            )
            assert response.status_code == 200
            data = response.json()
            assert data["overall_success"] is True
            assert len(data["results"]) == 1
        finally:
            installer_module.get_installer = original_get_installer

    @pytest.mark.asyncio
    async def test_install_agent_not_found(self, client, operator_headers):
        response = await client.post(
            "/api/v1/install",
            json={
                "agent_id": "non-existent-id",
                "targets": ["claude_code"],
            },
            headers=operator_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_install_requires_agent_id_or_slug(self, client, operator_headers):
        response = await client.post(
            "/api/v1/install",
            json={
                "targets": ["claude_code"],
            },
            headers=operator_headers,
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_install_with_identifier(self, client, operator_headers, tmp_path):
        await self._create_test_agent(client, operator_headers)

        from app.services.installer import get_installer
        import app.services.installer as installer_module
        test_installer = AgentInstaller(base_dir=tmp_path)
        original_get_installer = get_installer
        installer_module.get_installer = lambda base_dir=None: test_installer

        try:
            response = await client.post(
                "/api/v1/install",
                json={
                    "agent_slug": "test-agent",
                    "targets": ["qwen", "zcode"],
                    "identifier": "custom-id",
                },
                headers=operator_headers,
            )
            assert response.status_code == 200
            data = response.json()
            assert data["overall_success"] is True
            for r in data["results"]:
                assert "custom_id" in r["path"]
        finally:
            installer_module.get_installer = original_get_installer

    @pytest.mark.asyncio
    async def test_install_with_overwrite(self, client, operator_headers, tmp_path):
        await self._create_test_agent(client, operator_headers)

        from app.services.installer import get_installer
        import app.services.installer as installer_module
        test_installer = AgentInstaller(base_dir=tmp_path)
        original_get_installer = get_installer
        installer_module.get_installer = lambda base_dir=None: test_installer

        try:
            await client.post(
                "/api/v1/install",
                json={
                    "agent_slug": "test-agent",
                    "targets": ["claude_code"],
                },
                headers=operator_headers,
            )

            response = await client.post(
                "/api/v1/install",
                json={
                    "agent_slug": "test-agent",
                    "targets": ["claude_code"],
                    "overwrite": True,
                },
                headers=operator_headers,
            )
            assert response.status_code == 200
            data = response.json()
            assert data["overall_success"] is True
        finally:
            installer_module.get_installer = original_get_installer
