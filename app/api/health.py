from typing import Annotated

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.database import get_engine
from app.core.redis import get_redis
from app.schemas.health import HealthResponse

router = APIRouter()


async def _check_database(engine: AsyncEngine) -> str:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return "ok"
    except Exception:
        return "down"


async def _check_redis(redis_client: Redis) -> str:
    try:
        await redis_client.ping()
        return "ok"
    except Exception:
        return "down"


@router.get("/health", response_model=HealthResponse)
async def health_check(
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    redis_client: Annotated[Redis, Depends(get_redis)],
) -> HealthResponse:
    components = {
        "app": "ok",
        "database": await _check_database(engine),
        "redis": await _check_redis(redis_client),
    }
    status = "ok" if all(value == "ok" for value in components.values()) else "degraded"
    return HealthResponse(status=status, components=components)
