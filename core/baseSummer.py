from web3 import Web3
from core.abi.abi import SCROLL_MAIN_ABI
from core.client import WebClient
from loguru import logger
import asyncio, random
from core.request import global_request
from core.utils import WALLET_PROXIES, intToDecimal
from user_data.config import USE_PROXY
import json

class BaseSummer(WebClient):
    def __init__(self, id:int, key: str):
        super().__init__(id, key, 'base')

    async def request_data(self):
        proxy = None
        if USE_PROXY == True:
            proxy = WALLET_PROXIES[self.key]
            # proxy = {
            #     "http": f"{WALLET_PROXIES[self.key]}",
            #     "https": f"{WALLET_PROXIES[self.key]}"
            # }
        url = "https://api.wallet.coinbase.com/rpc/v3/creators/mintToken"
        headers = {
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9,uk;q=0.8',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
        }
        payload = json.dumps({
            "bypassSimulation": True,
            "mintAddress": "0xe5CE018E2aF6109be9FDA3a7dc36DB3Eb2765f93",
            "network": "networks/base-mainnet",
            "quantity": "1",
            "takerAddress": f'{self.address}'
        })
        status_code, response = await global_request(wallet=self.address, method='post', url=url, headers=headers, data=payload, proxy=proxy)
        return status_code, response

    async def mint_nft(self):
        try:

            status_code, response = await self.request_data()

            data = response['callData']['data']
            to = Web3().to_checksum_address(response['callData']['to'])
            value = int(response['callData']['value'], 16)
            contract_txn = {
                'data': data,
                'nonce': await self.web3.eth.get_transaction_count(self.address),
                'from': Web3().to_checksum_address(self.address),
                'gasPrice': await self.web3.eth.gas_price,
                'gas': 0,
                'chainId': self.chain_id,
                'to': to,
                'value': value
            }
            gas = await self.web3.eth.estimate_gas(contract_txn)
            contract_txn['gas'] = int(gas*1.05)
            status, tx_link = await self.send_tx(contract_txn)
            if status == 1:
                logger.success(f"{self.address} | claim nft | {tx_link}")
                await asyncio.sleep(5)
                return True
            else:
                logger.error(f"claim nft | tx is failed | {tx_link}")
                return False
        except Exception as error:
            logger.error(error)
            return False