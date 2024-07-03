from bin.transcription.LocalTranscription import LocalTranscription
from bin.transcription.RemoteTranscription import RemoteTranscription

import os
import json

class MeridianModel:

    def __init__(self, transcription_service = None):
        
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

        self.responses = []

    def summarize_audio(self, file_path:str) -> str:
        # Implement the summarize_session function here

        with open(file_path, 'r') as file:
            contents = file.read()
            result = self.agent.summarize_text(contents)
        return result


    def transcribe_audio(self, file_path:str, num_speakers: int) -> str:
        # Implement the summarize_session function here
        if os.path.exists(file_path):
            result = self.agent.transcribe_audio_v2(file_path, num_speakers)
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
        
    def ask_question(self, question, source_info) -> str:
        # Implement the ask_question function here
        return self.agent.ask_question(question, source_info)
    
    def clear_conversation(self):
        return self.agent.clear_chat_responses()

    def save_conversation(self, file_path:str):
        # Access the chat_responses variable in the agent
        chat_responses = self.agent.chat_responses

        # Save chat_responses in JSON format to the specified file_path
        with open(file_path, 'w') as file:
            json.dump(chat_responses, file)