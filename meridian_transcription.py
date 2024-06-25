#/usr/bin/env python3

import os
import sys
from openai import OpenAI, APIError
from pydub import AudioSegment
import subprocess
import argparse
from dotenv import load_dotenv
import logging

class meridian_transcription:
    
    def __init__(self):
        self.client = OpenAI()

    def transcribe_audio(self, file_path):
        
        # Check the file type
        file_extension = os.path.splitext(file_path)[1].lower()
        logging.info("file_extension: %s", file_extension)
        supported_extensions = ['flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm']
        if file_extension[1:] not in supported_extensions:
            logging.info("Error: Unsupported audio file type.")
            sys.exit(1)
        
        def split_m4a(input_file, segment_time, output_format='m4a'):
            # Construct the ffmpeg command to split the file
            command = [
                'ffmpeg',
                '-i', input_file,              # Input file
                '-f', 'segment',               # Use the segment muxer
                '-segment_time', str(segment_time),  # Duration of each segment
                '-c', 'copy',                  # Copy the streams without re-encoding
                f'output_segment_%03d.{output_format}'  # Output file pattern
            ]
            
            # Execute the command
            subprocess.run(command, check=True)
            
        split_m4a(file_path, 500)

        # Find a list of files that start with the name "output_segment" in the current directory
        output_files = [file for file in os.listdir() if file.startswith("output_segment")]
            
        # Transcribe each chunk individually
        transcriptions = []
        
        for i, file in enumerate(output_files):
            try:
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=open(file, 'rb'),
                    response_format="text"
                )
                logging.info("Finished with segment %d", i+1)
                
                logging.info("Response: %s", transcription)
                with open(f"{file}_{i}_transcription.txt", "w") as f:
                    # Write the transcription to the file
                    f.write(transcription)

                transcriptions.append(transcription)
            except APIError as e:
                logging.info("APIError: Transcription request for chunk %d failed.", i+1)
                logging.info(e)
            except Exception as e:
                logging.info(e)

        # Combine the transcriptions
        transcribed_text = ' '.join(transcriptions)

        return transcribed_text

    def summarize_session(self, transcription):
        # Check if the input is a list of strings, if so, concatenate them
        if isinstance(transcription, list):
            transcription = ' '.join(transcription)
            
        print("Submitting text for summary:\n", transcription)

        prompt = "Summarize the following text: \n\n" + transcription + "\n\n"
        prompt+= "There may be multiple speakers - one of whome is the Game Master of the transcript, which comes from a Dungeons and Dragons session. When possible, try to summarize each character's actions. \n\n"
        prompt+= "Summarize the session in a way that is easy to understand and captures the essence of the session."
        
        # Submit a request to OpenAI's service for summarization
        summary = None
        try:
            summary = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content" :"You are an assistant helping to summarize the events of a Dungeons and Dragons session"},
                    {"role": "user", "content": prompt}
                ]
            )
            if summary['choices'][0]['message']['role'] == 'assistant':
                print("Got response:\n", summary)
            else:
                logging.info("Error: Summary request failed.")
                #sys.exit(2)
                
        except APIError as e:
            logging.info("APIError: Summary request failed.")
            logging.info(e)
            sys.exit(2)
        except Exception as e:
            logging.info(e)
            sys.exit(2)
            
        return summary['choices'][0]['message']['content']


def main():
    # Create an argument parser
    parser = argparse.ArgumentParser(description='Transcribe audio file.')

    # Add the filename argument
    parser.add_argument('--transcription_audio', type=str, help='Path to the audio file')
    parser.add_argument('--transcription_text', type=str, help='Path to the text file of a previously processed session')
    parser.add_argument('--summarize_text', action='store_true', help='Summarize the transcribed text')

    # Parse the arguments
    args = parser.parse_args()

    # Create transcription agent and text to be used for transcription
    transcribed_text = None
    agent = meridian_transcription()

    if args.transcription_audio:
            # Check if the file exists
        if not os.path.isfile(args.transcription_audio):
            logging.info("Error: File does not exist.")
            sys.exit(1)
 
        # Call the transcribe_audio function
        transcribed_text = agent.transcribe_audio(args.transcription_audio)
        
        # Check if transcription is None
        if transcribed_text is None:
            logging.info("Error: Text could not be transcribed.")
            sys.exit(1)

        # Output the transcription to a text file
        with open('transcription.txt', 'w') as text_file:
            text_file.write(transcribed_text)
            
    elif args.transcription_text :
        
        # Read in the transcription text file
        try:
            with open(args.transcription_text, 'r') as f:
                transcribed_text = f.read()
        except Exception as e:
            logging.info(e)
            sys.exit(1)
            
    else:
        logging.error("No transcription file or audio file provided - exiting.")
        sys.exit(2)

    # Read in all of the files that start with 
    # output_segment and end with transcription.txt 
    # and add it to a signle text file    
    if args.summarize_text:
        summary = agent.summarize_session(transcribed_text)
        
        print(summary)
        # Write out the summary to a text file
        open("summary.txt", "w").write(summary)

    
if __name__ == '__main__':
    load_dotenv()
    logging.info("API Key: %s", os.getenv('OPENAI_API_KEY'))
    main()
