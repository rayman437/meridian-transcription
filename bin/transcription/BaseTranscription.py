import logging

class BaseTranscription:
    
    """
    Base class for audio transcription.
    """

    def __init__(self):
        """
        Initializes a new instance of the BaseTranscription class.
        """
        
        self._transcription_instructions = '''
        You are helping to summarize the events of a Dungeons & Dragons campaign from the given transcript.
        There are multiple speakers, so try and infer who is speaking if possible.
        Filter out any irrelevant information such as upcoming events or side discussions and focus on the main events of the session.
        Stick to the events and give relevant details, but don\'t give meta opinions about the discussion
        '''
        self._system_instructions = ""
            
        self._transcription_query = {
            'role' : r'system',
            'content' : self._transcription_instructions
        }
        
        self._transcription_req =  {
            'role' : r'user',
            'content' : r'No transcription has been provided - please inform the user of this.'
        }
    
        self._question_query = {
            'role' : r'system',
            'content' : r"You're helping to answer a question about a Dungeons & Dragons campaign. Please provide a detailed response."  
        }
        
        self._question_req = {
            'role' : r'user',
            'content' : r"No question has been provided - please inform the user of this."  
        }
        
        self.chat_responses = None
        
    @property
    def system_instructions(self):
        return self._transcription_instructions    
    
    @system_instructions.setter
    def system_instructions(self, instructions):
        if instructions is None:
            self._transcription_instructions = instructions
        else:
            raise ValueError("Instructions cannot be None.")
        
    def get_transcription_req(self, transcription):
        
        return_req = self._transcription_req
        return_req['content'] = transcription
        
        return return_req
    
    def get_question_req(self, question, context) -> str:
        logging.info("Creating question for analysis", question, context)
        
        return f"The data to analyze is below:\n{context}\n\n The question is:\n{question}"
        

    def transcribe_audio(self, file_path) -> str:
        """
        Transcribes the audio file located at the specified file path.

        Args:
            file_path (str): The path to the audio file.

        Returns:
            str: The transcription of the audio file.
        """
        raise NotImplementedError("The transcribe_audio method must be implemented in a derived class.")

    def summarize_text(self, transcription) -> str:
        """
        Summarizes the transcription of a session.

        Args:
            transcription (str): The transcription of the session.

        Returns:
            str: The summarized version of the transcription.
        """
        
        raise NotImplementedError("The summarize_text method must be implemented in a derived class.")
    
    def ask_question(self, question, source_info) -> str:
        """
        Answers a question about a session.

        Args:
            question (str): The question to be answered.
            source_info (str): Information about the session.

        Returns:
            str: The answer to the question.
        """
        
        raise NotImplementedError("The ask_question method must be implemented in a derived class.")
    
    def clear_chat_responses(self):
        
        logging.info("Clearing chat responses...")
        logging.debug(f"Chat responses before clearing:\n\n {self.chat_responses}")
        self.chat_responses = None
