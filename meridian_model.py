
from meridian_transcription import MeridianTranscription
import os

class MeridianModel:
    def __init__(self):
        # Initialize any necessary variables or resources here
        self.agent = MeridianTranscription()

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
            with open(file_path, 'r') as file:
                contents = file.read()
                result = self.agent.transcribe_audio(contents)
            return result
        else:
            return "File does not exist"
