import os
from io import BytesIO
from moviepy.editor import VideoFileClip
import telebot  # Ensure you have this imported to use bot methods

user_states = {}

def register_videotoaudio_handler(bot):
    @bot.message_handler(commands=['videotoaudio'])
    def videotoaudio_command(message):
        bot.reply_to(message, "Please send the video you want to convert to audio.")
        bot.send_message(message.chat.id, "Do not send the video in document format; send the direct video instead.")
        user_states[message.chat.id] = "waiting_for_video"

    @bot.message_handler(content_types=['video', 'document'])  # Directly use 'video' and 'document'
    def handle_video(message):
        chat_id = message.chat.id
        
        # Check if user is in the correct state
        if chat_id in user_states and user_states[chat_id] == "waiting_for_video":
            if message.content_type == 'video':
                video_file = message.video.file_id
            elif message.content_type == 'document':
                # Ensure the document is a video
                if message.document.mime_type.startswith('video/'):
                    video_file = message.document.file_id
                else:
                    bot.reply_to(message, "Please send a valid video file.")
                    return
            
            bot.send_message(chat_id, "Converting video to audio...")
            file_info = bot.get_file(video_file)
            downloaded_file = bot.download_file(file_info.file_path)
            audio_file = convert_video_to_audio(downloaded_file)

            # Send the converted audio file back to the user
            bot.send_document(chat_id, audio_file, caption="Here is your audio file.", visible_file_name="converted_audio.mp3")
            del user_states[chat_id]
        else:
            bot.reply_to(message, "Please use the /videotoaudio command first.")

def convert_video_to_audio(video_data):
    video_path = 'temp_video.mp4'
    audio_path = 'converted_audio.mp3'

    # Save the video data to a temporary file
    with open(video_path, 'wb') as video_file:
        video_file.write(video_data)

    # Convert the video to audio
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path)
    clip.close()  # Close the VideoFileClip to release the file

    audio_byte_array = BytesIO()
    with open(audio_path, 'rb') as audio_file:
        audio_byte_array.write(audio_file.read())

    audio_byte_array.seek(0)

    # Clean up temporary files
    os.remove(video_path)
    os.remove(audio_path)

    return audio_byte_array
