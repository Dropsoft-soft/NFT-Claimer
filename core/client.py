import math
from loguru import logger
from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth
from eth_account.messages import encode_defunct

from core.request import global_request
from core.retry import retry
from .data import DATA, ABI_PHOSPHOR
from .utils import WALLET_PROXIES, decimalToInt, intToDecimal, round_to, sleeping, ERC20_ABI
from user_data.config import RETRY, USE_PROXY
import asyncio
import random
import time
from eth_utils import keccak
from eth_abi import encode
import requests
import json

class WebClient():
    def __init__(self, id:int, key: str, chain: str):
        self.proxy = None
        self.id = id
        self.key = key
        self.chain = chain
        self.web3 = self._initialize_web3()
        self.address = self._get_account_address()
        self.chain_id = self._get_chain_id()

    def _initialize_web3(self) -> Web3:
        rpc = DATA[self.chain]['rpc']
        web3 = Web3(AsyncHTTPProvider(rpc), modules={"eth": (AsyncEth)}, middlewares=[])

        if (USE_PROXY and WALLET_PROXIES):
            try:
                self.proxy = WALLET_PROXIES[self.key]
                web3 = Web3(AsyncHTTPProvider(rpc, request_kwargs={"proxy": self.proxy}), modules={"eth": (AsyncEth)}, middlewares=[])
            except Exception as error:
                logger.error(f'{error}. Use web3 without proxy')
        return web3
    
    def _get_account_address(self) -> str:
        return self.web3.eth.account.from_key(self.key).address

    def _get_chain_id(self) -> int:
        return DATA[self.chain]['chain_id']
    
    async def get_data_token(self, token_address: str):
        try:
            token_contract  = self.web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
            decimals        = await token_contract.functions.decimals().call()
            symbol          = await token_contract.functions.symbol().call()
            return token_contract, decimals, symbol
        except Exception as error:
            logger.error(error)

    async def get_token_info(self, token_address: str) -> dict:
        if token_address == '': 
            address = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
            decimal = 18
            symbol = DATA[self.chain]['token']
            token_contract = ''
        else:
            address = Web3.to_checksum_address(token_address)
            token_contract, decimal, symbol = await self.get_data_token(address)

        return {'address': address, 'symbol': symbol, 'decimal': decimal, 'contract': token_contract}
    
    async def get_balance(self, token_address: str) -> float:
        while True:
            try:
                token_data = await self.get_token_info(token_address)
                if token_address == '': # eth
                    balance = await self.web3.eth.get_balance(self.web3.to_checksum_address(self.address))
                else:
                    balance = await token_data['contract'].functions.balanceOf(self.web3.to_checksum_address(self.address)).call()

                balance_human = decimalToInt(balance, token_data['decimal']) 
                return balance_human

            except Exception as error:
                logger.error(error)
                await asyncio.sleep(1)

    async def wait_balance(self, min_balance: float, token_address: str):
        token_data = await self.get_token_info(token_address)
        logger.info(f'{self.address} | waiting {min_balance} {token_data["symbol"]} [{self.chain}]')

        while True:
            try:
                balance = await self.get_balance(token_address)
                if balance > min_balance:
                    logger.info(f'{self.address} | balance : {round_to(balance)} {token_data["symbol"]} [{self.chain}]')
                    break
                await asyncio.sleep(1)

            except Exception as error:
                logger.error(f'balance error : {error}. check again')
                await asyncio.sleep(10)
    
    async def add_gas_limit(self, contract_txn) -> dict:
        pluser = [1.01, 1.05]
        gasLimit = await self.web3.eth.estimate_gas(contract_txn)
        contract_txn['gas'] = int(gasLimit * random.uniform(pluser[0], pluser[1]))
        # print(contract_txn)
        return contract_txn
    
    async def add_gas_price(self, contract_txn) -> dict:
        if self.chain == 'bsc':
            contract_txn['gasPrice'] = 1000000000
        else:
            gas_price = await self.web3.eth.gas_price
            contract_txn['gasPrice'] = gas_price
        return contract_txn
    
    def get_total_fee(self, contract_txn) -> bool:
        dollars = 10
        gas = int(contract_txn['gas'] * contract_txn['gasPrice'])
        gas = decimalToInt(gas, 18) * dollars
        logger.info(f'total_gas : {round_to(gas)} $')
        if gas > dollars:
            logger.info(f'gas is too high : {round_to(gas)}$ > {dollars}$. sleep and try again')
            sleeping(30,30)
            return False
        else:
            return True
        
    async def get_allowance(self, token_address: str, spender: str) -> int:
        try:
            contract = self.web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
            amount_approved = await contract.functions.allowance(self.address, spender).call()
            return amount_approved
        except Exception as error:
            logger.error(f'{error}. Return 0')
            return 0
        
    async def approve(self, amount: int, token_address: str, spender: str, retry=0):
        try:
            spender = Web3.to_checksum_address(spender)
            token_data = await self.get_token_info(token_address)

            module_str = f'approve : {token_data["symbol"]}'

            allowance_amount = await self.get_allowance(token_address, spender)
            if amount <= allowance_amount: return

            contract_txn = await token_data["contract"].functions.approve(
                spender,
                115792089237316195423570985008687907853269984665640564039457584007913129639935
                ).build_transaction(
                {
                    "chainId": self.chain_id,
                    "from": self.address,
                    "nonce": await self.web3.eth.get_transaction_count(self.address),
                    'gasPrice':  await self.web3.eth.gas_price,
                    'gas': 0,
                    "value": 0
                }
            )
            if self.get_total_fee(contract_txn) == False: return await self.approve(amount, token_address, spender, retry)

            status, tx_link = await self.send_tx(contract_txn)

            if status == 1:
                logger.success(f"{self.address} | {module_str} | {tx_link}")
                await asyncio.sleep(5)
            else:
                logger.error(f"{module_str} | tx is failed | {tx_link}")
                if retry < RETRY:
                    logger.info(f"try again in 10 sec.")
                    await asyncio.sleep(10)
                    return await self.approve(amount, token_address, spender, retry+1)

        except Exception as error:
            logger.error(f'{error}')
            if retry < RETRY:
                logger.info(f'try again in 10 sec.')
                await asyncio.sleep(10)
                return await self.approve(amount, token_address, spender, retry+1)
   
    async def sign_tx(self, contract_txn):
        signed_tx = self.web3.eth.account.sign_transaction(contract_txn, self.key)
        raw_tx_hash = await self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash = self.web3.to_hex(raw_tx_hash)
        return tx_hash
    
    async def get_status_tx(self, tx_hash) -> int:
        logger.info(f'{self.chain} : checking tx_status : {tx_hash}')
        start_time_stamp = int(time.time())

        while True:
            try:
                receipt = await self.web3.eth.get_transaction_receipt(tx_hash)
                status = receipt["status"]
                if status in [0, 1]:
                    return status

            except:
                time_stamp = int(time.time())
                if time_stamp-start_time_stamp > 300:
                    logger.info(f'Did not receive tx_status for {100} sec, assuming that tx is a success')
                    return 1
                await asyncio.sleep(1)
    
    async def get_amount_in(self, keep_from: float, keep_to: float, all_balance: bool, token: str, amount_from: float, amount_to: float, multiplier=1) -> int:
        keep_value = round(random.uniform(keep_from, keep_to), 8)
        if all_balance: amount = await self.get_balance(token) - keep_value
        else: amount = round(random.uniform(amount_from, amount_to), 8)

        amount = amount*multiplier
        return amount
    
    async def send_tx(self, contract_txn):
        try:
            tx_hash = await self.sign_tx(contract_txn)
            status  = await self.get_status_tx(tx_hash)
            tx_link = f'{DATA[self.chain]["scan"]}/{tx_hash}'
            return status, tx_link
        except Exception as error:
            logger.error(error)
            return False, error
        
    async def transfer(self, amount: float, token_address: str, transfer_all_balance: bool, to_address: str):
        try:
            # to_address = RECIPIENTS_WALLETS[self.key]
            amount = await self.get_amount_in(0, 0, transfer_all_balance, token_address, amount, amount, 0.999)
            token_data = await self.get_token_info(token_address)
            value = intToDecimal(amount, token_data['decimal']) 
            if token_address == '':
                contract_txn = {
                    'from': self.address,
                    'chainId': self.chain_id,
                    'gasPrice': await self.web3.eth.gas_price,
                    'nonce': await self.web3.eth.get_transaction_count(self.address),
                    'gas': 0,
                    'to': Web3.to_checksum_address(to_address),
                    'value': value
                }
            else:
                contract_txn = await token_data['contract'].functions.transfer(
                    Web3.to_checksum_address(to_address),
                    int(value)
                    ).build_transaction(
                        {
                            'from': self.address,
                            'chainId': self.chain_id,
                            'gasPrice': await self.web3.eth.gas_price,
                            'gas': 0,
                            'nonce': await self.web3.eth.get_transaction_count(self.address),
                            'value': 0
                        }
                    )
            # contract_txn = await self.add_gas_price(contract_txn)
            # contract_txn = await self.add_gas_limit(contract_txn)
            gas = await self.web3.eth.estimate_gas(contract_txn)
            contract_txn['gas'] = int(gas*1.01)
            status, tx_link = await self.send_tx(contract_txn)

            if status == 1:
                logger.success(f"{self.address} | transfer | {tx_link}")
                await asyncio.sleep(5)
            else:
                logger.error(f"transfer | tx is failed | {tx_link}")
        except Exception as error:
            logger.error(error)
            return False, error

    async def sign_message(self, message_text: str) -> str:
        message = encode_defunct(text=message_text)
        signed_message = self.web3.to_hex(
            self.web3.eth.account.sign_message(message, private_key=self.key).signature)
        return signed_message

    def get_voucher(self) -> str:
        logger.info(f"Trying to get response data from phosphor.")

        url = "https://public-api.phosphor.xyz/v1/purchase-intents"

        payload = json.dumps({
            "buyer": {
                "eth_address": self.address,
            },
            "listing_id": "86a8741b-28dd-42ca-9f2f-dfb173a62099",
            "provider": "MINT_VOUCHER",
            "quantity": 1
        })
        headers = {
            'Content-Type': 'application/json',
            # 'Cookie': '__cf_bm=oOHsQm2q5AfX5_s32tobx38.w6_og.LTfCn8jNcuch4-1721682527-1.0.1.1-x_E0K8uirx0SbGwNuYnJuQG8sJbK48oAXVD7NBk09j2J3RTV4B.5jYc32HR3WDYgtF7aE7jhgWA_bFN26siomw'
        }
        prxies = None
        if USE_PROXY:
            prxies = {
              "http"  : self.proxy, 
              "https" : self.proxy, 
            }
        response = requests.request("POST", url, headers=headers, data=payload, proxies=prxies)
        if response.status_code > 300:
            logger.info(f"Error in getting response data {response.status_code}. Sleep for 30 secs and try again.")
            time.sleep(30)
            self.get_voucher()
        else:
            response_data = response.json()

            signature = response_data["data"]["signature"]

            initial_recipient = self.web3.to_checksum_address(response_data["data"]["voucher"]["initial_recipient"])
            initial_recipient_amount = int(response_data["data"]["voucher"]["initial_recipient_amount"])
            net_recipient = self.web3.to_checksum_address(response_data["data"]["voucher"]["net_recipient"])
            quantity = response_data["data"]["voucher"]["quantity"]
            nonce = response_data["data"]["voucher"]["nonce"]
            expiry = response_data["data"]["voucher"]["expiry"]
            price = int(response_data["data"]["voucher"]["price"])
            token_id = int(response_data["data"]["voucher"]["token_id"])
            currency = self.web3.to_checksum_address(response_data["data"]["voucher"]["currency"])

            voucher = (net_recipient,
                       initial_recipient,
                       initial_recipient_amount,
                       quantity,
                       nonce,
                       expiry,
                       price,
                       token_id,
                       currency,
            )
            # print(response.text)
            return voucher, signature

    async def claimNFT(self):
        try:
            supply_contract = self.web3.to_checksum_address('0x8975e0635586C6754C8D549Db0e3C7Ee807D9C8C')
            contract = self.web3.eth.contract(address=supply_contract, abi=ABI_PHOSPHOR)

            voucher, signature = self.get_voucher()

            signature = self.clean_and_convert_hex_string(signature)


            contract_txn = await contract.functions.mintWithVoucher(
                voucher,
                signature
            ).build_transaction({
                'from': self.address,
                'gas': 0,
                'gasPrice': await self.web3.eth.gas_price,
                'nonce': await self.web3.eth.get_transaction_count(self.address),
                'chainId': self.chain_id,
                'value': 0,
            })
            gas = await self.web3.eth.estimate_gas(contract_txn)
            contract_txn['gas'] = int(gas*1.05)

            status, tx_link = await self.send_tx(contract_txn)
            print(status, tx_link)
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


    def clean_and_convert_hex_string(self, hex_string):
        if hex_string.startswith('0x'):
            hex_string = hex_string[2:]

        hex_string = hex_string.strip()

        valid_chars = "0123456789abcdefABCDEF"
        for char in hex_string:
            if char not in valid_chars:
                raise ValueError(f"Invalid character '{char}' found in hexadecimal string")

        if len(hex_string) % 2 != 0:
            hex_string = '0' + hex_string

        byte_data = bytes.fromhex(hex_string)
        return byte_data

    async def check_data_token(self, token_address):
        try:
            token_contract  = self.web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
            decimals        = await token_contract.functions.decimals().call()
            symbol          = await token_contract.functions.symbol().call()

            data = {
                'contract'  : token_contract,
                'decimal'   : decimals,
                'symbol'    : symbol
            }
            return token_contract, decimals, symbol

        except Exception as error:
            logger.error(f'check_data_token {error}')
    
    async def check_balance(self, address_contract):
        try:
            if address_contract == '': # eth
                balance         = self.web3.eth.get_balance(self.web3.to_checksum_address(self.address))
                token_decimal   = 18
            else:
                token_contract, token_decimal, symbol = await self.check_data_token(Web3.to_checksum_address(address_contract))
                balance = await token_contract.functions.balanceOf(self.address).call()

            human_readable = decimalToInt(balance, token_decimal)
            return human_readable

        except Exception as error:
            logger.error(error)
            await asyncio.sleep(5)
            self.check_balance(address_contract)
        
    async def wait_balance(self, min_balance, token):

        if token == '':
            symbol = DATA[self.chain]['token']
        else:
            token_contract, token_decimal, symbol = await self.check_data_token(self.chain, token)

        logger.info(f'waiting {min_balance} {symbol} in {self.chain}')

        while True:

            try:
                balance = await self.check_balance(token)
                if balance == None:
                    await asyncio.sleep(5)
                    logger.info(f'balance loading failed will repeat')
                else:
                    if balance > min_balance:
                        logger.info(f'balance : {balance}')
                        break

            except Exception as error:
                logger.error(f'balance error : {error}. check again')
                await asyncio.sleep(5)
