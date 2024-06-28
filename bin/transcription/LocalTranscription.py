import logging
from bin.transcription.BaseTranscription import BaseTranscription
import whisper
import ollama

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
        self.audo_model = audio_model
        self.text_model = text_model
        
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
        
        self.model = whisper.load_model(selected_model, device='cuda')
        
    def transcribe_audio(self, file_path) -> str:
        """
        Transcribes the audio file located at the specified file path.

        Args:
            file_path (str): The path to the audio file.

        Returns:
            str: The transcription of the audio file.
        """
        # Add your code here to transcribe the audio locally
        audio_data = whisper.load_audio(file_path)
        transcription = self.model.transcribe(audio_data)
        
        return transcription

    def summarize_text(self, transcription_file) -> str:
        """
        Summarizes the transcription of a session.

        Args:
            transcription (str): The transcription of the session.

        Returns:
            str: The summarized version of the transcription.
        """
        # Add your code here to summarize the transcription
        transcription = ''
        
        with open(transcription_file, 'r') as file:
            transcription = file.read()
            
        system_query = {
            'role' : 'system',
            'content' : 'You are helping to summarize the events of a Dungeons & Dragons campaign from the given transcript. There are multiple speakers, so try and infer who is speaking if possible'
        }
        
        transcription_req =  {
                'role' : 'user',
                'content' : 'Summarize the following transcription:\n\n ' + transcription
                }    
        print("Sending query to ollama for summarization using following message:\n", transcription_req)
        try:
            response = ollama.chat(model=self.text_model, messages=[transcription_req])
            print("Response from ollama: ", response)
            return response['message']['content']
        except Exception as e:
            logging.error(e)
            return None
  