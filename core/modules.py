
from core.client import WebClient

async def linea_layer3_nft(account_id, key):
    web3 = WebClient(
        account_id, key, 'linea'
    )
    await web3.claimNFT()