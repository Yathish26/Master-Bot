user_states = {}

def register_welcome_handler(bot):
    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        response = (
            "Use the Following Commands:\n"
            "/imagecompress - Compress an Image\n"
            "/videotoaudio - Convert Video to Audio\n"
            "/ytdownload - Download any Internet Video"
        )
        bot.reply_to(message, response)
        user_states[message.chat.id] = "waiting_for_input"
        
    @bot.message_handler(func=lambda message: message.text.lower() in ['hi', 'hello'])
    def send_welcome(message):
        response = (
            "Use the Following Commands:\n"
            "/imagecompress - Compress an Image\n"
            "/videotoaudio - Convert Video to Audio\n"
            "/ytdownload - Download any Internet Video"
        )
        bot.reply_to(message, response)
