from handlers.imagecompress import register_imagecompress_handler
# from handlers.textqr import register_textqr_handler
from handlers.videotoaudio import register_videotoaudio_handler
from handlers.ytdownload import register_ytdownload_handler
from handlers.welcome import register_welcome_handler

def register_all_handlers(bot):
    register_welcome_handler(bot)
    # register_textqr_handler(bot)
    register_imagecompress_handler(bot)
    register_videotoaudio_handler(bot)
    register_ytdownload_handler(bot)
    
