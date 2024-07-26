
from core.baseSummer import BaseSummer
from core.scroll import ScrollCanvas
from core.client import WebClient

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

async def scroll_base_summer_nft(account_id, key):
    web3 = BaseSummer(
        account_id, key
    )
    await web3.mint_nft()