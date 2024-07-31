
from core.baseSummer import BaseSummer
from core.beranft import BeraTestnet
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

async def base_summer_nft(account_id, key):
    web3 = BaseSummer(
        account_id, key
    )
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
    