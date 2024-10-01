import os
from pytube import YouTube
import yt_dlp

user_states = {}

def register_ytdownload_handler(bot):
    @bot.message_handler(commands=['ytdownload'])
    def ytdownload_command(message):
        bot.reply_to(message, "Please send the YouTube link you want to download.")
        bot.send_message(message.chat.id, "You can also send any Link of Video for eg: Instagram, Twitter, or more...")
        user_states[message.chat.id] = "waiting_for_youtube_link"

    @bot.message_handler(content_types=['text']) 
    def handle_text_message(message):
        chat_id = message.chat.id
        if chat_id in user_states and user_states[chat_id] == "waiting_for_youtube_link":
            youtube_link = message.text
            bot.send_message(chat_id, "Checking the link...")
            if validate_youtube_link(youtube_link):
                bot.send_message(chat_id, "Downloading the video...")
                download_youtube_video(bot, chat_id, youtube_link)  # Pass bot to the download function
                del user_states[chat_id]  # Remove the state after processing
            else:
                bot.send_message(chat_id, "No video found at this link. Please send a valid YouTube / Internet Media link.")
                del user_states[chat_id]  # Clear the state if invalid

def validate_youtube_link(link):
    try:
        yt = YouTube(link)
        return True
    except Exception:
        return False

def download_youtube_video(bot, chat_id, youtube_link):  # Add bot as a parameter
    temp_filename = "downloads/temp_video.mp4"
    final_filename = "downloads/final_video.mp4"

    # Define the progress hook inside this function to have access to the bot
    def progress_hook(d):
        if d['status'] == 'downloading':
            percent = d['downloaded_bytes'] / d['total_bytes'] * 100
            bot.send_message(chat_id, f"Downloading... {percent:.2f}%")


    ydl_opts = {
        'format': 'best',
        'outtmpl': temp_filename,
        'progress_hooks': [progress_hook],  # Use the inner function
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(youtube_link, download=True)
            os.rename(temp_filename, final_filename)  # Rename the file
            with open(final_filename, 'rb') as video_file:
                bot.send_video(chat_id, video_file)
        except Exception as e:
            bot.send_message(chat_id, f"Error: {str(e)}")
        finally:
            cleanup_files(temp_filename, final_filename)

def cleanup_files(temp_filename, final_filename):
    # Cleanup temporary and final files
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
