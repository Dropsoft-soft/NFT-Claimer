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
import requests

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
        contract_txn['gas'] = int(gas*FEE_MULTIPLIER)

        status, tx_link = await self.send_tx(contract_txn)
        if status == 1:
            logger.success(f"[{self.id}] {self.address} | claimed nft nickname: {nickname} | {tx_link}")
            await asyncio.sleep(5)
            return
        else:
            logger.error(f"[{self.id}] {self.address} | tx is failed | {tx_link}")
        # except Exception as error:
        #     logger.error(error)
        #     return False
    async def mins_omihub_nft(self):
        contract_txn = {
            "chainId": self.chain_id,
            "from": self.address,
            "to": "0xD932ad965CE8a342ad49E14c98Bcf179Eb668C56",
            "value": 180000000000000,
            "data": "0xa0712d680000000000000000000000000000000000000000000000000000000000000001",
            "gas": 0,
            'maxFeePerGas': int(await self.web3.eth.gas_price*FEE_MULTIPLIER),
            'maxPriorityFeePerGas': int(await self.web3.eth.max_priority_fee),  
            'nonce': await self.web3.eth.get_transaction_count(self.address),
        }
        gas = await self.web3.eth.estimate_gas(contract_txn)
        contract_txn['gas'] = int(gas*1.1)
        status, tx_link = await self.send_tx(contract_txn)
        if status == 1:
            logger.success(f"[{self.id}] {self.address} | claimed nft: {tx_link}")
            await asyncio.sleep(5)
            return
        else:
            logger.error(f"[{self.id}] {self.address} | tx is failed | {tx_link}")

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
    @retry
    async def create_delegatee(self):
        signed_string = await self.sign_message("{\n\t\"agreeCodeConduct\": true,\n\t\"daoSlug\": \"SCROLL\",\n\t\"discord\": \"\",\n\t\"delegateStatement\": \"A brief intro to yourself: \\n\\nA message to the community and ecosystem:\\n\\nDiscourse username:\",\n\t\"email\": \"\",\n\t\"twitter\": \"\",\n\t\"warpcast\": \"\",\n\t\"topIssues\": [],\n\t\"topStakeholders\": []\n}")
        url = "https://gov.scroll.io/delegates/create"
        # payload = """[\n    {\n        \"address\": \"{self.}\",\n        \"delegateStatement\": {\n            \"agreeCodeConduct\": true,\n            \"daoSlug\": \"SCROLL\",\n            \"discord\": \"\",\n            \"delegateStatement\": \"A brief intro to yourself: \\n\\nA message to the community and ecosystem:\\n\\nDiscourse username:\",\n            \"email\": \"\",\n            \"twitter\": \"\",\n            \"warpcast\": \"\",\n            \"topIssues\": [],\n            \"topStakeholders\": [],\n            \"openToSponsoringProposals\": null,\n            \"mostValuableProposals\": [],\n            \"leastValuableProposals\": []\n        },\n        \"signature\": \"0xf4a6ff177dc4c55ca6f644a0907e33a4690a387e1080a3180159fa5232d9b59246a75ad747eb4528edb5c2caf35a4a99867cbc01abf6ce9fc938c54a32084ddc1c\",\n        \"message\": \"{\\n\\t\\\"agreeCodeConduct\\\": true,\\n\\t\\\"daoSlug\\\": \\\"SCROLL\\\",\\n\\t\\\"discord\\\": \\\"\\\",\\n\\t\\\"delegateStatement\\\": \\\"A brief intro to yourself: \\\\n\\\\nA message to the community and ecosystem:\\\\n\\\\nDiscourse username:\\\",\\n\\t\\\"email\\\": \\\"\\\",\\n\\t\\\"twitter\\\": \\\"\\\",\\n\\t\\\"warpcast\\\": \\\"\\\",\\n\\t\\\"topIssues\\\": [],\\n\\t\\\"topStakeholders\\\": []\\n}\"\n    }\n]"""
        payload = json.dumps([
    {
        "address": f"{self.address}",
        "delegateStatement": {
            "agreeCodeConduct": True,
            "daoSlug": "SCROLL",
            "discord": "",
            "delegateStatement": "A brief intro to yourself: \n\nA message to the community and ecosystem:\n\nDiscourse username:",
            "email": "",
            "twitter": "",
            "warpcast": "",
            "topIssues": [],
            "topStakeholders": [],
            "openToSponsoringProposals": None,
            "mostValuableProposals": [],
            "leastValuableProposals": []
        },
        "signature": f"{signed_string}",
        "message": "{\n\t\"agreeCodeConduct\": true,\n\t\"daoSlug\": \"SCROLL\",\n\t\"discord\": \"\",\n\t\"delegateStatement\": \"A brief intro to yourself: \\n\\nA message to the community and ecosystem:\\n\\nDiscourse username:\",\n\t\"email\": \"\",\n\t\"twitter\": \"\",\n\t\"warpcast\": \"\",\n\t\"topIssues\": [],\n\t\"topStakeholders\": []\n}"
    }
])
        headers = {
            'accept': 'text/x-component',
            'accept-language': 'en-US,en;q=0.9,uk;q=0.8',
            'cache-control': 'no-cache',
            'content-type': 'text/plain;charset=UTF-8',
            'next-action': '885a57e1f202724ff4ba962c69d432e5ea192f28',
            'origin': 'https://gov.scroll.io',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://gov.scroll.io/delegates/create',
            'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
        }
        proxies = None
        if USE_PROXY == True:
            proxy = WALLET_PROXIES[self.key]
            proxies = {
                "http": proxy,
                "https": proxy
            }

        response = requests.request("POST", url, headers=headers, data=payload, proxies=proxies)
        if response.status_code == 200:
            logger.info(f'Registred delegatee {self.address}')
        else:
            logger.error(f'Not registred {response.status_code}')

    async def get_drop(self):
        url = "https://claim.scroll.io/?step=4"
        headers = {
        'Content-Type': 'text/plain;charset=UTF-8',
        'Accept': 'text/x-component',
        'Sec-Fetch-Site': 'same-origin',
        'Accept-Language': 'en-US,en-GB;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Sec-Fetch-Mode': 'cors',
        'Origin': 'https://claim.scroll.io',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15',
        'Content-Length': '46',
        'Referer': 'https://claim.scroll.io/?step=4',
        'Sec-Fetch-Dest': 'empty',
        'Priority': 'u=3, i',
        'Next-Action': '2ab5dbb719cdef833b891dc475986d28393ae963'
        }

        proxies = None
        if USE_PROXY == True:
            proxy = WALLET_PROXIES[self.key]
            proxies = {
                "http": proxy,
                "https": proxy
            }
        payload = f"[\"{self.address}\"]"
        response = requests.request("POST", url, headers=headers, data=payload, proxies=proxies)
        if response.status_code == 200:
            dataObj = response.text.split('1:')[1]
            try:
                json_result = json.loads(dataObj)
                status = json_result['claim_status']
                if status == "CLAIMED":
                    logger.warning('Drop already claimed.skip')
                else:
                    amount = int(json_result['amount'])
                    merkle_proof = json_result['proof']
                    await self.claim_tx(amount, merkle_proof)
            except Exception as error:
                logger.error('Not elligable for claim, or onchain error')

    async def claim_tx(self, amount, merkle_proof):
        claim_contract = self.web3.eth.contract(address=Web3.to_checksum_address('0xE8bE8eB940c0ca3BD19D911CD3bEBc97Bea0ED62'), abi=CLAIM_ABI)
        contract_txn = await claim_contract.functions.claim(self.address, amount, merkle_proof).build_transaction({
            'nonce': await self.web3.eth.get_transaction_count(self.address),
            'from': self.address,
            'gas': 0,
            'maxFeePerGas': int(await self.web3.eth.gas_price*FEE_MULTIPLIER),
            'maxPriorityFeePerGas': int(await self.web3.eth.max_priority_fee),  
            'chainId': self.chain_id,
            'value': 0,
        })
        gas = await self.web3.eth.estimate_gas(contract_txn)
        contract_txn['gas'] = int(gas*FEE_MULTIPLIER)

        status, tx_link = await self.send_tx(contract_txn)
        if status == 1:
            logger.success(f"[{self.id}] {self.address} | claimed {tx_link}")
            await asyncio.sleep(5)
            return
        else:
            logger.error(f"[{self.id}] {self.address} | tx is failed | {tx_link}")

    
CLAIM_ABI = '[{"inputs":[{"internalType":"bytes32","name":"_merkleRoot","type":"bytes32"},{"internalType":"address","name":"_token","type":"address"},{"internalType":"address","name":"_owner","type":"address"},{"internalType":"uint256","name":"_claimEnd","type":"uint256"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"internalType":"address","name":"target","type":"address"}],"name":"AddressEmptyCode","type":"error"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"AddressInsufficientBalance","type":"error"},{"inputs":[],"name":"AlreadyClaimed","type":"error"},{"inputs":[],"name":"ClaimFinished","type":"error"},{"inputs":[],"name":"ClaimNotFinished","type":"error"},{"inputs":[],"name":"EmptyProof","type":"error"},{"inputs":[],"name":"FailedInnerCall","type":"error"},{"inputs":[],"name":"InvalidAmount","type":"error"},{"inputs":[],"name":"InvalidProof","type":"error"},{"inputs":[],"name":"InvalidToken","type":"error"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"OwnableInvalidOwner","type":"error"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"OwnableUnauthorizedAccount","type":"error"},{"inputs":[{"internalType":"address","name":"token","type":"address"}],"name":"SafeERC20FailedOperation","type":"error"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Claimed","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferStarted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Withdrawn","type":"event"},{"inputs":[],"name":"CLAIM_END","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"MERKLE_ROOT","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"TOKEN","outputs":[{"internalType":"contract IERC20","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"acceptOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_account","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"bytes32[]","name":"_merkleProof","type":"bytes32[]"}],"name":"claim","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"}],"name":"hasClaimed","outputs":[{"internalType":"bool","name":"claimed","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pendingOwner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"}]'