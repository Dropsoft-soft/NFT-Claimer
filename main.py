import asyncio
import sys, time, random
from core.client import WebClient
from core.utils import WALLETS
from core.__init__ import *
from concurrent.futures import ThreadPoolExecutor
from loguru import logger
from user_data.config import DELAY_FROM, DELAY_TO
from core.modules import *

CHAIN = 'linea'

def get_wallets():
    wallets = [
        {
            "id": _id,
            "key": key,
        } for _id, key in enumerate(WALLETS, start=1)
    ]
    return wallets

async def run_module(module, account_id, key):
    try:
        asyncio.run(module(account_id, key))
    except Exception as e:
        logger.error(e)

def _async_run_module(module, account_id, key):
    asyncio.run(run_module(account_id, key))

def get_module(string):
    if string == 'linea_layer3_nft':
        return linea_layer3_nft
    else:
        return

if __name__ == "__main__":
    MODULE = int(input('''
MODULE:
1. Linea Layer3 mint NFT
2. Scroll carnival mint NFT               
''')
)   
    active_module = None
    if MODULE == 1:
        active_module = linea_layer3_nft
    if MODULE == 2: 
        active_module 
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    wallets = get_wallets()

    with ThreadPoolExecutor(max_workers=1) as executor:
        for _, account in enumerate(wallets, start=1):
            executor.submit(
                _async_run_module,
                active_module,
                account.get("id"),
                account.get("key")
            )
            time.sleep(random.randint(DELAY_FROM, DELAY_TO))
