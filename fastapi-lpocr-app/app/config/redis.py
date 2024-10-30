
import redis.asyncio as aioredis
from app.config.settings import get_settings

settings = get_settings()
JTI_EXPIRY = 3600

token_blocklist = aioredis.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
)
async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(name=jti, value="", ex=JTI_EXPIRY)


async def token_in_blocklist(jti: str) -> bool:
    jti = await token_blocklist.get(jti)

    return jti is not None