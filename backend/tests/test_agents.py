import os
os.environ["DEMO_MODE"] = "true"

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.security import create_access_token, TokenData
from app.models.agent import Agent

print("MODULE LEVEL: Tables in metadata:", list(Base.metadata.tables.keys()))

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


def create_token(roles: list[str]) -> str:
    return create_access_token({"sub": "test-user", "email": "test@example.com", "roles": roles})


class TestAgentEndpoints:
    @pytest.fixture(autouse=True)
    def setup_db(self):
        print("FIXTURE: Before create_all (sync)")
        import asyncio
        async def create_tables():
            async with test_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            async with test_engine.begin() as conn:
                from sqlalchemy import text
                result = await conn.execute(text('SELECT name FROM sqlite_master WHERE type="table"'))
                print("FIXTURE: Tables in DB:", result.fetchall())
        asyncio.run(create_tables())
        print("FIXTURE: After create_all")
        yield
        print("FIXTURE: Teardown")
        async def drop_tables():
            async with test_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
        asyncio.run(drop_tables())

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

    @pytest.mark.asyncio
    async def test_create_agent(self, client, operator_headers):
        print("TEST: Starting test_create_agent")
        response = await client.post(
            "/api/v1/agents",
            json={"name": "Test Agent", "slug": "test-agent", "content": "Agent content"},
            headers=operator_headers,
        )
        print("TEST: Response status:", response.status_code)
        print("TEST: Response:", response.json())
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Agent"
        assert data["slug"] == "test-agent"
        assert data["content"] == "Agent content"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_agent_duplicate_slug(self, client, operator_headers):
        await client.post(
            "/api/v1/agents",
            json={"name": "Test Agent", "slug": "test-agent", "content": "Agent content"},
            headers=operator_headers,
        )
        response = await client.post(
            "/api/v1/agents",
            json={"name": "Test Agent 2", "slug": "test-agent", "content": "Agent content 2"},
            headers=operator_headers,
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_list_agents(self, client, operator_headers):
        await client.post(
            "/api/v1/agents",
            json={"name": "Agent 1", "slug": "agent-1", "content": "Content 1"},
            headers=operator_headers,
        )
        await client.post(
            "/api/v1/agents",
            json={"name": "Agent 2", "slug": "agent-2", "content": "Content 2"},
            headers=operator_headers,
        )
        response = await client.get("/api/v1/agents", headers=operator_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    @pytest.mark.asyncio
    async def test_get_agent(self, client, operator_headers):
        create_resp = await client.post(
            "/api/v1/agents",
            json={"name": "Test Agent", "slug": "test-agent", "content": "Agent content"},
            headers=operator_headers,
        )
        agent_id = create_resp.json()["id"]
        response = await client.get(f"/api/v1/agents/{agent_id}", headers=operator_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Agent"
        assert data["slug"] == "test-agent"

    @pytest.mark.asyncio
    async def test_get_agent_not_found(self, client, operator_headers):
        response = await client.get("/api/v1/agents/non-existent-id", headers=operator_headers)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_agent(self, client, operator_headers):
        create_resp = await client.post(
            "/api/v1/agents",
            json={"name": "Test Agent", "slug": "test-agent", "content": "Agent content"},
            headers=operator_headers,
        )
        agent_id = create_resp.json()["id"]
        response = await client.patch(
            f"/api/v1/agents/{agent_id}",
            json={"name": "Updated Agent", "content": "Updated content"},
            headers=operator_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Agent"
        assert data["content"] == "Updated content"
        assert data["slug"] == "test-agent"

    @pytest.mark.asyncio
    async def test_delete_agent(self, client, operator_headers):
        create_resp = await client.post(
            "/api/v1/agents",
            json={"name": "Test Agent", "slug": "test-agent", "content": "Agent content"},
            headers=operator_headers,
        )
        agent_id = create_resp.json()["id"]
        response = await client.delete(f"/api/v1/agents/{agent_id}", headers=operator_headers)
        assert response.status_code == 204
        get_resp = await client.get(f"/api/v1/agents/{agent_id}", headers=operator_headers)
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_agent_by_slug(self, client, operator_headers):
        await client.post(
            "/api/v1/agents",
            json={"name": "Test Agent", "slug": "test-agent", "content": "Agent content"},
            headers=operator_headers,
        )
        response = await client.get("/api/v1/agents/slug/test-agent", headers=operator_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "test-agent"

    @pytest.mark.asyncio
    async def test_list_agents_pagination(self, client, operator_headers):
        for i in range(5):
            await client.post(
                "/api/v1/agents",
                json={"name": f"Agent {i}", "slug": f"agent-{i}", "content": f"Content {i}"},
                headers=operator_headers,
            )
        response = await client.get("/api/v1/agents?page=1&page_size=2", headers=operator_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert data["total_pages"] == 3

    @pytest.mark.asyncio
    async def test_list_agents_filter(self, client, operator_headers):
        await client.post(
            "/api/v1/agents",
            json={"name": "Foo Agent", "slug": "foo-agent", "content": "Content", "tags": ["tag1"]},
            headers=operator_headers,
        )
        await client.post(
            "/api/v1/agents",
            json={"name": "Bar Agent", "slug": "bar-agent", "content": "Content", "tags": ["tag2"]},
            headers=operator_headers,
        )
        response = await client.get("/api/v1/agents?search=foo", headers=operator_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "Foo Agent"
