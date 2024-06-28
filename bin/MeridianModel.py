from bin.LocalTranscription import LocalTranscription
from bin.RemoteTranscription import RemoteTranscription


class MeridianModel:

    def __init__(self):
        # Initialize any necessary variables or resources here
        transcription_service = input("Choose transcription service (Local/Remote): ")
        if transcription_service.lower() == "local":
            self.agent = LocalTranscription()
        elif transcription_service.lower() == "remote":
            self.agent = RemoteTranscription()
        else:
            print("Invalid transcription service choice. Defaulting to Remote.")
            self.agent = RemoteTranscription()

        self.responses = []

    def summarize_audio(self, file_path:str) -> str:
        # Implement the summarize_session function here

        with open(file_path, 'r') as file:
            contents = file.read()
            result = self.agent.summarize_audio(contents)
        return result


    def transcribe_audio(self, file_path:str) -> str:
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