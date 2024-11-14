import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv
import ccxt

# Load and encrypt Telegram API token
from cryptography.fernet import Fernet
import base64

def get_or_create_key():
    key_file = 'secret.key'
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, 'wb') as f:
            f.write(key)
        return key

def encrypt_token(token: str, key: bytes) -> str:
    f = Fernet(key)
    return f.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(encrypted_token.encode()).decode()

# Get encryption key
key = get_or_create_key()

# Load and encrypt token from env
load_dotenv()
raw_token = os.getenv('Telegram_API_Token')
TOKEN = decrypt_token(encrypt_token(raw_token, key), key)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class CryptoBinaryBot:
    def __init__(self):
        self.exchange = ccxt.binance()
        self.active_bets = {}  # Store active bets: user_id -> bet_details
        self.user_balances = {}  # Store user balances: user_id -> balance

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler for /start command"""
        keyboard = [
            [InlineKeyboardButton(
                "Start Trading", 
                web_app=WebAppInfo(url="YOUR_WEBAPP_URL_HERE")
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_message = (
            "🎯 Welcome to Crypto Binary Options Bot!\n\n"
            "Make predictions on crypto price movements and win rewards!\n"
            "• Predict if price goes UP or DOWN in 30 seconds\n"
            "• Win 1.5x your bet amount on correct predictions\n"
            "• Start with /trade to begin trading"
        )
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def main():
    """Start the bot"""
    app = Application.builder().token(TOKEN).build()
    
    bot = CryptoBinaryBot()
    
    # Add handlers
    app.add_handler(CommandHandler("start", bot.start))
    
    # Start the bot
    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main()) 