from youtube_dl import YoutubeDL
from vtt_to_srt.vtt_to_srt import ConvertFile 
import pysrt
import os
import shutil
from googletrans import Translator
from unidecode import unidecode
import traceback

class Methods:

    # Downloads the vtt formatted subtitles from the video, then converts it to srt formatted subtitles
    def download(self, link):

        print('[ Downloading... ]')

        # Parameters for youtube-dl
        YDL_OPTS = {'writeautomaticsub':'True','skip_download':'True',}
        
        # Downloads video subtitles
        with YoutubeDL(YDL_OPTS) as ydl:
            i = ydl.extract_info(link,download=False)
            video_title = f'{i["title"]}'
            file_name = 'sub.vtt'
            file_name_with_path = f'storage{os.sep}{file_name}'
            ydl.download([link])

            # Renames file
            for file in os.listdir():
                if file.endswith('.vtt'):
                    os.rename(file, file_name)
                    shutil.move(file_name, file_name_with_path)
        
        # Converts vtt to srt subtitles
        convert_file = ConvertFile(file_name_with_path, 'utf-8')
        convert_file.convert()
        os.remove(file_name_with_path)
        file_name_with_path = f'storage{os.sep}sub.srt'

        print('[ Downloading Complete! ]')

        return video_title, file_name_with_path

    # Converts the srt formatted subtitles to plain text
    def transcribe(self, link):

        # Calls download function. [0] is the name of the video, [1] is the name of the subtitles file with path
        sub_info = self.download(link)

        print('[ Converting Text... ]')

        # Converts subtitles to plain text
        subs = pysrt.open(sub_info[1])
        subs_list = []

        for sub in subs:
            subs_list.append(sub.text)
        raw_text = ''.join(subs_list)
        
        cleaned_text = raw_text.replace('  ', '\n')
        cleaned_text = cleaned_text.replace('[ __ ]', '[ Expletive ]')

        # Writes text to file
        with open (f'{sub_info[0]}.txt', 'w') as file:
            file.write(cleaned_text)

        os.remove(sub_info[1])

        return f'{sub_info[0]}.txt'

    # Reads the text file, translates the text, then writes to a new file
    def translate(self, text_file:str, language:str):

        # Reads text file
        with open(text_file, 'r') as file:
            transcript = file.read()
        
        if len(transcript) >= 14999:
            print('Sorry, this file is too large to be translated.')
            return '[No file created]'
        
        # Splits the text into smaller chunks then sends to Google Translate
        translation_text = self.call_translate(text=transcript, language=language)
    
        translated_file = f'[{language.upper()}] {text_file}'
        
        # Writes translated text to file
        with open(translated_file, 'w', encoding="utf-8") as file:
            
            file.write(translation_text)
            
        os.remove(text_file)

        print('[ Translation Complete! ]')

        return translated_file

    # Splits the text into smaller chunks then sends to Google Translate
    def call_translate(self, text, language):
        t = Translator()
        list_of_segments = []
        text_container = []
        new_list_of_segments = []
        num_of_lines = 0

        # If more than 100 lines, splits it up into chunks
        for line in text:
            text_container.append(line)
            if '\n' in line:
                num_of_lines += 1
            if num_of_lines == 100:
                list_of_segments.append(text_container)
                num_of_lines = 0
                text_container = []
        
        if list_of_segments == []:
            list_of_segments.append(text)
        
        print('[ Translating... ]')

        # Joins chunks of text, then translates
        for i in list_of_segments:
            text_segment = ''.join(i)
            translation_output = t.translate(text=text_segment, dest=language)
            translation_text:str = translation_output.text
            new_list_of_segments.append(translation_text)
        
        translated_transcript = ''.join(new_list_of_segments)

        return translated_transcript

    # Runs the program with input prompts
    def run(self):
        link_prompt = input('Enter your YouTube link here: ')
        starting_prompt = input('Would you like to translate the text into another language? Enter "1" for yes, or "2" for no: \n')

        try:
            # If user wants translation, calls translation function with the transcribe function and language input as arguments
            if starting_prompt == '1':
                lang_prompt = input('What Language would you like to translate to? Please use the codes provided in the "Language Codes" file: ')
                print(f'Your file: {self.translate(text_file=self.transcribe(link=link_prompt), language=lang_prompt)}, has been created!')
                input('Press enter to quit.')
            
            # Calls transcribe function with the yt link
            elif starting_prompt == '2':
                print(f'Your file: {self.transcribe(link=link_prompt)}, has been created!')
                input('Press enter to quit.')
            else:
                print('Invalid input.')
                self.run()
        except Exception:
            traceback.print_exc()
            self.run()