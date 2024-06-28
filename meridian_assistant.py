# python3

import os
import sys
import argparse
from dotenv import load_dotenv
import logging
import tkinter as tk

from bin.LocalTranscription import LocalTranscription
from bin.RemoteTranscription import RemoteTranscription
from bin.meridian_gui import MeridianGUI
import time

def main():

    # Create an argument parser
    parser = argparse.ArgumentParser(description='Transcribe audio file.')
    
    # Configure the logging package
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
        logging.FileHandler('log.txt'),
        logging.StreamHandler()
    ])
    
    # Add the filename argument
    parser.add_argument('--transcription_audio', type=str, help='Path to the audio file')
    parser.add_argument('--transcription_text', type=str, help='Path to the text file of a previously processed session')
    parser.add_argument('--local', action='store_true', help='Use local transcription service')
    parser.add_argument('--remote', action='store_true', help='Use remote transcription service')
    parser.add_argument('--summarize_text', action='store_true', help='Summarize the transcribed text')
    parser.add_argument("--gui", action="store_true", help="Launch the GUI")

    # Parse the arguments
    args = parser.parse_args()

    # Create transcription agent and text to be used for transcription
    transcribed_text = None
    agent = None

    if args.gui:
           
        app = MeridianGUI()
        
    if args.transcription_audio:
            # Check if the file exists
        if not os.path.isfile(args.transcription_audio):
            logging.error("Error: File does not exist.")
            sys.exit(1)
            
        transcription_service = ""
        
        if not args.local and not args.remote:    
            transcription_service = input("Choose transcription service (Local/Remote): ")
            if transcription_service.lower() == "local":
                agent = LocalTranscription()
            elif transcription_service.lower() == "remote":
                agent = RemoteTranscription()
            else:
                print("Invalid transcription service choice. Defaulting to Remote.")
                agent = RemoteTranscription()
        elif args.local:
            agent = LocalTranscription()
        elif args.remote:
            agent = RemoteTranscription()
 
        # Call the transcribe_audio function
        start_time = time.time()
        transcribed_text = agent.transcribe_audio(args.transcription_audio)
        end_time = time.time()

        execution_time = end_time - start_time
        print(f"Transcription completed in {str(execution_time)} seconds.")
        
        print("Transcribed text:\n\n" , transcribed_text)
        
        # Check if transcription is None
        if transcribed_text is None:
            logging.error("Error: Text could not be transcribed.")
            sys.exit(1)

        # Output the transcription to a text file
        with open('transcription.txt', 'w') as text_file:
            text_file.write(transcribed_text['text'])
            
    elif args.transcription_text :
        
        # Read in the transcription text file
        try:
            with open(args.transcription_text, 'r') as f:
                transcribed_text = f.read()
        except Exception as e:
            logging.error(e)
    else:
        parser.print_help()
        sys.exit(1)


    # Read in all of the files that start with 
    # output_segment and end with transcription.txt 
    # and add it to a signle text file    
    if args.summarize_text:
        summary = agent.summarize_audio(transcribed_text)
        
        print(summary)
        # Write out the summary to a text file
        open("summary.txt", "w").write(summary)

    
if __name__ == '__main__':
    load_dotenv()
    logging.info("API Key: %s", os.getenv('OPENAI_API_KEY'))
    main()
