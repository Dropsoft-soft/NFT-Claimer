import asyncio
import sys, time, random
from core.client import WebClient
from core.utils import WALLETS
from core.__init__ import *
from concurrent.futures import ThreadPoolExecutor
from loguru import logger
from user_data.config import DELAY_FROM, DELAY_TO
from core.modules import *
import questionary
from questionary import Choice

def get_wallets():
    wallets = [
        {
            "id": _id,
            "key": key,
        } for _id, key in enumerate(WALLETS, start=1)
    ]
    return wallets

def run_module(module, account_id, key):
    try:
        asyncio.run(module(account_id, key))
    except Exception as e:
        logger.error(e)

def _async_run_module(module, account_id, key):
    asyncio.run(run_module(account_id, key))

def get_module():
    result = questionary.select(
        "Select a method to get started",
        choices=[
            Choice("1) Mint linea layer3 NFT", linea_layer3_nft),
            Choice("2) Mint Base summer NFT", base_summer_nft),
            Choice("3) Mint scroll NFT", scroll_mint_username),
            Choice("99) Exit", "exit"),
        ],
        qmark="⚙️ ",
        pointer="✅ "
    ).ask()
    if result == "exit":
        print("\nSubscribe – https://t.me/@web3sftwr\n")
        print("Donate me: 0xDEEF1cAb244Bb0f3A8f16C497B4380C0E8328FE3")
        sys.exit()
    return result

if __name__ == "__main__":
    print("Subscribe https://t.me/@web3sftwr\n")

    module = get_module()
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    wallets = get_wallets()

    for account in wallets:
        run_module(module, account.get("id"), account.get("key"))
        if account != wallets[-1]:
            time.sleep(random.randint(DELAY_FROM, DELAY_TO))