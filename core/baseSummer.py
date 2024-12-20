from web3 import Web3
from core.abi.abi import SCROLL_MAIN_ABI
from core.client import WebClient
from loguru import logger
import asyncio, random
from core.request import global_request
from core.utils import WALLET_PROXIES, intToDecimal
from user_data.config import FEE_MULTIPLIER, USE_PROXY
from eth_account.messages import encode_defunct, encode_structured_data

from eth_account import Account

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

    async def mint_welcome_to_new_base(self):
        data = '0x574fed17000000000000000000000000'+self.address[2:] +'000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000000'
        contract = Web3().to_checksum_address('0x803Fc79D31AB30a39B3BD2A90171470cC82Ba44a')
        await self.logic_for_mint(contract, 100000000000000, data)

    async def getamout_odos(self):
        proxy = None
        if USE_PROXY == True:
            proxy = WALLET_PROXIES[self.key]
        lowercased = self.address.lower()
        url = f'https://api.odos.xyz/loyalty/users/{lowercased}/balances'
        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,uk;q=0.8',
            'cache-control': 'no-cache',
            'origin': 'https://app.odos.xyz',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://app.odos.xyz/',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }
        status, result = await self.global_request(url=url, headers=headers, proxy=proxy)
        if 'data' in result and 'claimableTokenBalance' in result['data']:
            return int(result['data']['claimableTokenBalance'])
        else:
            return 0
        
    async def odos_approve(self):
        typed_data = {
            "domain": {
                "name": "OdosDaoRegistry",
                "version": "1",
                "chainId": 8453,
                "verifyingContract": "0x8bDA13Bc6DC08d4008C9f3A72C4572C98478502c",
            },
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                    {"name": "chainId", "type": "uint256"},
                    {"name": "verifyingContract", "type": "address"},
                ],
                "Registration": [
                    {"name": "member", "type": "address"},
                    {"name": "agreement", "type": "string"},
                    {"name": "nonce", "type": "uint256"},
                ],
            },
            "primaryType": "Registration",
            "message": {
                "member": self.address,
                "agreement": "By signing this, you agree to be bound by the terms set forth in the Odos DAO LLC Amended and Restated Operating Agreement (as amended from time to time), available at: https://docs.odos.xyz/home/dao/operating-agreement.",
                "nonce": 0,
            },
        }

        data_encoded = encode_structured_data(typed_data)
        signed_message = self.web3.eth.account.sign_message(data_encoded, private_key=self.key)
        # signed = Account.sign_typed_data(self.key, full_message=json_eip)
        return signed_message.signature.hex()
     
    async def getProof(self):
        proxy = None
        if USE_PROXY == True:
            proxy = WALLET_PROXIES[self.key]
        url = f'https://api.odos.xyz/loyalty/permits/8453/0xca73ed1815e5915489570014e024b7EbE65dE679/{self.address}'
        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,uk;q=0.8',
            'cache-control': 'no-cache',
            'origin': 'https://app.odos.xyz',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://app.odos.xyz/',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }
        status, result = await global_request(self.address, url=url, headers=headers, proxy=proxy)
        if 'data' in result:
            return result['data']['claim'], result['data']['signature']
        else:
            return None
    
    async def claimDrop(self):
        await self.approve(57896044618658097711785492504343953926634992332820282019728792003956564819967, '0xca73ed1815e5915489570014e024b7EbE65dE679', '0x4C8f8055D88705f52c9994969DDe61AB574895a3')
        signed = await self.odos_approve()
        claim, signature = await self.getProof()
        claim_contract = self.web3.eth.contract(address=Web3.to_checksum_address('0x4C8f8055D88705f52c9994969DDe61AB574895a3'), abi=BASE_ODOS_ABI)
        claim_array = (Web3.to_checksum_address(claim['sender']),Web3.to_checksum_address(claim['recipient']), Web3.to_checksum_address(claim['payoutToken']),int(claim['amount']), int(claim['nonce']), int(claim['deadline']))
        sign_array = (self.address, "By signing this, you agree to be bound by the terms set forth in the Odos DAO LLC Amended and Restated Operating Agreement (as amended from time to time), available at: https://docs.odos.xyz/home/dao/operating-agreement.", 0)
        contract_txn = await claim_contract.functions.registerAndClaim(claim_array, sign_array, signature, signed).build_transaction({
            'nonce': await self.web3.eth.get_transaction_count(self.address),
            'from': self.address,
            'gas': 0,
            'gasPrice': (await self.web3.eth.gas_price),
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




BASE_ODOS_ABI = '[{"inputs":[{"internalType":"address","name":"_initialOwner","type":"address"},{"internalType":"address","name":"_authorizedSigner","type":"address"},{"internalType":"address","name":"_odosDaoRegistry","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"internalType":"address","name":"target","type":"address"}],"name":"AddressEmptyCode","type":"error"},{"inputs":[],"name":"AlreadyAuthorized","type":"error"},{"inputs":[],"name":"ECDSAInvalidSignature","type":"error"},{"inputs":[{"internalType":"uint256","name":"length","type":"uint256"}],"name":"ECDSAInvalidSignatureLength","type":"error"},{"inputs":[{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"ECDSAInvalidSignatureS","type":"error"},{"inputs":[],"name":"ExpiredSignature","type":"error"},{"inputs":[],"name":"FailedCall","type":"error"},{"inputs":[{"internalType":"uint256","name":"balance","type":"uint256"},{"internalType":"uint256","name":"needed","type":"uint256"}],"name":"InsufficientBalance","type":"error"},{"inputs":[],"name":"InvalidNonce","type":"error"},{"inputs":[],"name":"InvalidShortString","type":"error"},{"inputs":[],"name":"InvalidSignature","type":"error"},{"inputs":[],"name":"NotAuthorized","type":"error"},{"inputs":[],"name":"NotRegistered","type":"error"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"OwnableInvalidOwner","type":"error"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"OwnableUnauthorizedAccount","type":"error"},{"inputs":[{"internalType":"address","name":"token","type":"address"}],"name":"SafeERC20FailedOperation","type":"error"},{"inputs":[{"internalType":"string","name":"str","type":"string"}],"name":"StringTooLong","type":"error"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"newOdosDaoRegistry","type":"address"}],"name":"DaoRegistryUpdated","type":"event"},{"anonymous":false,"inputs":[],"name":"EIP712DomainChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferStarted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":true,"internalType":"address","name":"recipient","type":"address"},{"indexed":true,"internalType":"address","name":"token","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"nonce","type":"uint256"}],"name":"RewardClaimed","type":"event"},{"inputs":[],"name":"acceptOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"authorizedSigner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"components":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"address","name":"payoutToken","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"internalType":"struct Claim","name":"_claim","type":"tuple"},{"internalType":"bytes","name":"_signature","type":"bytes"}],"name":"claimReward","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"eip712Domain","outputs":[{"internalType":"bytes1","name":"fields","type":"bytes1"},{"internalType":"string","name":"name","type":"string"},{"internalType":"string","name":"version","type":"string"},{"internalType":"uint256","name":"chainId","type":"uint256"},{"internalType":"address","name":"verifyingContract","type":"address"},{"internalType":"bytes32","name":"salt","type":"bytes32"},{"internalType":"uint256[]","name":"extensions","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_token","type":"address"}],"name":"extractERC20","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"extractNative","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"components":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"address","name":"payoutToken","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"internalType":"struct Claim","name":"_claim","type":"tuple"}],"name":"getClaimHash","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"odosDaoRegistry","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pendingOwner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"recipientNonces","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"components":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"address","name":"payoutToken","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"internalType":"struct Claim","name":"_claim","type":"tuple"},{"components":[{"internalType":"address","name":"member","type":"address"},{"internalType":"string","name":"agreement","type":"string"},{"internalType":"uint256","name":"nonce","type":"uint256"}],"internalType":"struct Registration","name":"_registration","type":"tuple"},{"internalType":"bytes","name":"_claimSignature","type":"bytes"},{"internalType":"bytes","name":"_registrationSignature","type":"bytes"}],"name":"registerAndClaim","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_odosDaoRegistry","type":"address"}],"name":"updateOdosDaoRegistry","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"_newSigner","type":"address"}],"name":"updateSigner","outputs":[],"stateMutability":"payable","type":"function"}]'