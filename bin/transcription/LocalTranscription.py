import logging
import time
import whisper
import ollama
import json
import torch
import os
import re

from bin.transcription.BaseTranscription import BaseTranscription
from pydub import AudioSegment
from pyannote.audio import Pipeline
from pyannote.core import Segment

class LocalTranscription(BaseTranscription):
    """
    Class for local audio transcription.
    """

    def __init__(self, audio_model = 'small.en', text_model = 'llama3'):
        """
        Initializes a new instance of the LocalTranscription class.
        
        This method initializes the LocalTranscription object by calling the base class's __init__ method.
        It prompts the user to select a whisper model from the available models list and loads the selected model.
        """
        super().__init__()
        self._audio_model = audio_model
        self._text_model = text_model
        self._audio_pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=os.getenv('HF_ACCESS_TOKEN')).to(torch.device("cuda"))

        if self._audio_pipeline is None:
            logging.error("Could not load the speaker diarization pipeline.")
            return
        
        if audio_model not in whisper.available_models():
            available_models = whisper.available_models()
            selected_model = ""

            # Ask the user to select models from the available models list
            print("Available models:")
            for i, audio_model in enumerate(available_models):
                print(f"{i+1}. {audio_model}")

            while True:
                model_index = input("Select a model (enter the corresponding number) or press 'q' to quit: ")
                if model_index == 'q':
                    break
                try:
                    model_index = int(model_index)
                    if 1 <= model_index <= len(available_models):
                        selected_model = available_models[model_index-1]
                        print(f"Selected model: {selected_model}")
                        break
                    else:
                        print("Invalid model index. Please try again.")
                except ValueError:
                    print("Invalid input. Please try again.")
        else:
            selected_model = audio_model
        self._whisper_model = whisper.load_model(selected_model, device='cuda')
        
    def transcribe_audio(self, file_path) -> str:
        """
        Transcribes the audio file located at the specified file path.

        Args:
            file_path (str): The path to the audio file.

        Returns:
            str: The transcription of the audio file.
        """
        
        def millisec(val: float ) -> int:

            logging.info(f"Time: {val}")
            return int(val * 1000.0)
      
        # apply pretrained pipeline for diarization
        def get_audiosegment(_file_path):
            temp_filename = _file_path
            file_extension = os.path.splitext(temp_filename)[1][1:]
            start_time = time.time()
            logging.info(f"Loading audio file: {temp_filename}")
            audio = AudioSegment.from_file(temp_filename, format=file_extension)
            logging.info(f"Done loading audio file: {temp_filename}. Time to load: {(time.time() - start_time):.3f}")
            
            # Diarization requires the audio to be in .wav format - convert if necessary
            if file_extension != 'wav':
                temp_filename = os.path.splitext(temp_filename)[0] + '.wav'
                logging.info(f"Converting file from {file_extension} to .wav format. File: {temp_filename}")
                start_time = time.time()
                audio.export(temp_filename, format='wav')
                logging.info(f"Done converting file to .wav format. File: {temp_filename}. Time to transcribe: {(time.time() - start_time):.3f}")
                
            # Return handle to both AudioSegment and the filename of the audio file    
            return (temp_filename, audio)
        
        (diarization_filename, audio) = get_audiosegment(file_path)
        
        diarization_json = os.path.splitext(diarization_filename)[0] + '_diarization.json'
        logging.info(f"Checking if diarization file exists: {diarization_json}")
       
        groups = None
        if os.path.exists(diarization_json):
            logging.info(f"File exists - attempt to load file")
            try:
                logging.info(f"Loading diarization from file: {diarization_json}")
                with open(diarization_json, 'r') as f:
                    groups = json.loads(f.read())
                logging.info(f"Loaded diarization from file: {diarization_json}")
            except Exception as e:
                logging.error(e)
                # Remove diariazation file if it exists
                if os.path.exists(diarization_json):
                    logging.info(f"Removing diarization file: {diarization_json}")
                    os.remove(diarization_json)
                    
                return "Could not load diarization. Please try again."
        
        else:
            logging.info(f"File does not exist - attempt to diarize audio file")
            try:
                start_time = time.time()
                logging.info(f"Begin diarizing audio file: {diarization_filename}")
                diarization = self._audio_pipeline(diarization_filename)
                # Write diarization to a file
                logging.info(f"Finished diarizing audio file: {file_path}. Time to transcribe: {(time.time() - start_time):.3f}")
                logging.info(f"Type of diarization: {type(diarization)}")
            
                groups = { speaker : [] for speaker in diarization.labels()}
                logging.info(f"List of speakers: {groups.keys()}")
                # return type:  Iterator[Union[Tuple[Segment, TrackName], Tuple[Segment, TrackName, Label]]]
                for i, track_data in enumerate(diarization.itertracks(yield_label=True)):
                    for i, datum in enumerate(track_data):
                        logging.info(f"Speaker[{i}]: {datum}")

                    start = track_data[0].start
                    end = track_data[0].end
                    speaker_id = track_data[2]
                    logging.info(f"Speaker: {speaker_id} - Start: {start} - End: {end}")
                    groups[speaker_id].append({"start":start, "end": end})
        
                logging.info(f"Writing speaker diarization info to {diarization_json}")
                for speaker, times in groups.items():
                    with open(diarization_json, 'w') as f:
                        f.write(json.dumps(groups))
                logging.info(f"Speaker diarization info written to file: {diarization_json}")

            except Exception as e:
                logging.error(e)                    
                return "Could not transcribe audio. Please try again."
        
        gidx = -1
        speaker_dict = {}
        filenames = [] 
        
        if not os.path.exists(os.path.curdir + r'\tmp'):
            logging.info(f"Making temporary directory for audio files: {os.path.curdir + r'\tmp'}")
            os.makedirs(os.path.curdir + r'\tmp')
            logging.info(f"Done making temporary directory for audio files")

            
        for speaker, time_list in groups.items():
            logging.info(f"Processing speaker {speaker}")
            for seg in time_list:
                logging.info(f"Time tuple: {seg}")
                start = seg['start']
                end = seg['end']
                gidx +=1
                tmp_filename = 'tmp/' + str(gidx) + '.wav'
                speaker_dict[gidx] = speaker

                try:
                    audio[millisec(start):millisec(end)].export(tmp_filename, format='wav')
                    filenames.append(tmp_filename)
                except Exception as e:
                    logging.error(e)
                    logging.error(f"Could not export audio file: {tmp_filename} for times {start} to {end}.")
        
        # Now that we have the diarization, do the transcription
        start_time = time.time()
        transcription = []
        logging.info(f"Begin transcribing audio files for {file_path}")
        gidx = 0
        idx_len = len(filenames)
        for tmpfile in filenames:
            logging.info(f"Transcribing audio file {tmpfile} for idx {gidx} of {idx_len}")
            start_time = time.time()
            audio_data = whisper.load_audio(tmpfile)
            segment_transcription = self._whisper_model.transcribe(
                audio_data)
            logging.info(f"Done transcribing audio {tmpfile}. Time to transcribe: {(time.time() - start_time):.3f}")
            transcription.append(f"Speaker {speaker_dict[gidx]}: {segment_transcription['text']}")
            gidx +=1
            
        logging.info(f"Finished transcribing audio files for {file_path}. Time to transcribe: {(time.time() - start_time):.3f}")
                
        return "\n".join(transcription)
        

    def summarize_text(self, transcription) -> str:
        """
        Summarizes the transcription of a session.

        Args:
            transcription (str): The transcription of the session.

        Returns:
            str: The summarized version of the transcription.
        """
        
        transcription_req = f"Summarize the following transcription of a Dungeons and Dragons campagin session: \n\n{transcription}"
        logging.info(f"Sending query to ollama for summarization using following message:\n {transcription_req}")
        try:
            response = ollama.generate(model=self._text_model, prompt=transcription_req)
            logging.info(f"Response from ollama: {response}")
            return response['response']
        except Exception as e:
            logging.error(e)
            return None
        
    def ask_question(self, question, source_info) -> str:
        answer = ""
        if self.chat_responses is None:
            logging.info("Chat responses cleared - reinitializing with contents of transcription window.")
            self.chat_responses = [{"role" : "assistant", 
                                "content" : "You're helping to answer a question about a Dungeons & Dragons campaign."},
                                {"role" : "system",
                                "content" : f'''Please provide a detailed response based on the information in this transcript
                                
{source_info} 
                                
                                             
Any responses that you give should be based on the information in the transcript and the conversation with the user. If you need more information, please ask for it.'''}]
        
        self.chat_responses.append({"role" : "user", "content" : question})
        
        logging.debug(f"Query:\n\n {question}")
        logging.debug(f"Current responses:\n\n {self.chat_responses}")
        
        try:
            logging.info(f"Attempting to send query to ollama for question analysis: {question}")
            responses = ollama.chat(
                messages=self.chat_responses,
                model=self._text_model,
                stream = True)
            for response in responses:
                if not response['done']:
                    self.chat_responses.append({"role": "assistant",
                                                "content": response['message']['content']})
                    answer+=response['message']['content']
                else:
                    break
            logging.debug(f"Response from ollama: {answer}")
            return answer
        
        except Exception as e:
            logging.error(e)
            return "Query failed - please try again."
    
