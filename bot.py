import os
from dotenv import load_dotenv
import telebot
from io import BytesIO
from PIL import Image
import qrcode
from moviepy.editor import VideoFileClip
from pytube import YouTube
import yt_dlp
import time

# Load environment variables
load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

user_states = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    response = (
        "Use the Following Commands:\n"
        "/textqr - Convert Text to QR Code\n"
        "/imagecompress - Compress an Image\n"
        "/videotoaudio - Convert Video to Audio\n"
        "/ytdownload - Download a YouTube Video"
    )
    bot.reply_to(message, response)

@bot.message_handler(commands=['textqr'])
def textqr_command(message):
    bot.reply_to(message, "Write a link or text word to convert it to a QR code.")
    user_states[message.chat.id] = "waiting_for_input"

@bot.message_handler(commands=['imagecompress'])
def imagecompress_command(message):
    bot.reply_to(message, "Please send the image you want to compress.")
    user_states[message.chat.id] = "waiting_for_image"

@bot.message_handler(commands=['videotoaudio'])
def videotoaudio_command(message):
    bot.reply_to(message, "Please send the video you want to convert to audio.")
    user_states[message.chat.id] = "waiting_for_video"

@bot.message_handler(commands=['ytdownload'])
def ytdownload_command(message):
    bot.reply_to(message, "Please send the YouTube video link.")
    user_states[message.chat.id] = "waiting_for_youtube_link"

@bot.message_handler(content_types=['text'])
def handle_text_message(message):
    chat_id = message.chat.id

    if chat_id in user_states and user_states[chat_id] == "waiting_for_input":
        text = message.text
        qr_image = generate_qr_code(text)
        bot.send_photo(chat_id, qr_image)
        del user_states[chat_id]
    elif chat_id in user_states and user_states[chat_id] == "waiting_for_youtube_link":
        youtube_link = message.text
        bot.send_message(chat_id, "Checking the link...")
        if validate_youtube_link(youtube_link):
            bot.send_message(chat_id, "Downloading the video...")
            download_youtube_video(chat_id, youtube_link)  # Pass chat_id to the download function
            del user_states[chat_id]
        else:
            bot.send_message(chat_id, "No video found at this link. Please send a valid YouTube link.")
            del user_states[chat_id]
    else:
        send_command_list(chat_id)

def send_command_list(chat_id):
    response = (
        "Use the Following Commands:\n"
        "/textqr - Convert Text to QR Code\n"
        "/imagecompress - Compress an Image\n"
        "/videotoaudio - Convert Video to Audio\n"
        "/ytdownload - Download a YouTube Video"
    )
    bot.send_message(chat_id, response)  # Corrected to send_message


@bot.message_handler(content_types=['photo'])
def handle_image(message):
    chat_id = message.chat.id

    if chat_id in user_states and user_states[chat_id] == "waiting_for_image":
        bot.send_message(chat_id, "Compressing image...")

        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        compressed_image = compress_image(downloaded_file)

        bot.send_document(chat_id, compressed_image, caption="Here is your compressed image.", visible_file_name="compressed_image.jpg")
        del user_states[chat_id]
    else:
        bot.reply_to(message, "Please use the /imagecompress command first to compress an image.")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    chat_id = message.chat.id

    if chat_id in user_states:
        if user_states[chat_id] == "waiting_for_image":
            handle_image_document(message)
        elif user_states[chat_id] == "waiting_for_video":
            handle_video(message)
    else:
        bot.reply_to(message, "Please use the /imagecompress or /videotoaudio command first.")

def handle_image_document(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Compressing image...")

    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    compressed_image = compress_image(downloaded_file)

    bot.send_document(chat_id, compressed_image, caption="Here is your compressed image.", visible_file_name="compressed_image.jpg")
    del user_states[chat_id]

@bot.message_handler(content_types=['video'])
def handle_video(message):
    chat_id = message.chat.id

    if chat_id in user_states and user_states[chat_id] == "waiting_for_video":
        bot.send_message(chat_id, "Converting video to audio...")

        file_info = bot.get_file(message.video.file_id)
        if not file_info:
            bot.reply_to(message, "Could not retrieve video file. Please send a valid video.")
            return

        downloaded_file = bot.download_file(file_info.file_path)
        audio_file = convert_video_to_audio(downloaded_file)

        bot.send_document(chat_id, audio_file, caption="Here is your audio file.", visible_file_name="converted_audio.mp3")
        del user_states[chat_id]
    else:
        bot.reply_to(message, "Please use the /videotoaudio command first.")

def generate_qr_code(text):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img_byte_array = BytesIO()
    img.save(img_byte_array, format='PNG')
    img_byte_array.seek(0)
    return img_byte_array

def compress_image(image_data):
    img = Image.open(BytesIO(image_data))
    img_byte_array = BytesIO()

    img_format = 'JPEG' if img.mode in ('RGB', 'RGBA') else 'PNG'

    if img_format == 'PNG':
        img = img.convert('RGB')

    quality = 85
    img.save(img_byte_array, format='JPEG', optimize=True, quality=quality)

    while img_byte_array.tell() > 1 * 1024 * 1024:
        img_byte_array.seek(0)
        img_byte_array.truncate(0)
        quality -= 5
        img.save(img_byte_array, format='JPEG', optimize=True, quality=quality)

    img_byte_array.seek(0)
    return img_byte_array

def convert_video_to_audio(video_data):
    video_path = 'temp_video.mp4'
    audio_path = 'converted_audio.mp3'

    with open(video_path, 'wb') as video_file:
        video_file.write(video_data)

    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path)
    clip.close()  # Close the VideoFileClip to release the file

    audio_byte_array = BytesIO()
    with open(audio_path, 'rb') as audio_file:
        audio_byte_array.write(audio_file.read())

    audio_byte_array.seek(0)

    os.remove(video_path)
    os.remove(audio_path)

    return audio_byte_array

def validate_youtube_link(link):
    try:
        yt = YouTube(link)
        return True
    except Exception:
        return False

def download_youtube_video(chat_id, youtube_link):
    temp_filename = "downloads/temp_video.mp4"
    final_filename = "downloads/final_video.mp4"

    ydl_opts = {
        'format': 'best',
        'outtmpl': temp_filename,
        'progress_hooks': [lambda d: progress_hook(d, chat_id)],  # Pass chat_id to the progress_hook
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(youtube_link, download=True)
            # Wait for any processes to finish (if needed)
            # time.sleep(1)  # Delay to allow file system to settle
            # Rename the file
            os.rename(temp_filename, final_filename)
            # Send the video
            with open(final_filename, 'rb') as video_file:
                bot.send_video(chat_id, video_file)
        except Exception as e:
            bot.send_message(chat_id, f"Error: {str(e)}")
        finally:
            # Cleanup if needed
            if os.path.exists(temp_filename):
                try:
                    os.remove(temp_filename)
                except Exception as e:
                    print(f"Failed to delete temporary file: {temp_filename}. Error: {str(e)}")
            if os.path.exists(final_filename):
                try:
                    os.remove(final_filename)
                except Exception as e:
                    print(f"Failed to delete final file: {final_filename}. Error: {str(e)}")

def progress_hook(d, chat_id):
    if d['status'] == 'downloading':
        percent = d['downloaded_bytes'] / d['total_bytes'] * 100
        bot.send_message(chat_id, f"Downloading... {percent:.2f}%")

# Start the bot
bot.polling()
