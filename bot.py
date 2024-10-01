import os
import time
from dotenv import load_dotenv
import telebot
from register_handlers import register_all_handlers

# Load environment variables
load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Register all handlers
register_all_handlers(bot)

# Start the bot
if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)  # This will keep polling
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(5)  # Wait for 5 seconds before restarting the polling
