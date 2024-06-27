
from meridian_transcription import MeridianTranscription
import os

class MeridianModel:
    def __init__(self):
        # Initialize any necessary variables or resources here
        self.agent = MeridianTranscription()
        
        self.responses = []

    def summarize_session(self, file_path:str) -> str:
        # Implement the summarize_session function here
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                contents = file.read()
                result = self.agent.summarize_session(contents)
            return result
        else:
            return "File does not exist"

    def transcribe_session(self, file_path:str) -> str:
        # Implement the summarize_session function here
        if os.path.exists(file_path):
            result = self.agent.transcribe_audio(file_path)
        else:
            result = None
            
        return result
        
    def save_session(self, filename) -> None:
        
        # Implement the save_session function here
        with open(filename, 'w') as file:
            for i, response in enumerate(self.responses):
                file.write(f"{i+1}. {response}\n")
        
    def load_campaign(self, filename) -> None:
        # Implement the load_progress function here
        
        with open(filename, 'r') as file:
            self.responses = [line.strip("%0d+.").strip() for line in file.readlines()]
            
    def get_campaign_info(self) -> list:
        # Implement the get_campaign_info function here
        return self.responses
    
    def save_to_campaign(self, data) -> None:
        # Implement the save_to_campaign function here
        self.responses.append(data)
