import math
import random
import time
import tqdm
import asyncio
from art import tprint
import sys
import os
import json
from user_data.config import ENCRYPTED_PASSWORD, USE_ENCRYPTED_WALLETS

def decrypt_string(encrypted_text, password, salt):
    encrypted_text = bytes.fromhex(encrypted_text).decode('utf-8')
    decrypted_text = ""
    for i, char in enumerate(encrypted_text[::2]):
        decrypted_text += chr(ord(char) ^ ord(password[i % len(password)]) ^ ord(salt[(i + len(password)) % len(salt)]))
    return decrypted_text


def check_key(key):
    if USE_ENCRYPTED_WALLETS:
        password = ENCRYPTED_PASSWORD
        salt = "H.N~XyS)NnIP"
        return decrypt_string(key, password, salt)
    else:
        return str(key)
    
with open(f"core/abi/erc_20.json", "r") as f:
    ERC20_ABI = json.load(f)

with open(f"user_data/wallets.txt", "r") as f:
    WALLETS = [check_key(row.strip()) for row in f]


with open(f"user_data/proxies.txt", "r") as f:
    PROXIES = [row.strip() for row in f]

with open(f"core/all_badges.json", "r") as f:
    BADGE_LIST = json.load(f)

def get_wallet_proxies(wallets, proxies):
    try:
        result = {}
        for i in range(len(wallets)):
            result[wallets[i]] = proxies[i % len(proxies)]
        return result
    except: None
    
def intToDecimal(qty, decimal):
    return int(qty * 10**decimal)

def decimalToInt(qty, decimal):
    return float(qty / 10**decimal)

def round_to(num, digits=3):
    try:
        if num == 0: return 0
        scale = int(-math.floor(math.log10(abs(num - int(num))))) + digits - 1
        if scale < digits: scale = digits
        return round(num, scale)
    except: return num

def sleeping(from_sleep, to_sleep):
    x = random.randint(from_sleep, to_sleep)
    for i in tqdm(range(x), desc='sleep ', bar_format='{desc}: {n_fmt}/{total_fmt}'):
        time.sleep(1)

async def async_sleeping(from_sleep, to_sleep):
    x = random.randint(from_sleep, to_sleep)
    for i in tqdm(range(x), desc='sleep ', bar_format='{desc}: {n_fmt}/{total_fmt}'):
        await asyncio.sleep(1)

WALLET_PROXIES  = get_wallet_proxies(WALLETS, PROXIES)