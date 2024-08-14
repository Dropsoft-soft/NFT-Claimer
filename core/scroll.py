import json
import time
from web3 import Web3
from core.abi.abi import SCROLL_MAIN_ABI
from core.client import WebClient
from loguru import logger
import asyncio, random
from random_user_agent.user_agent import UserAgent
from core.request import global_request
from core.utils import BADGE_LIST, WALLET_PROXIES, intToDecimal, sleep
from user_data.config import FEE_MULTIPLIER, USE_PROXY
from user_data.config import MINT_RANDOM_NICKNAME
user_agent_rotator = UserAgent(software_names=['chrome'], operating_systems=['windows', 'linux'])

class ScrollCanvas(WebClient):
    def __init__(self, id:int, key: str):
        super().__init__(id, key, 'scroll')
        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,uk;q=0.8',
            'cache-control': 'no-cache',
            'origin': 'https://scroll.io',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://scroll.io/',
            'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': user_agent_rotator.get_random_user_agent(),
            'Content-Type': 'application/json'
        }

    async def getSignature(self):
        proxy = None
        if USE_PROXY == True:
            proxy = WALLET_PROXIES[self.key]
        url = f"https://canvas.scroll.cat/code/NTAQN/sig/{self.address}"
        
        status_code, response = await global_request(wallet=self.address, method='get', url=url, headers=self.headers, proxy=proxy)
        return status_code, response
    
    async def is_elligable_address(self, domain, badge):
        try:
            proxy = None
            if USE_PROXY == True:
                proxy = WALLET_PROXIES[self.key]
            url = f'{domain}/check?badge={badge}&recipient={self.address}'
            
            status_code, response = await global_request(wallet=self.address, method='get', url=url, headers=self.headers, proxy=proxy)
            return response
        except Exception as error:
            logger.error(error)
            return False
    
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

    async def mintUserName(self):
        try:
            mint_contract = self.web3.eth.contract(address=Web3.to_checksum_address('0xb23af8707c442f59bdfc368612bd8dbcca8a7a5a'), abi=SCROLL_MAIN_ABI)
            nickname = str(random.choice(MINT_RANDOM_NICKNAME))
            code, response = await self.getSignature()
            bytes_for = response['signature']
            base_fee = (await self.web3.eth.max_priority_fee)
            contract_txn = await mint_contract.functions.mint(nickname, bytes_for).build_transaction({
                'nonce': await self.web3.eth.get_transaction_count(self.address),
                'from': self.address,
                'gas': 0,
                'maxFeePerGas': int(await self.web3.eth.gas_price),
                'maxPriorityFeePerGas': int(await self.web3.eth.max_priority_fee*FEE_MULTIPLIER),  
                'chainId': self.chain_id,
                'value': intToDecimal(0.001, 18),
            })
            gas = await self.web3.eth.estimate_gas(contract_txn)
            contract_txn['gas'] = int(gas*FEE_MULTIPLIER)

            status, tx_link = await self.send_tx(contract_txn)
            if status == 1:
                logger.success(f"[{self.id}] {self.address} | claimed nft nickname: {nickname} | {tx_link}")
                await asyncio.sleep(5)
                return True
            else:
                logger.error(f"[{self.id}] {self.address} | tx is failed | {tx_link}")
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
                'maxFeePerGas': int(await self.web3.eth.gas_price),
                'maxPriorityFeePerGas': int(await self.web3.eth.max_priority_fee*FEE_MULTIPLIER),  
                'gas': 0,
                'chainId': self.chain_id,
                'to': to,
                'value': 0,
            }
            gas = await self.web3.eth.estimate_gas(contract_txn)
            contract_txn['gas'] = int(gas*FEE_MULTIPLIER)
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
        badge_array = BADGE_LIST['badges']
        logger.info(f'Received badges: {len(badge_array)}')
        minted_counter = 0
        for jsonBadge in badge_array:
            badge = jsonBadge['badgeContract']
            domain = jsonBadge['baseUrl']
            name = jsonBadge['name']
            json = await self.is_elligable_address(domain, badge)
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
        if minted_counter > 0:
            logger.success(f'[{self.id} - {self.address}] Minted {minted_counter}')
        else:
            logger.info(f'[{self.id} - {self.address}] Minted {minted_counter}')
        
# 0xC47300428b6AD2c7D03BB76D05A176058b47E6B0
# 0x39fb5E85C7713657c2D9E869E974FF1e0B06F20C
# https://canvas.scroll.cat/badge/check?badge=0x3dacAd961e5e2de850F5E027c70b56b5Afa5DfeD&recipient=

# // {
# //     "name": "Scroll Overlord",
# //     "image": "https://xenobunny.s3.amazonaws.com/images/scroll-canvas/scroll-overlord-badge.png",
# //     "description": "Participated in at least one Land War season on scroll.",
# //     "badgeContract": "0xb2c69173829E23EE2876FBe13Ab474FEe101bc64",
# //     "category": "Achievement",
# //     "issuer": {
# //         "name": "XenoBunny",
# //         "logo": "https://scroll-eco-list.netlify.app/logos/XenoBunny.jpg",
# //         "origin": "https://www.xenobunny.xyz/"
# //     },
# //     "native": false,
# //     "eligibilityCheck": true
# // },
# // {
# //     "name": "Scroll Domain Master Badge 🎖️",
# //     "image": "https://assets.znsconnect.io/domain-master-badge.png",
# //     "description": "Achieve the Scroll Domain Master Badge by minting 5 domains on Scroll. This prestigious badge marks you as a master in the domain space! Mint your domains now: https://zns.bio/",
# //     "badgeContract": "0x55B867a955e4384bcAc03eF7F2E492F68016C152",
# //     "category": "Achievement",
# //     "issuer": {
# //         "name": "ZNS Connect",
# //         "logo": "https://scroll-eco-list.netlify.app/logos/ZNS Connect.jpg",
# //         "origin": "https://www.znsconnect.io/"
# //     },
# //     "native": false,
# //     "eligibilityCheck": true
# // },
# //         {
# //     "name": "ZNS Badge",
# //     "image": "https://assets.znsconnect.io/scroll-badge.jpg",
# //     "description": "Earn this badge for minting a ZNS Domain on Scroll",
# //     "badgeContract": "0x0246D65bA41Da3DB6dB55e489146eB25ca3634E5",
# //     "issuer": {
# //         "name": "ZNS Connect",
# //         "logo": "https://scroll-eco-list.netlify.app/logos/ZNS Connect.jpg",
# //         "origin": "https://www.znsconnect.io/"
# //     },
# //     "eligibilityCheck": true,
# //     "native": false
# // },