from bin.transcription.LocalTranscription import LocalTranscription
from bin.transcription.RemoteTranscription import RemoteTranscription

import os
import json
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage
import random
import string


class MeridianModel:

    def __init__(self, persist_dir:str = "./data"):
        
        self.index = None
        self.persist_dir = persist_dir

    def save_session(self) -> None:

        # Implement the save_session function here
        self.index.storage_context.persist(persist_dir=self.persist_dir)

    def load_campaign(self, file_path=None) -> None:
        # Implement the load_progress function here
        
        if file_path is None:
            file_path = self.persist_dir
            
        storage_context = StorageContext.from_defaults(persist_dir=file_path)
        self.index = load_index_from_storage(storage_context)

    def save_to_campaign(self, data) -> None:
        
        # Implement the save_to_campaign function here
        def generate_random_filename(length):
            letters_and_digits = string.ascii_letters + string.digits
            while True:
                filename = ''.join(random.choice(letters_and_digits) for _ in range(length))
                if not os.path.exists(os.path.join(self.persist_dir, filename)):
                    return filename

        # Make filenames unique and 10 characters long  
        filename = generate_random_filename(10)
        with open(os.path.join(self.persist_dir, filename), 'w') as file:
            file.write(data)
            
        # Reload the campaign
        self.load_campaign(self.persist_dir)
        
        # Save the new index
        self.save_session()


