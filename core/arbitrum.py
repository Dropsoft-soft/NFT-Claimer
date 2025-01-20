
from web3 import Web3
from core.abi.abi import SCROLL_MAIN_ABI
from core.client import WebClient
from loguru import logger
import asyncio, random, json
from core.utils import intToDecimal, decimalToInt
from core.utils import WALLET_PROXIES
from user_data.config import FEE_MULTIPLIER, USE_PROXY
from core.request import global_request
from eth_abi import abi

class Arbitrum(WebClient):
    def __init__(self, id:int, key: str):
        super().__init__(id, key, 'arbitrum')
    
    async def claim_drop(self):
        amount, merkle = await self.get_merkle()
        print(amount)
        if amount != None and merkle != None:
            print('start claim')
            await self.claim_tx(amount, merkle)
            
    async def get_merkle(self):
        proxy = None
        message_signed = await self.sign_message(message_text='Orbiter Airdrop')
        if USE_PROXY:
            proxy = WALLET_PROXIES[self.key]
        url = f'https://airdrop-api.orbiter.finance/airdrop/snapshot'
        headers = {
            'token': message_signed,
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }
        status, result = await global_request(self.address, method='post', url=url, headers=headers, proxy=proxy)
        if result['result'] != None:
            proof = result['result']['proof'][0]['data']
            amount = str(result['result']['proof'][0]['amount']).replace(".", "")
            return amount, proof
        else:
            return None, None
            

    async def claim_tx(self, amount, merkle_proof):
        amount_dec = int(amount)
        claim_contract = self.web3.eth.contract(address=Web3.to_checksum_address('0x13dfdd3a9b39323f228daf73b62c23f7017e4679'), abi=CLAIM_ABI)
        data = '0xfa5c4e99071cbb2ff029ddaf4b691745b2ba185cbe9ca2f5fa9e7358bada8fbdce764291'
        emaunt = abi.encode(["uint256"], [amount_dec]).hex()
        merkle_proof_bytes = [bytes.fromhex(proof[2:]) for proof in merkle_proof]
        encoded_proof = abi.encode(["bytes32[]"], [merkle_proof_bytes]).hex()
        data = data + emaunt + encoded_proof
        data = data.replace("0000000000000020000000000000", "0000000000000060000000000000")
        # contract_txn = await claim_contract.functions.claim(bytes.fromhex("071cbb2ff029ddaf4b691745b2ba185cbe9ca2f5fa9e7358bada8fbdce764291"), amount_dec, merkle_proof).build_transaction({
        contract_txn = {
            'to': Web3().to_checksum_address('0x13dfdd3a9b39323f228daf73b62c23f7017e4679'),
            'data': data,
            'nonce': await self.web3.eth.get_transaction_count(self.address),
            'from': self.address,
            'gas': 0,
            'gasPrice': int(await self.web3.eth.gas_price),
            # 'maxPriorityFeePerGas': int(await self.web3.eth.max_priority_fee),  
            'chainId': self.chain_id,
            'value': 0,
        }
        gas = await self.web3.eth.estimate_gas(contract_txn)
        contract_txn['gas'] = int(gas*FEE_MULTIPLIER)

        status, tx_link = await self.send_tx(contract_txn)
        if status == 1:
            logger.success(f"[{self.id}] {self.address} | claimed {tx_link}")
            await asyncio.sleep(5)
            return
        else:
            logger.error(f"[{self.id}] {self.address} | tx is failed | {tx_link}")
CLAIM_ABI = [
  {
    "name": "claim",
    "type": "function",
    "inputs": [
      {
        "name": "userAddress",
        "type": "bytes32"
      },
      {
        "name": "amount",
        "type": "uint256"
      },
      {
        "name": "proof",
        "type": "bytes32[]"
      }
    ],
    "outputs": [],
    "stateMutability": "nonpayable"
  }
]

#        {
#     "func": "claim",
#     "params": [
#         "071cbb2ff029ddaf4b691745b2ba185cbe9ca2f5fa9e7358bada8fbdce764291",
#         649547102560300000000,
#         [
#             "9d811dfc8aac6dda5ecbcbc41e83fab98efc7a5580a424ceedb318062478e356",
#             "3bf465c173d56a899d96ab52e8998c9fdc1fa271648365d3d1c53854485e12b3",
#             "697091ef2db92d61620442e1348d084369cbd13af10947813bf185f56cf2672b",
#             "0a23cbad48e05c1c08ec9f01e3a9be4fd94f5e514d08c0b90eec633dc53cc4dd",
#             "3729bf6068da2403202687c4813ade1a93720d3412314a7875d6f3869abd3eee",
#             "c8803984dbe974e176553011b9bb40ba30c1b7f1de91adcfe7369e19ad7d6dad",
#             "3d60a22f43b97225c27d82b4b1eee9c2efa8352802b91eb818d81bb8122efb6d",
#             "4d132f307a0762865d20479a4938b9e92e78eeb14533cbdf2c26866a6f69805d",
#             "bf86b511fb3925ef1ce80e484db89ed32e4f5702c66da75cae5b50afe236d515",
#             "1fe67c83dc55adb1bd30187c2c2f5d011c81c1aa6510d05e87a12bda03b26bea",
#             "f09e2c7b06e4204b0f20b62c340c4ad1e02fb2a093ad567de0bd4df6f13141cd",
#             "9b7d98f9607e04eba17bfab90df6c1b5a6cf15384fe72624460167fd9361fd82",
#             "8a1041cb3681c38c31dab50150f7f77ea6da80e77d26ee392128fdf03c17ae03",
#             "c08ffe3601f4dc7d4e51fee7b6f8d920b16f016005390aa29f2d9a3a647dae9f",
#             "82b2f98ea911ce1a9306f5cdb3d2f405610cb53672a6362666aaae845fb52355",
#             "7e81aed774f893c0a7fc44c89dfde20b8e95fafe4babd28df31385f821b49e4d",
#             "47b2799f475913157f3e4b2bbbae0fc516a62ba691cf6ea3656d24851f8e016a",
#             "1c166086d02af636d1639187599a29e6f37860b74fda97e88f18ea86f6065e34",
#             "e268b165a259cdf25f3e9cb22a30393e28fefd65c9f379c3be00b5ab54370d35"
#         ]
#     ]
# }