# python3

import os
import sys
import argparse
from dotenv import load_dotenv
import logging
import time

from bin.transcription.LocalTranscription import LocalTranscription
from bin.transcription.RemoteTranscription import RemoteTranscription
from bin.gui.MeridianGUI import MeridianGUI

def main():

    # Create an argument parser
    parser = argparse.ArgumentParser(description='Transcribe audio file.')
        
    # Add the filename argument
    parser.add_argument('--transcription_audio', type=str, help='Path to the audio file')
    parser.add_argument('--local', action='store_true', help='Use local transcription service')
    parser.add_argument('--remote', action='store_true', help='Use remote transcription service')
    parser.add_argument('--summarize_text', type=str, help='Summarize the text in the given file')
    parser.add_argument('--output_file', type=str, help='Path to the output file')
    parser.add_argument("--gui", action="store_true", help="Don't launch the GUI", default=True)

    # Parse the arguments
    args = parser.parse_args()

    # Create transcription agent and text to be used for transcription
    transcribed_text = None
    agent = None
    
    if args.output_file:
        output_filename = args.output_file
    else:
        output_filename = "transcription.txt"

    if args.gui:
           
        app = MeridianGUI()
        
    elif args.transcription_audio or args.summarize_text:
        
        if not args.local and not args.remote:    
            transcription_service = input("Choose transcription service (Local/Remote): ")
            if transcription_service.lower() == "local":
                agent = LocalTranscription()
            elif transcription_service.lower() == "remote":
                agent = RemoteTranscription()
            else:
                print("Invalid transcription service choice. Defaulting to Local.")
                agent = LocalTranscription()
        elif args.local:
            agent = LocalTranscription()
        elif args.remote:
            agent = RemoteTranscription()
            
            
        if args.transcription_audio:
            
            # Check if the file exists
            if not os.path.isfile(args.transcription_audio):
                logging.error("Error: File does not exist.")
                sys.exit(1)
                
            transcription_service = ""
            
            # Call the transcribe_audio function
            logging.info(f"Transcribing audio file... {args.transcription_audio}")
            
            start_time = time.time()
            transcribed_text = agent.transcribe_audio(args.transcription_audio)
            end_time = time.time()

            execution_time = end_time - start_time
            logging.info(f"Transcription completed in {str(execution_time)} seconds.")
            
            # Check if transcription is None
            if transcribed_text is None:
                logging.error("Error: Text could not be transcribed.")
                sys.exit(1)

            # Output the transcription to a text file            
            with open(output_filename, 'w') as text_file:
                text_file.write(transcribed_text['text'])
                
        elif args.summarize_text:
            
            logging.info(f"Beginning text summary for {args.summarize_text}")
            start_time = time.time()
            summary = agent.summarize_text(args.summarize_text)
            end_time = time.time()

            execution_time = end_time - start_time
            logging.info(f"Text summarization completed in {str(execution_time)} seconds.")
            
            print(summary)
            # Write out the summary to a text file
            open(output_filename, "w").write(summary)        
    else:
        parser.print_help()
        sys.exit(1)
    
if __name__ == '__main__':
    
    # Load .env file which has the OpenAI key
    load_dotenv()
    
    # Configure the logging package
    #current_time = time.strftime("%Y%m%d-%H%M%S")
    log_filename = "log.txt"
    debug_filename = "debug.txt"
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler(sys.stdout)
    ])
    
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
        logging.FileHandler(debug_filename),
    ])
    logging.debug("API Key: %s", os.getenv('OPENAI_API_KEY'))
    
    main()
