

class BaseTranscription:
    
    """
    Base class for audio transcription.
    """

    def __init__(self):
        """
        Initializes a new instance of the BaseTranscription class.
        """
        pass

    def transcribe_audio(self, file_path) -> str:
        """
        Transcribes the audio file located at the specified file path.

        Args:
            file_path (str): The path to the audio file.

        Returns:
            str: The transcription of the audio file.
        """
        pass

    def summarize_text(self, transcription) -> str:
        """
        Summarizes the transcription of a session.

        Args:
            transcription (str): The transcription of the session.

        Returns:
            str: The summarized version of the transcription.
        """
        pass
    
    
