from web3 import Web3
from core.abi.abi import SCROLL_MAIN_ABI
from core.client import WebClient
from loguru import logger
import asyncio, random

from core.request import global_request
from core.utils import WALLET_PROXIES, intToDecimal
from user_data.config import FEE_MULTIPLIER, USE_PROXY
from user_data.config import MINT_RANDOM_NICKNAME

class ScrollCanvas(WebClient):
    def __init__(self, id:int, key: str):
        super().__init__(id, key, 'scroll')


    async def getSignature(self):
        proxy = None
        if USE_PROXY == True:
            proxy = WALLET_PROXIES[self.key]
        url = f"https://canvas.scroll.cat/code/NTAQN/sig/{self.address}"
        headers = {
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9,uk;q=0.8',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
        }
        status_code, response = await global_request(wallet=self.address, method='get', url=url, headers=headers, proxy=proxy)
        return status_code, response
    
    async def mintUserName(self):
        try:
            mint_contract = self.web3.eth.contract(address=Web3.to_checksum_address('0xb23af8707c442f59bdfc368612bd8dbcca8a7a5a'), abi=SCROLL_MAIN_ABI)
            nickname = str(random.choice(MINT_RANDOM_NICKNAME))
            code,response = await self.getSignature()
            bytes_for = response['signature']
            contract_txn = await mint_contract.functions.mint(nickname, bytes_for).build_transaction({
                'nonce': await self.web3.eth.get_transaction_count(self.address),
                'from': self.address,
                'gas': 0,
                'maxFeePerGas': int(await self.web3.eth.gas_price*FEE_MULTIPLIER),
                'maxPriorityFeePerGas': await self.web3.eth.max_priority_fee,
                'chainId': self.chain_id,
                'value': intToDecimal(0.0005, 18),
            })
            gas = await self.web3.eth.estimate_gas(contract_txn)
            contract_txn['gas'] = int(gas*1.05)

            status, tx_link = await self.send_tx(contract_txn)
            if status == 1:
                logger.success(f"{self.address} | nickname claim nft | {tx_link}")
                await asyncio.sleep(5)
                return True
            else:
                logger.error(f"claim nft | tx is failed | {tx_link}")
                return False
        except Exception as error:
            logger.error(error)
            return False
        
    async def mintFromJSON(self, json):
        try:
            data = json['tx']['data']
            to = Web3().to_checksum_address(json['tx']['to'])
            contract_txn = {
                'data': data,
                'nonce': await self.web3.eth.get_transaction_count(self.address),
                'from': self.address,
                'gasPrice': await self.web3.eth.gas_price,
                'gas': 0,
                'chainId': self.chain_id,
                'to': to,
                'value': 0,
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
        

        
# 0xC47300428b6AD2c7D03BB76D05A176058b47E6B0
# 0x39fb5E85C7713657c2D9E869E974FF1e0B06F20C
# https://canvas.scroll.cat/badge/check?badge=0x3dacAd961e5e2de850F5E027c70b56b5Afa5DfeD&recipient=0x387c6e7fe88042966aCF9EAc1852E0F101E4b37D



