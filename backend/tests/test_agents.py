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
        yield session


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
