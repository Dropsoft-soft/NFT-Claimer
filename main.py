import asyncio
import sys, time, random
from core.client import WebClient
from core.utils import WALLETS, sleeping
from core.__init__ import *
from concurrent.futures import ThreadPoolExecutor
from loguru import logger
from user_data.config import DELAY_FROM, DELAY_TO, RANDOM_WALLETS
from core.modules import *
import questionary
from questionary import Choice
from datetime import datetime
date_now = datetime.now().strftime("%d-%m-%Y")
format = '<white>{time:HH:mm:ss}</white> | <bold><level>{level: <7}</level></bold> | <level>{message}</level>'
logger.remove()
logger.add(sys.stderr, format=format)

def get_wallets():
    if RANDOM_WALLETS == True: random.shuffle(WALLETS)
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
            Choice("3) Mint Scroll Nickname NFT", scroll_mint_username),
            Choice("4) Bera NFT", bera_nft),
            Choice("5) Mint Scroll claim badges", scroll_mint_badges),
            Choice("6) Mint Welcome to New Base NFT", welcome_to_base_summer_nft),
            Choice("7) Mint omnihub Scroll OG NFT",  scroll_omnihub_nft),
            Choice("8) Scroll Register delegatee", scroll_register_delegatee),
            Choice("99) Exit", "exit"),
        ],
        qmark="⚙️ ",
        pointer="✅ "
    ).ask()
    if result == "exit":
        print("\nSubscribe – https://t.me/web3sftwr\n")
        sys.exit()
    return result

if __name__ == "__main__":
    print("Subscribe https://t.me/web3sftwr\n")

    module = get_module()
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    wallets = get_wallets()
    for account in wallets:
        try:
            run_module(module, account.get("id"), account.get("key"))
            if account != wallets[-1]:
                random_time = random.randint(DELAY_FROM,DELAY_TO)
                logger.info(f'Sleep: {random_time} s')
                time.sleep(random_time)
        except Exception as error:
            logger.error(f'Error: {error}')
