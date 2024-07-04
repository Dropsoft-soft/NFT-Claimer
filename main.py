import asyncio
import sys, time, random
from core.client import WebClient
from core.request import global_request
from core.utils import WALLET_PROXIES, WALLETS
from core.__init__ import *
from concurrent.futures import ThreadPoolExecutor
from loguru import logger
from user_data.config import DELAY_FROM, DELAY_TO, USE_PROXY, USE_TRANSFER

CHAIN = 'linea'

def get_wallets():
    wallets = [
        {
            "id": _id,
            "key": key,
        } for _id, key in enumerate(WALLETS, start=1)
    ]
    return wallets

async def run_module(account_id, key):
    try:
        web3 = WebClient(
            account_id, key, CHAIN
        )
        proxy = None
        await web3.claimDrop()
    except Exception as e:
        logger.error(e)

def _async_run_module(module, account_id, key):
    asyncio.run(run_module(account_id, key))

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    wallets = get_wallets()

    with ThreadPoolExecutor(max_workers=1) as executor:
        for _, account in enumerate(wallets, start=1):
            executor.submit(
                _async_run_module,
                WebClient,
                account.get("id"),
                account.get("key")
            )
            time.sleep(random.randint(DELAY_FROM, DELAY_TO))
