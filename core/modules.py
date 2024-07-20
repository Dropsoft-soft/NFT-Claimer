
from core.scroll import ScrollCanvas
from core.client import WebClient

async def linea_layer3_nft(account_id, key):
    web3 = WebClient(
        account_id, key, 'linea'
    )
    await web3.claimNFT()

async def scroll_mint_username(account_id, key):
    web3 = ScrollCanvas(
        account_id, key, 'scroll'
    )
    await web3.mintUserName()