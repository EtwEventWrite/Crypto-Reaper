# Crypto Reaper

A comprehensive stealer based on the entire purpose of stealing crypto wallets and vital crypto information and exfiltrating to a telegram c2/bot using your Token/Chat ID.

## Features

### Crypto Wallet Targeting
- Supports extraction from 12+ cryptocurrency wallets including MetaMask, Exodus, Atomic, Electrum, Phantom, and Coinbase Wallet
- Targets browser extension wallets and desktop applications
- Extracts seed phrases, private keys, keystore files, and wallet configuration data
- Supports hardware wallet software like Ledger Live and Trezor Suite

### Browser Data Extraction
- Compatible with Chrome 127+ app-bound encryption
- Supports Brave, Edge, and other Chromium-based browsers
- Extracts passwords, cookies, and extension data
- Focuses on crypto-related browser storage and sessions

### Advanced Evasion Techniques
- AMSI, ETW, and WLDP bypass capabilities
- Anti-debugging and anti-VM protections
- Sandbox environment detection
- Analysis tool process termination
- Sleep obfuscation and timing checks

### Stealth & Persistence
- Hidden console operation
- Multiple persistence mechanisms
- Fileless execution options
- Startup folder and scheduled task installation

### Exfiltration
- Telegram C2 communication
- Data compression and encryption
- Chunked transfer for large datasets
- Multiple fallback delivery methods

## Educational Purpose

This tool is intended for:
- Red team exercises and penetration testing
- Security research and malware analysis
- Defensive security training
- Educational demonstrations of data extraction techniques

## Legal Notice

This software is provided for educational and authorized security testing purposes only. Users must ensure they have proper authorization before deploying this tool in any environment. The developers are not responsible for misuse of this software.

## Configuration

The tool is highly configurable through the settings.py or just the main builder.py file, allowing users to:
- Enable/disable specific wallet targets
- Configure evasion techniques
- Set persistence options
- Define exfiltration methods
- Adjust detection thresholds

## Requirements

- Python 3.8+
- Windows operating system
- Required dependencies listed in requirements.txt

## Disclaimer

This project demonstrates advanced data extraction capabilities for educational purposes. Always ensure you have explicit permission before testing on any system. Unauthorized use may violate local laws and regulations.
