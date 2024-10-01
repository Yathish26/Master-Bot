from PIL import Image
from io import BytesIO
import os

user_states = {}

def register_imagecompress_handler(bot):
    @bot.message_handler(commands=['imagecompress'])
    def imagecompress_command(message):
        bot.reply_to(message, "Please send the image you want to compress.")
        user_states[message.chat.id] = "waiting_for_image"

    @bot.message_handler(content_types=['photo'])
    def handle_image(message):
        chat_id = message.chat.id
        if chat_id in user_states and user_states[chat_id] == "waiting_for_image":
            bot.send_message(chat_id, "Compressing image...")
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            # Since PhotoSize does not have mime_type, we will set it to JPEG by default
            original_format = 'JPEG'  # Default to JPEG

            # Call the compress_image function with the original format
            compressed_image = compress_image(downloaded_file, original_format)
            bot.send_document(chat_id, compressed_image, caption="Here is your compressed image.", visible_file_name=f"compressed_image.{original_format.lower()}")
            del user_states[chat_id]
        else:
            bot.reply_to(message, "Please use the /imagecompress command first to compress an image.")

    @bot.message_handler(content_types=['document'])
    def handle_document(message):
        chat_id = message.chat.id
        if chat_id in user_states and user_states[chat_id] == "waiting_for_image":
            bot.send_message(chat_id, "Compressing image...")
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            # Check the file extension to determine the original format
            file_extension = os.path.splitext(message.document.file_name)[1].lower()
            if file_extension in ['.jpg', '.jpeg', '.png']:
                original_format = file_extension[1:].upper()  # Get 'PNG' or 'JPEG'
                compressed_image = compress_image(downloaded_file, original_format)
                bot.send_document(chat_id, compressed_image, caption="Here is your compressed image.", visible_file_name=f"compressed_image.{original_format.lower()}")
                del user_states[chat_id]
            else:
                bot.reply_to(message, "Please upload a valid image (JPG, JPEG, or PNG).")
        else:
            bot.reply_to(message, "Please use the /imagecompress command first to compress an image.")

def compress_image(image_data, original_format):
    img = Image.open(BytesIO(image_data))
    img_byte_array = BytesIO()

    if original_format.lower() == 'png':
        # For PNG, save it directly and optimize it
        img.save(img_byte_array, format='PNG', optimize=True)
        
        # Compress PNG until the size is under 1MB
        while img_byte_array.tell() > 1 * 1024 * 1024:
            img_byte_array.seek(0)
            img_byte_array.truncate(0)
            # Try to save it again with optimization (may not always reduce size significantly)
            img.save(img_byte_array, format='PNG', optimize=True)
    else:
        # For JPEG, start with initial quality
        quality = 85
        img.save(img_byte_array, format='JPEG', optimize=True, quality=quality)

        # Compress until the size is under 1MB
        while img_byte_array.tell() > 1 * 1024 * 1024:
            img_byte_array.seek(0)
            img_byte_array.truncate(0)
            quality -= 5
            img.save(img_byte_array, format='JPEG', optimize=True, quality=quality)

    img_byte_array.seek(0)
    return img_byte_array
