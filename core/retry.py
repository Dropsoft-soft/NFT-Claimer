from loguru import logger

from user_data.config import RETRY
from .utils import sleep


def retry(func):
    async def wrapper(*args, **kwargs):
        retries = 0
        while retries < RETRY:
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"Error | {e}")
                await sleep(10, 30)
                retries += 1

    return wrapper