
from openai import APIError, OpenAI
import logging
import os
import subprocess
import sys
import threading
from bin.transcription.BaseTranscription import BaseTranscription

class RemoteTranscription(BaseTranscription):
    """
    A class that handles remote audio transcription using OpenAI API.

    Attributes:
        client (OpenAI): An instance of the OpenAI client.

    Methods:
        transcribe_audio(file_path): Transcribes the audio file located at the given file path.
        summarize_session(transcription): Summarizes the transcription of a session.
    """

    def __init__(self):
        """
        Initializes the RemoteTranscription object.
        """
        self.client = OpenAI()

    def transcribe_audio(self, file_path) -> str:
        """
        Transcribes the audio file located at the given file path.

        Args:
            file_path (str): The path to the audio file.

        Returns:
            str: The transcribed text.
        """
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
            """
            Splits the given M4A audio file into segments.

            Args:
                input_file (str): The path to the input audio file.
                segment_time (int): The duration of each segment in seconds.
                output_format (str, optional): The format of the output files. Defaults to 'm4a'.
            """
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
                    """
                    Transcribes a segment of the audio file.

                    Args:
                        file (str): The path to the segment file.
                        i (int): The index of the segment.

                    """
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

    def summarize_text(self, transcription) -> str:
        """
        Summarizes the transcription of a session.

        Args:
            transcription (str or list): The transcription of the session, either as a single string or a list of strings.

        Returns:
            str: The summarized text.
        """
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