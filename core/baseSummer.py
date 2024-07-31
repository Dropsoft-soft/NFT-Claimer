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

    async def request_data(self, mint_address):
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
            "mintAddress": f'{mint_address}',
            "network": "networks/base-mainnet",
            "quantity": "1",
            "takerAddress": f'{self.address}'
        })
        status_code, response = await global_request(wallet=self.address, method='post', url=url, headers=headers, data=payload, proxy=proxy)
        return status_code, response

    async def mint_nft(self):
        try:
            status_code, response = await self.request_data("0xe5CE018E2aF6109be9FDA3a7dc36DB3Eb2765f93")
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
                logger.success(f"[{self.id}] {self.address} | claim nft | {tx_link}")
                await asyncio.sleep(5)
                return True
            else:
                logger.error(f"[{self.id}] {self.address} | claim nft | tx is failed | {tx_link}")
                return False
        except Exception as error:
            logger.error(error)
            return False
        
    async def logic_for_mint(self, contract_to_mint, amount, data):
        try:
            to = Web3().to_checksum_address(contract_to_mint)
            contract_txn = {
                'data': data,
                'nonce': await self.web3.eth.get_transaction_count(self.address),
                'from': Web3().to_checksum_address(self.address),
                'gasPrice': await self.web3.eth.gas_price,
                'gas': 0,
                'chainId': self.chain_id,
                'to': to,
                'value': amount
            }
            gas = await self.web3.eth.estimate_gas(contract_txn)
            contract_txn['gas'] = int(gas*1.05)
            status, tx_link = await self.send_tx(contract_txn)
            if status == 1:
                logger.success(f"[{self.id}] {self.address} | claim nft | {tx_link}")
                await asyncio.sleep(30)
                return True
            else:
                logger.error(f"[{self.id}] {self.address} | claim nft | tx is failed | {tx_link}")
                return False
        except Exception as error:
            logger.error(error)
            return False
        
    async def mint_sanfrancisco_nft(self):
        contract = '0xf9aDb505EaadacCF170e48eE46Ee4d5623f777d7'
        value = intToDecimal(0.0008, 18)
        data = '0x574fed17000000000000000000000000' + self.address[2:] + '000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000000'
        await self.logic_for_mint(contract, value, data)
        
    async def mint_birthday_toshi_nft(self):
        contract = '0xE65dFa5C8B531544b5Ae4960AE0345456D87A47D'
        value = intToDecimal(0.0001, 18)
        data = '0x574fed17000000000000000000000000' + self.address[2:] + '000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000000'
        await self.logic_for_mint(contract, value, data)

    async def mint_summer_chibling_nft(self):
        contract = '0x13F294BF5e26843C33d0ae739eDb8d6B178740B0'
        value = intToDecimal(0.0001, 18)
        data = '0x574fed17000000000000000000000000' + self.address[2:] + '000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000000'
        await self.logic_for_mint(contract, value, data)

    async def mint_eth_cant_be_stopped_nft(self):
        contract = '0xb0FF351AD7b538452306d74fB7767EC019Fa10CF'
        value = intToDecimal(0.0001, 18)
        data = '0x574fed17000000000000000000000000' + self.address[2:] + '000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000000'
        await self.logic_for_mint(contract, value, data)

    async def mint_midnight_diner_pass_nft(self):
        contract = '0xf9aDb505EaadacCF170e48eE46Ee4d5623f777d7'
        value = intToDecimal(0.000877, 18)
        data = '0x574fed17000000000000000000000000' + self.address[2:] + '000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000000'
        await self.logic_for_mint(contract, value, data)

    async def mint_doodlestv_pass_nft(self):
        status_code, response = await self.request_data("0x76FEa18dcA768c27Afc3a32122c6b808C0aD9b06")
        data = response['callData']['data']
        contract = Web3().to_checksum_address(response['callData']['to'])
        value = int(response['callData']['value'], 16)
        await self.logic_for_mint(contract, value, data)

    async def mint_onchain_summer_board_nft(self):
        status_code, response = await self.request_data("0xf9aDb505EaadacCF170e48eE46Ee4d5623f777d7")
        data = response['callData']['data']
        contract = Web3().to_checksum_address(response['callData']['to'])
        value = int(response['callData']['value'], 16)
        await self.logic_for_mint(contract, value, data)
