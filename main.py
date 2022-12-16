from youtube_dl import YoutubeDL
from vtt_to_srt.vtt_to_srt import ConvertFile 
import pysrt
import os
import shutil
from googletrans import Translator
from unidecode import unidecode

def download(link):

    YDL_OPTS = {'writeautomaticsub':'True','skip_download':'True',}
    
    with YoutubeDL(YDL_OPTS) as ydl:
        i = ydl.extract_info(link,download=False)
        video_title = f'{i["title"]}'
        file_name = 'sub.vtt'
        file_name_with_path = f'storage{os.sep}{file_name}'
        ydl.download([link])
        for file in os.listdir():
            if file.endswith('.vtt'):
                os.rename(file, file_name)
                shutil.move(file_name, file_name_with_path)
        
    convert_file = ConvertFile(file_name_with_path, 'utf-8')
    convert_file.convert()
    os.remove(file_name_with_path)
    file_name_with_path = f'storage{os.sep}sub.srt'

    return video_title, file_name_with_path


def transcribe(link):

    sub_info = download(link)

    subs = pysrt.open(sub_info[1])
    subs_list = []

    for sub in subs:
        subs_list.append(sub.text)
    raw_text = ''.join(subs_list)
    
    cleaned_text = raw_text.replace('  ', '\n')
    cleaned_text = cleaned_text.replace('[ __ ]', '[ Expletive ]')

    with open (f'{sub_info[0]}.txt', 'w') as file:
        file.write(cleaned_text)

    os.remove(sub_info[1])

    return f'{sub_info[0]}.txt'


def translate(text_file:str, lang:str, encoding:str):

    t = Translator()
    with open(text_file, 'r') as file:
        transcript = file.read()
    
    if len(transcript) >= 14999:
        print('Sorry, this file is too large to be translated.')
        return '[No file created]'
    
    translation_output = t.translate(text=transcript, dest=lang)
    translation_text:str = translation_output.text
  
    translated_file = f'[{lang.upper()}] {text_file}'
    
    with open(translated_file, 'w') as file:
        if encoding == '2':
            file.write(unidecode(translation_text))
        else:
            file.write(translation_text)
        
    os.remove(text_file)
    return translated_file
    

def run():
    link = input('Enter your YouTube link here: ')
    starting_prompt = input('Would you like to translate the text into another language? 1: Yes, 2: No\n')

    try:
        if starting_prompt == '1':
            lang_prompt = input('What Language would you like to translate to? ')
            encoding_prompt = input('Would you like to keep the accented characters? May not work properly on english devices. 1: Yes, 2: No\n')
            print(f'Your file: {translate(text_file=transcribe(link=link), lang=lang_prompt, encoding=encoding_prompt)}, has been created!')
            input('Press enter to quit.')
        elif starting_prompt == '2':
            print(f'Your file: {transcribe()}, has been created!')
            input('Press enter to quit.')
        else:
            print('Invalid input.')
            run()
    except Exception as e:
        print(e)
        run()

if __name__ == '__main__':
    run()