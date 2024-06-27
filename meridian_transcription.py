#/usr/bin/env python3

import os
import sys
from openai import OpenAI, APIError
import subprocess
import argparse
from dotenv import load_dotenv
import logging
import threading
import tkinter as tk
import threading
import threading


class MeridianTranscription:
    
    def __init__(self):
        self.client = OpenAI()

    def transcribe_audio(self, file_path):
        
        # Check the file type
        file_extension = os.path.splitext(file_path)[1].lower()
        base_name = os.path.basename(file_path).split('.')[0]
        logging.info("file_extension: %s", file_extension)
        supported_extensions = ['flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm']
        if file_extension[1:] not in supported_extensions:
            logging.info("Error: Unsupported audio file type.")
            sys.exit(1)
        else:
            logging.info(f"File {file_path} has a supported audio file type. Continuing...")
        
        def split_m4a(input_file, segment_time, output_format='m4a'):
            # Construct the ffmpeg command to split the file
            
            file_name = os.path.splitext(input_file)[0].lower()
            
            command = [
                'ffmpeg',
                '-i', input_file,              # Input file
                '-f', 'segment',               # Use the segment muxer
                '-segment_time', str(segment_time),  # Duration of each segment
                '-c', 'copy',                  # Copy the streams without re-encoding
                f'{file_name}_%03d.{output_format}'  # Output file pattern
            ]
            
            logging.info("Running ffmpeg command: %s", command)
            # Execute the command
            subprocess.run(command, check=True)
            
        split_m4a(file_path, 500)
        
        # Extract the directory from file_path
        directory = os.path.dirname(file_path)

        # Find a list of files that start with the name "output_segment" in the current directory
        logging.info("Looking for files starting with %s in the current directory", base_name)
        logging.info("Files in the directory: %s", os.listdir(directory))
        output_files = [file for file in os.listdir(directory) if file.startswith(base_name.lower()) and file.endswith(".m4a")]
        logging.info("Output files: %s", output_files)
            
        # Transcribe each chunk individually
        transcriptions = []
        
        # Create a list to hold the threads
        threads = []

        # Create a semaphore to protect the logging.info call
        logging_semaphore = threading.Semaphore()

        for i, file in enumerate(output_files):
            try:
                logging_semaphore.acquire()  # Acquire the semaphore before logging
                logging.info("Processing segment %d", i)
                logging_semaphore.release()  # Release the semaphore after logging
                
                # Define the function to be executed in the thread
                def process_segment(file, i):
                    transcription = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=open(f"{directory}/{file}", 'rb'),
                        response_format="text",
                        language="en"
                        #prompt="Generate a transcript of the audio file and return a response in English."
                    )
                    logging_semaphore.acquire()  # Acquire the semaphore before logging
                    logging.info("Finished with segment %d", i)
                    logging.info("Response: %s", transcription)
                    logging_semaphore.release()  # Release the semaphore after logging

                    # Append the transcription to the list in a thread-safe way
                    with threading.Lock():
                        transcriptions.append((i, transcription))
                                    
                # Create a new thread for each iteration
                thread = threading.Thread(target=process_segment, args=(file, i))
                threads.append(thread)
                
                # Start the thread
                thread.start()
                
            except APIError as e:
                logging_semaphore.acquire()  # Acquire the semaphore before logging
                logging.error("APIError: Transcription request for chunk %d failed.", i+1)
                logging.error(e)
                logging_semaphore.release()  # Release the semaphore after logging

            except Exception as e:
                logging_semaphore.acquire()  # Acquire the semaphore before logging
                logging.error(e)
                logging_semaphore.release()  # Release the semaphore after logging


        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        sorted_transcriptions = sorted(transcriptions, key=lambda x: x[0])
        sorted_transcriptions = [t[1] for t in sorted_transcriptions]
        logging.info("Transcriptions: %s", sorted_transcriptions)

        # Combine the transcriptions and sort them
        transcribed_text = ' '.join(t[1] for t in sorted_transcriptions)

        return transcribed_text

    def summarize_session(self, transcription):
        # Check if the input is a list of strings, if so, concatenate them
        if isinstance(transcription, list):
            transcription = ' '.join(transcription)
            
        logging.info("Submitting text for summary:\n", transcription)

        role = "You are an assistant helping to summarize the events of a Dungeons and Dragons session"
        role += "There may be multiple speakers - one of whome is the Game Master of the transcript. When possible, try to summarize each character's actions."
        role+= "Summarize the session in a way that is easy to understand and captures the essence of the session."
        
        # Analyze the transcription string and break it into a list of strings that are 128,000 tokens
        transcription_list = []
        max_tokens = 128000
        num_tokens = 0
        current_string = ""

        logging.info(f"Found {len(transcription.split())} tokens in the transcription.")
        for word in transcription.split():
            num_tokens += len(word.split())
            if num_tokens <= max_tokens:
                current_string += word + " "
            else:
                transcription_list.append(current_string.strip())
                current_string = word + " "
                num_tokens = len(word.split())

        # Add the last string to the list
        if current_string:
            transcription_list.append(current_string.strip())
            
        logging.info("Number of segments: ", len(transcription_list))
        # Submit a request to OpenAI's service for summarization
        summary = None
        output_string = ""

        for i in range(len(transcription_list)):
            print(f"Calling OpenAI API for summary of transcription segment {i}")
            try:
                summary = self.client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content" :role},
                        {"role": "user", "content": transcription_list[i]}
                    ]
                )
                print(f"Summary response: {summary}")
                if summary.choices[0].message.role == 'assistant':
                    print("Response for chunk ", i, ":", summary.choices[0].message.content  )
                    output_string += summary.choices[0].message.content + " "
                else:
                    logging.error("Error: Summary request failed.")
                    sys.exit(2)
                    
            except APIError as e:
                logging.error("APIError: Summary request failed.")
                logging.error(e)
                sys.exit(2)
            except Exception as e:
                logging.error(e)
                sys.exit(2)
            print(f"Done with summarization of segment {i}")

        return output_string


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
    parser.add_argument('--summarize_text', action='store_true', help='Summarize the transcribed text')

    # Parse the arguments
    args = parser.parse_args()

    # Create transcription agent and text to be used for transcription
    transcribed_text = None
    agent = MeridianTranscription()

    if args.transcription_audio:
            # Check if the file exists
        if not os.path.isfile(args.transcription_audio):
            logging.error("Error: File does not exist.")
            sys.exit(1)
 
        # Call the transcribe_audio function
        transcribed_text = agent.transcribe_audio(args.transcription_audio)
        
        # Check if transcription is None
        if transcribed_text is None:
            logging.error("Error: Text could not be transcribed.")
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
            logging.error(e)
            sys.exit(1)
            
    else:
        parser.print_help()
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
