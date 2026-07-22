import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_engine
from app.core.redis import get_redis
from app.main import app


class _FakeConnection:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        return False

    async def execute(self, *args, **kwargs):
        return None


class _FakeEngine:
    def __init__(self, healthy: bool):
        self.healthy = healthy

    def connect(self):
        if not self.healthy:
            raise ConnectionError("database unreachable")
        return _FakeConnection()


class _FakeRedis:
    def __init__(self, healthy: bool):
        self.healthy = healthy

    async def ping(self):
        if not self.healthy:
            raise ConnectionError("redis unreachable")
        return True


@pytest.fixture(autouse=True)
def _clear_dependency_overrides():
    yield
    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_health_ok_when_all_components_healthy():
    app.dependency_overrides[get_engine] = lambda: _FakeEngine(healthy=True)
    app.dependency_overrides[get_redis] = lambda: _FakeRedis(healthy=True)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body == {"status": "ok", "components": {"app": "ok", "database": "ok", "redis": "ok"}}


@pytest.mark.anyio
async def test_health_degraded_when_redis_down():
    app.dependency_overrides[get_engine] = lambda: _FakeEngine(healthy=True)
    app.dependency_overrides[get_redis] = lambda: _FakeRedis(healthy=False)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["components"]["redis"] == "down"
    assert body["components"]["database"] == "ok"


@pytest.mark.anyio
async def test_health_degraded_when_database_down():
    app.dependency_overrides[get_engine] = lambda: _FakeEngine(healthy=False)
    app.dependency_overrides[get_redis] = lambda: _FakeRedis(healthy=True)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["components"]["database"] == "down"
    assert body["components"]["redis"] == "ok"
