from web3 import Web3
from core.abi.abi import SCROLL_MAIN_ABI
from core.client import WebClient
from loguru import logger
import asyncio, random

from core.request import global_request
from core.utils import WALLET_PROXIES, intToDecimal
from user_data.config import FEE_MULTIPLIER, USE_PROXY
from user_data.config import MINT_RANDOM_NICKNAME

class BeraTestnet(WebClient):
    def __init__(self, id:int, key: str):
        super().__init__(id, key, 'bera_testnet')

    async def mint_nft(self):
        try:
            contract_txn = {
                'nonce': await self.web3.eth.get_transaction_count(self.address),
                'from': Web3().to_checksum_address(self.address),
                'gas': 0,
                'gasPrice': await self.web3.eth.gas_price,
                'to': Web3().to_checksum_address('0x46B4b78d1Cd660819C934e5456363A359fde43f4'),
                'chainId': self.chain_id,
                'value': 250000000000000000,
                'data': "0xb3ab66b00000000000000000000000000000000000000000000000000000000000000001",
            }
            gas = await self.web3.eth.estimate_gas(contract_txn)
            contract_txn['gas'] = int(gas*1.05)

            status, tx_link = await self.send_tx(contract_txn)
            if status == 1:
                logger.success(f"[{self.id}] {self.address} | claimed nft | {tx_link}")
                await asyncio.sleep(5)
                return True
            else:
                logger.error(f"[{self.id}] {self.address} | tx is failed | {tx_link}")
                return False
        except Exception as error:
            logger.error(error)
            return False
#     {
#   "chainId": 80084,
#   "data": "0xb3ab66b00000000000000000000000000000000000000000000000000000000000000001",
#   "from": "0x2EDEc0Da3385611C59235fc711faFac5298Cc0CA",
#   "gas": "0x41fbb",
#   "gasPrice": "0x124f8d",
#   "nonce": "0x0",
#   "to": "0x46B4b78d1Cd660819C934e5456363A359fde43f4",
#   "value": "0x3782dace9d90000"
# }


