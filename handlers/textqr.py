import qrcode
from io import BytesIO

user_states = {}

def register_textqr_handler(bot):
    @bot.message_handler(commands=['textqr'])
    def textqr_command(message):
        bot.reply_to(message, "Write a link or text word to convert it to a QR code.")
        user_states[message.chat.id] = "waiting_for_input"

    @bot.message_handler(content_types=['text'])
    def handle_text_message(message):
        chat_id = message.chat.id
        text = message.text

        # Ignore commands (anything that starts with a /)
        if text.startswith('/'):
            return  # Do nothing if it's a command
        
        # Check if the user is in the state for QR code generation
        if chat_id in user_states and user_states[chat_id] == "waiting_for_input":
            qr_image = generate_qr_code(text)
            bot.send_photo(chat_id, qr_image)
            del user_states[chat_id]  # Clear state after processing
        else:
            bot.reply_to(message, "You are not in a state to generate a QR code. Please use the /textqr command first.")

def generate_qr_code(text):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img_byte_array = BytesIO()
    img.save(img_byte_array, format='PNG')
    img_byte_array.seek(0)
    return img_byte_array
