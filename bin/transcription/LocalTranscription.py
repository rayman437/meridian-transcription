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
        self._audio_model = audio_model
        self._text_model = text_model
        
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
        # Add your code here to transcribe the audio locally
        audio_data = whisper.load_audio(file_path)
        transcription = self._whisper_model.transcribe(audio_data)
        
        return transcription['text']

    def summarize_text(self, transcription) -> str:
        """
        Summarizes the transcription of a session.

        Args:
            transcription (str): The transcription of the session.

        Returns:
            str: The summarized version of the transcription.
        """

        logging.info("Sending query to ollama for summarization using following message:\n", self.get_transcription_req(transcription))
        try:
            response = ollama.chat(model=self._text_model, messages=[self._transcription_query, self.get_transcription_req(transcription)])
            logging.info("Response from ollama: ", response)
            return response['message']['content']
        except Exception as e:
            logging.error(e)
            return None
        
    def ask_question(self, question, source_info) -> str:
        messages = [self._question_query, self.get_question_req(question, source_info)]
        logging.info(f"Sending query to ollama for answering question using following messages:\n{messages}")
        try:
            response = ollama.chat(model=self._text_model, messages=messages)
            logging.info("Response from ollama: ", response)
            return response['message']['content']
        except Exception as e:
            logging.error(e)
            return None
  