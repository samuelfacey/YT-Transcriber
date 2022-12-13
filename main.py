from youtube_dl import YoutubeDL
from youtube_dl.utils import DownloadError
import traceback
import os
import pathlib
import shutil
import asyncio

async def download(link):

    YDL_OPTS = {'audioformat':'mp3', 'format': 'bestaudio/best','noplaylist':'True', 'outtml':'/static/storage/song', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192' }],'default_search':'auto', 'nocheckcertificates':'true'}
    
    with YoutubeDL(YDL_OPTS) as ydl:
        i = ydl.extract_info(link,download=False)
        old_file_name = i['title']
        try:
            os.remove(f"storage\{old_file_name}.mp3")
        except:
            pass
        ydl.download([link])
        new_file_name = f"{old_file_name}.mp3"
        for file in os.listdir():
            if file.endswith(f'.mp3'):
                os.rename(file, new_file_name)
                shutil.move(new_file_name, f'storage\{new_file_name}')
    
    return new_file_name


link = input('Paste your link here: ')

asyncio.run(download(link=link))