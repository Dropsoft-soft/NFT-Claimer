
from core.arbitrum import Arbitrum
from core.baseSummer import BaseSummer
from core.beranft import BeraTestnet
from core.scroll import ScrollCanvas
from core.client import WebClient
from user_data.config import MINT_RANDOM_SUMMER_BASE_NFT
import random
from loguru import logger

async def linea_layer3_nft(account_id, key):
    web3 = WebClient(
        account_id, key, 'linea'
    )
    await web3.claimNFT()

async def scroll_mint_username(account_id, key):
    web3 = ScrollCanvas(
        account_id, key
    )
    await web3.mintUserName()

async def scroll_mint_badges(account_id, key):
    web3 = ScrollCanvas(
        account_id, key
    )
    await web3.mint_all_available_badge()

async def scroll_omnihub_nft(account_id, key):
    web3 = ScrollCanvas(
        account_id, key
    )
    await web3.mins_omihub_nft()

async def scroll_register_delegatee(account_id, key):
    web3 = ScrollCanvas(
        account_id, key
    )
    await web3.create_delegatee()

async def scroll_mint_drop(account_id, key):
    web3 = ScrollCanvas(
        account_id, key
    )
    await web3.get_drop()

async def welcome_to_base_summer_nft(account_id, key):
    web3 = BaseSummer(
        account_id, key
    )
    await web3.mint_welcome_to_new_base()

async def base_summer_nft(account_id, key):
    web3 = BaseSummer(
        account_id, key
    )

    if MINT_RANDOM_SUMMER_BASE_NFT:
        array_nft = [web3.mint_nft, web3.mint_sanfrancisco_nft, web3.mint_birthday_toshi_nft, web3.mint_summer_chibling_nft, web3.mint_eth_cant_be_stopped_nft, web3.mint_midnight_diner_pass_nft, web3.mint_doodlestv_pass_nft, web3.mint_onchain_summer_board_nft]
        selected = random.choice(list(array_nft))
        logger.info(f'Mint random nft: {selected}')
        await selected()
    else:
        await web3.mint_nft()
        await web3.mint_sanfrancisco_nft()
        await web3.mint_birthday_toshi_nft()
        await web3.mint_summer_chibling_nft()
        await web3.mint_eth_cant_be_stopped_nft()
        await web3.mint_midnight_diner_pass_nft()
        await web3.mint_doodlestv_pass_nft()
        await web3.mint_onchain_summer_board_nft()

async def bera_nft(account_id, key):
    web3 = BeraTestnet(
        account_id, key
    )
    await web3.mint_nft()
    
async def claim_odos_drop(account_id, key):
    web3 = BaseSummer(account_id, key)
    await web3.claimDrop()

async def claim_orbiter_drop(account_id, key):
    web3 = Arbitrum(account_id, key)
    await web3.claim_drop()