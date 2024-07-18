import logging
import os

from bin.model.MeridianModel import MeridianModel
from bin.transcription.LocalTranscription import LocalTranscription
from bin.transcription.RemoteTranscription import RemoteTranscription

class MeridianController:
    
    def __init__(self, transcription_service = None):
        
        self.model = None # Handles persistency and historical data
        self.agent = None # Handles transcription and summarization
        self.responses = []
        
        if transcription_service is None:
            # Initialize any necessary variables or resources here
            transcription_service = input("Choose transcription service (Local/Remote): ")
            
        if transcription_service.lower() == "local":
            self.agent = LocalTranscription()
        elif transcription_service.lower() == "remote":
            self.agent = RemoteTranscription()
        else:
            print("Invalid transcription service choice. Defaulting to Local.")
            self.agent = LocalTranscription()
        
        self.model = MeridianModel()
        
    def transcribe_audio(self, audio_file:str, num_speakers:int) -> str:
        # Add your code to transcribe the audio file here
        logging.info("transcribe_audio function called with audio_file: %s", audio_file)
        if os.path.exists(audio_file):
            result = self.agent.transcribe_audio_v2(audio_file, num_speakers)
        else:
            result = None

        return result

    def summarize_session(self, file_path) -> str:
        logging.info("summarize_session function called with file_path: %s", file_path)
        # Add your code to summarize the file here
        with open(file_path, 'r') as file:
            contents = file.read()
            result = self.agent.summarize_text(contents)
        return result
    
    def ask_question(self, question, source_info, num_ctx = 4096):
        logging.info("ask_question function called with question: %s, source_info: %s", question, source_info)
        # Add your code to ask a question here
        response = self.agent.ask_question(question, source_info, num_ctx)
        logging.info("Response: %s", response)
        self.responses.append(response)
        
        return response
    
    def clear_conversation(self):
        logging.info("clear_conversation function called")
        # Add your code to clear the conversation here
        self.agent.clear_chat_responses()
        
    def save_conversation(self, filename):
        logging.info("save_conversation function called with filename: %s", filename)
        # Add your code to save the conversation here
        with open(filename, 'w') as file:
            for response in self.responses:
                file.write(response + "\n")
                
    def save_data(self, filename:str, data:str) -> None:
        logging.info("save_conversation function called with filename: %s", filename)
        # Add your code to save the conversation here
        with open(filename, 'w') as file:
            file.write(data)
    
    def load_data(self, filename:str) -> str:
        logging.info("load_data function called with filename: %s", filename)
        # Add your code to load the data here
        with open(filename, 'r') as file:
            data = file.read()
        
        return data
    
    def save_session(self):
        logging.info("save_session function called with filename: %s", filename)
        # Add your code to save the session here
        self.model.save_session()
    
    def load_campaign(self, filename):
        logging.info("load_campaign function called with filename: %s", filename)
        # Add your code to load the campaign here
        self.model.load_campaign(filename)
    
   
