import json
import time
from web3 import Web3
from core.abi.abi import SCROLL_MAIN_ABI
from core.client import WebClient
from loguru import logger
import asyncio, random
from random_user_agent.user_agent import UserAgent
from core.request import global_request
from core.retry import retry
from core.utils import BADGE_LIST, WALLET_PROXIES, intToDecimal, sleep
from user_data.config import FEE_MULTIPLIER, MINT_REFS_FOR_NICKNAME, USE_PROXY
from user_data.config import MINT_RANDOM_NICKNAME
user_agent_rotator = UserAgent(software_names=['chrome'], operating_systems=['windows', 'linux'])

class ScrollCanvas(WebClient):
    def __init__(self, id:int, key: str):
        super().__init__(id, key, 'scroll')
        self.headers = {
            'user-agent': user_agent_rotator.get_random_user_agent(),
            'Content-Type': 'application/json'
        }

    async def getSignature(self):
        proxy = None
        if USE_PROXY == True:
            proxy = WALLET_PROXIES[self.key]
        ref = random.choice(list(MINT_REFS_FOR_NICKNAME))
        url = f"https://canvas.scroll.cat/code/{ref}/sig/{self.address}"
        
        status_code, response = await global_request(wallet=self.address, method='get', url=url, headers=self.headers, proxy=proxy)
        return status_code, response
   
    @retry
    async def is_elligable_address(self, domain, badge):
        proxy = None
        if USE_PROXY == True:
            proxy = WALLET_PROXIES[self.key]
        url = f'{domain}/check?badge={badge}&recipient={self.address}'
        
        status_code, response = await global_request(wallet=self.address, method='get', url=url, headers=self.headers, proxy=proxy)
        return response
  
    @retry
    async def get_tx_for_badge(self, domain, badge):
        try:
            proxy = None
            if USE_PROXY == True:
                proxy = WALLET_PROXIES[self.key]
            url = f'{domain}/claim?badge={badge}&recipient={self.address}'
            status_code, response = await global_request(wallet=self.address, method='get', url=url, headers=self.headers, proxy=proxy)
            return response
        except Exception as error:
            logger.error(error)
            return False
    @retry  
    async def mintUserName(self):
        mint_contract = self.web3.eth.contract(address=Web3.to_checksum_address('0xb23af8707c442f59bdfc368612bd8dbcca8a7a5a'), abi=SCROLL_MAIN_ABI)
        nickname = str(random.choice(MINT_RANDOM_NICKNAME))
        is_minted = await self.is_claimed()
        if is_minted:
            logger.warning('Skip. profile minted')
            return
        nickname_used = await self.verify_nickname(nickname)
        if nickname_used:
            logger.info(f'nickname: {nickname} used. retry')
            return await self.mintUserName()
        code, response = await self.getSignature()
        bytes_for = response['signature']
        base_fee = (await self.web3.eth.max_priority_fee)
        contract_txn = await mint_contract.functions.mint(nickname, bytes_for).build_transaction({
            'nonce': await self.web3.eth.get_transaction_count(self.address),
            'from': self.address,
            'gas': 0,
            'maxFeePerGas': int(await self.web3.eth.gas_price*FEE_MULTIPLIER),
            'maxPriorityFeePerGas': int(await self.web3.eth.max_priority_fee),  
            'chainId': self.chain_id,
            'value': intToDecimal(0.0005, 18),
        })
        gas = await self.web3.eth.estimate_gas(contract_txn)
        contract_txn['gas'] = int(gas*1.1)

        status, tx_link = await self.send_tx(contract_txn)
        if status == 1:
            logger.success(f"[{self.id}] {self.address} | claimed nft nickname: {nickname} | {tx_link}")
            await asyncio.sleep(5)
        else:
            logger.error(f"[{self.id}] {self.address} | tx is failed | {tx_link}")
        # except Exception as error:
        #     logger.error(error)
        #     return False
    
    async def verify_nickname(self, nickname):
        mint_contract = self.web3.eth.contract(address=Web3.to_checksum_address('0xB23AF8707c442f59BDfC368612Bd8DbCca8a7a5a'), abi=SCROLL_MAIN_ABI)
        isused = await mint_contract.functions.isUsernameUsed(nickname).call()
        return isused
    
    async def is_claimed(self):
        mint_contract = self.web3.eth.contract(address=Web3.to_checksum_address('0xB23AF8707c442f59BDfC368612Bd8DbCca8a7a5a'), abi=SCROLL_MAIN_ABI)
        profile = await mint_contract.functions.getProfile(self.address).call()
        isused = await mint_contract.functions.isProfileMinted(profile).call()
        return isused

    @retry  
    async def mintFromJSON(self, json):
        try:
            data = json['tx']['data']
            to = Web3().to_checksum_address(json['tx']['to'])
            contract_txn = {
                'data': data,
                'nonce': await self.web3.eth.get_transaction_count(self.address),
                'from': self.address,
                'maxFeePerGas': int(await self.web3.eth.gas_price*FEE_MULTIPLIER),
                'maxPriorityFeePerGas': int(await self.web3.eth.max_priority_fee),  
                'gas': 0,
                'chainId': self.chain_id,
                'to': to,
                'value': 0,
            }
            gas = await self.web3.eth.estimate_gas(contract_txn)
            contract_txn['gas'] = int(gas*1.01)
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
        
    async def mint_all_available_badge(self):
        try:
            badge_array = BADGE_LIST['badges']
            logger.info(f'Received badges: {len(badge_array)}')
            minted_counter = 0
            for jsonBadge in badge_array:
                name = jsonBadge['name']
                if 'baseURL' in jsonBadge:
                    badge = jsonBadge['badgeContract']
                    domain = jsonBadge['baseURL']
                    json = await self.is_elligable_address(domain, badge)
                    if 'eligibility' in json:
                        is_elligable = json['eligibility']
                        logger.info(f'[{self.id}] Eligable for mint {name}: {is_elligable}')
                        if is_elligable == True:
                            await sleep(5, 30)
                            get_tx_data = await self.get_tx_for_badge(domain, badge)
                            logger.info('Get transaction data')
                            minted_badge = await self.mintFromJSON(get_tx_data)
                            if minted_badge:
                                logger.success(f'[{self.id}] Badge: {badge} minted')
                                minted_counter += 1
                                await sleep(5, 30)
                            else:
                                logger.info(f'[{self.id}] Badge: {badge} not minted')
                        else: 
                            logger.info(f'[{self.id}] Badge: {badge} user not elligable for mint')
                else:
                    logger.info(f'Skip badge: {name}. ')
            if minted_counter > 0:
                logger.success(f'[{self.id} - {self.address}] Minted {minted_counter}')
            else:
                logger.info(f'[{self.id} - {self.address}] Minted {minted_counter}')
        except Exception as error:
            logger.error(error)

