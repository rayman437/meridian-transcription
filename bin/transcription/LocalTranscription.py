import logging
import time
import whisperx as whisper
import ollama
import json
import torch
import os
from bin.transcription.BaseTranscription import BaseTranscription
from pydub import AudioSegment
from pyannote.audio import Pipeline
import torch

class LocalTranscription(BaseTranscription):
    """
    Class for local audio transcription.
    """

    def __init__(self,
                 audio_model = 'small.en',
                 text_model = 'llama3',
                 batch_size = 16,
                 compute_type = "float16",
                 device="cuda"):
        """
        Initializes a new instance of the LocalTranscription class.
        
        This method initializes the LocalTranscription object by calling the base class's __init__ method.
        It prompts the user to select a whisper model from the available models list and loads the selected model.
        """
        super().__init__()
        self._device = device
        self._audio_model = audio_model
        self._batch_size = batch_size
        self._audio_model = audio_model
        self._text_model = text_model
        self._compute_type = compute_type
        self._whisper_model = None
        self.load_ollama_model()

    def load_ollama_model(self):
        if not torch.cuda.is_available():
            self._text_model = "phi3"
        ollama.pull(self._text_model)

    def load_whisper_model(self):
        """
        Loads the whisper model for audio transcription.
        """
        # Default to CPU and smaller models for resources if a GPU is not present
        if not torch.cuda.is_available():
            self._device = 'cpu'
            self._compute_type = "int8"
            self._audio_model = "small.en"

        self._whisper_model = whisper.load_model(
            whisper_arch=self._audio_model,
            device=self._device,
            compute_type=self._compute_type
        )

        if self._whisper_model is None:
            raise Exception("Was not able to create local whisper model instance")
    
    def transcribe_audio_v2(self, file_path, num_speakers=4) -> str:
        
        if self._whisper_model is None:
            self.load_whisper_model()

        # save model to local path (optional)
        # model_dir = "/path/"
        # model = whisperx.load_model("large-v2", device, compute_type=compute_type, download_root=model_dir)
        try:
            audio = whisper.load_audio(file_path)
            logging.info("Beginning transcription")
            start_time = time.time()
            result = self._whisper_model.transcribe(
                audio,
                batch_size=self._batch_size,
                print_progress=True,
                )
            
            logging.info(f"Finished transcription - total time: {(time.time() - start_time):.3f} seconds")
            logging.debug("Before alignment")
            logging.debug(result["segments"]) # before alignment

            # delete model if low on GPU resources
            # import gc; gc.collect(); torch.cuda.empty_cache(); del model

            # 2. Align whisper output
            logging.info("Beginning alignment")
            start_time = time.time()
            
            model_a, metadata = whisper.load_align_model(
                language_code=result["language"],
                device=self._device)
            
            result = whisper.align(result["segments"],
                model_a,
                metadata,
                audio,
                self._device,
                return_char_alignments=False,
                print_progress=True)
            
            logging.info(f"Finished alignment - total time: {(time.time() - start_time):.3f} seconds")
            logging.debug("After alignment")
            logging.debug(result["segments"]) # after alignment
            
            diarize_model = whisper.DiarizationPipeline(use_auth_token=os.getenv("HF_ACCESS_TOKEN"), device=self._device)

            # add min/max number of speakers if known
            logging.info("Beginning diarization")
            start_time = time.time()
            diarize_segments = diarize_model(
                audio,
                min_speakers=1,
                max_speakers=num_speakers)
            logging.info(f"Finished diarization - total time: {(time.time() - start_time):.3f} seconds")
            logging.debug(diarize_segments)
            # diarize_model(audio, min_speakers=min_speakers, max_speakers=max_speakers)

            logging.info("Assigning word speakers")
            start_time = time.time()
            results = whisper.assign_word_speakers(
                diarize_segments,
                result)
            logging.info(f"Finished assigning word speakers - total time: {(time.time() - start_time):.3f} seconds")
            logging.debug(results)
            
            transcription = []
            logging.info("Constructing response")
            start_time = time.time()
            for i, entry in enumerate(results['segments']):
                logging.debug(f"Segment {i}: {entry}")
                if 'speaker' in entry.keys():
                    transcription.append(entry['speaker'] + ": " + entry['text'])
                else:
                    transcription.append("Unknown speaker: " + entry['text'])
                    
            logging.info(f"Done constructing response - total time: {(time.time() - start_time):.3f} seconds")
            
            logging.debug(f"Returning from transcribe_audio_v2 - transcription is below:\n\n{transcription}")
            return '\n'.join(statement for statement in transcription)
        except Exception as e:
            logging.error(e)
            return "Could not transcribe audio. Please try again."
        
    def transcribe_audio(self, file_path) -> str:
        """
        Transcribes the audio file located at the specified file path.

        Args:
            file_path (str): The path to the audio file.

        Returns:
            str: The transcription of the audio file.
        """

        if self._whisper_model is None:
            self.load_whisper_model()
        
        def millisec(val: float ) -> int:

            logging.info(f"Time: {val}")
            return int(val * 1000.0)
      
        # apply pretrained pipeline for diarization
        def get_audiosegment(_file_path):
            temp_filename = _file_path
            file_extension = os.path.splitext(temp_filename)[1][1:]
            start_time = time.time()
            logging.info(f"Loading audio file: {temp_filename}")
            audio = AudioSegment.from_file(temp_filename, format=file_extension)
            logging.info(f"Done loading audio file: {temp_filename}. Time to load: {(time.time() - start_time):.3f}")
            
            # Diarization requires the audio to be in .wav format - convert if necessary
            if file_extension != 'wav':
                temp_filename = os.path.splitext(temp_filename)[0] + '.wav'
                logging.info(f"Converting file from {file_extension} to .wav format. File: {temp_filename}")
                start_time = time.time()
                audio.export(temp_filename, format='wav')
                logging.info(f"Done converting file to .wav format. File: {temp_filename}. Time to transcribe: {(time.time() - start_time):.3f}")
                
            # Return handle to both AudioSegment and the filename of the audio file    
            return (temp_filename, audio)
        
        (diarization_filename, audio) = get_audiosegment(file_path)
        
        diarization_json = os.path.splitext(diarization_filename)[0] + '_diarization.json'
        logging.info(f"Checking if diarization file exists: {diarization_json}")
       
        groups = None
        if os.path.exists(diarization_json):
            logging.info(f"File exists - attempt to load file")
            try:
                logging.info(f"Loading diarization from file: {diarization_json}")
                with open(diarization_json, 'r') as f:
                    groups = json.loads(f.read())
                logging.info(f"Loaded diarization from file: {diarization_json}")
            except Exception as e:
                logging.error(e)
                # Remove diariazation file if it exists
                if os.path.exists(diarization_json):
                    logging.info(f"Removing diarization file: {diarization_json}")
                    os.remove(diarization_json)
                    
                return "Could not load diarization. Please try again."
        
        else:
            logging.info(f"File does not exist - attempt to diarize audio file")
            try:
                start_time = time.time()
                logging.info(f"Begin diarizing audio file: {diarization_filename}")
                diarization = self._audio_pipeline(diarization_filename)
                # Write diarization to a file
                logging.info(f"Finished diarizing audio file: {file_path}. Time to transcribe: {(time.time() - start_time):.3f}")
                logging.info(f"Type of diarization: {type(diarization)}")
            
                groups = { speaker : [] for speaker in diarization.labels()}
                logging.info(f"List of speakers: {groups.keys()}")
                # return type:  Iterator[Union[Tuple[Segment, TrackName], Tuple[Segment, TrackName, Label]]]
                for i, track_data in enumerate(diarization.itertracks(yield_label=True)):
                    for i, datum in enumerate(track_data):
                        logging.debug(f"Speaker[{i}]: {datum}")

                    start = track_data[0].start
                    end = track_data[0].end
                    speaker_id = track_data[2]
                    logging.debug(f"Speaker: {speaker_id} - Start: {start} - End: {end}")
                    groups[speaker_id].append({"start":start, "end": end})
        
                logging.info(f"Writing speaker diarization info to {diarization_json}")
                for speaker, times in groups.items():
                    with open(diarization_json, 'w') as f:
                        f.write(json.dumps(groups))
                logging.info(f"Speaker diarization info written to file: {diarization_json}")

            except Exception as e:
                logging.error(e)                    
                return "Could not transcribe audio. Please try again."
        
        gidx = -1
        speaker_dict = {}
        filenames = [] 
        
        if not os.path.exists(os.path.curdir + r'\tmp'):
            logging.info(f"Making temporary directory for audio files: {os.path.curdir} \\tmp")
            os.makedirs(os.path.curdir + '\\tmp')
            logging.info(f"Done making temporary directory for audio files")

            
        for speaker, time_list in groups.items():
            logging.info(f"Processing speaker {speaker}")
            for seg in time_list:
                logging.info(f"Time tuple: {seg}")
                start = seg['start']
                end = seg['end']
                gidx +=1
                tmp_filename = 'tmp/' + str(gidx) + '.wav'
                speaker_dict[gidx] = speaker

                try:
                    audio[millisec(start):millisec(end)].export(tmp_filename, format='wav')
                    filenames.append(tmp_filename)
                except Exception as e:
                    logging.error(e)
                    logging.error(f"Could not export audio file: {tmp_filename} for times {start} to {end}.")
        
        # Now that we have the diarization, do the transcription
        start_time = time.time()
        transcription = []
        logging.info(f"Begin transcribing audio files for {file_path}")
        gidx = 0
        idx_len = len(filenames)
        for tmpfile in filenames:
            logging.info(f"Transcribing audio file {tmpfile} for idx {gidx} of {idx_len}")
            start_time = time.time()
            audio_data = whisper.load_audio(tmpfile)
            segment_transcription = self._whisper_model.transcribe(
                audio_data, batch_size=self._batch_size)
                
            logging.info(f"Done transcribing audio {tmpfile}. Time to transcribe: {(time.time() - start_time):.3f}")
            transcription.append(f"Speaker {speaker_dict[gidx]}: {segment_transcription['text']}")
            gidx +=1
            
        logging.info(f"Finished transcribing audio files for {file_path}. Time to transcribe: {(time.time() - start_time):.3f}")
                
        return "\n".join(transcription)
        

    def summarize_text(self, transcription, num_lines = 20, levels = 2, granularity=2) -> str:
        """
        Summarizes the transcription of a session.

        Args:
            transcription (str): The transcription of the session.

        Returns:
            str: The summarized version of the transcription.
        """
        num_summarizations = 0
        # Break the text up into smaller chunks to increase the ability for the LLM to extract data
        def summarize_chunk(chunk, num_summarizations):
            
            prompt = f"Summarize the following text:\n {chunk}"
            try:
                logging.info("Summarizing chunk %0d with prompt: %s", num_summarizations, prompt)
                response = ollama.generate(model=self._text_model, prompt=prompt, system="You are an assistant trying to help summarize a text", stream=False)
                logging.info("Response from ollama for chunk %0d: %s", num_summarizations, response['response'])
                num_summarizations+=1
                return response['response']
            except Exception as e:
                logging.error(e)
                return None
            
        def consolidate_chunks(responses, num_summarizations):
            consolidated = ""
            for response in responses:
                consolidated += response + "\n"
            
            return summarize_chunk(consolidated, num_summarizations)
        
        responses = []
        chunks = []
        transcription_lines = transcription.split("\n")
        for i in range(0, len(transcription_lines), num_lines):
            lines = "\n".join(transcription_lines[i:i+num_lines])
            logging.info("Summarizing lines %0d to %0d", i, i+num_lines)
            chunk = summarize_chunk(lines, num_summarizations)
            chunks.append(chunk)
        
        logging.info("Summarizing chunks")
        for i in range(0, levels):
            logging.info("Summarizing level %0d",i+1)
            for i in range(0, len(chunks), granularity):
                logging.info("Summarizing chunk %0d to %0d", i, i+granularity)
                try:
                    response = consolidate_chunks(chunk[i:i+granularity], num_summarizations)
                    logging.info("Consolidated response: %s", {response})
                    responses.append(response)
                except Exception as e:
                    logging.error(e)
                    return None
            logging.info(f"Finished summarizing level {i+1} - resizing chunks ({len(chunks)}) to {len(responses)}")
            logging.info(f"Responses: {responses}")
            chunks = responses
        logging.info("Returning consolidated %0d responses: %s", num_summarizations, "\n".join(chunks) )
        return "\n".join(chunks)
        
        s
        
    def ask_question(self, question, source_info) -> str:
        answer = ""
        if self.chat_responses is None:
            logging.info("Chat responses cleared - reinitializing with contents of transcription window.")
            self.chat_responses = [{"role" : "assistant", 
                                "content" : "You're helping to answer a question about a Dungeons & Dragons campaign."},
                                {"role" : "system",
                                "content" : f'''Please provide a detailed response based on the information in this transcript
                                
{source_info} 
                                
                                             
Any responses that you give should be based on the information in the transcript and the conversation with the user. If you need more information, please ask for it.'''}]
        
        self.chat_responses.append({"role" : "user", "content" : question})
        
        logging.debug(f"Query:\n\n {question}")
        logging.debug(f"Current responses:\n\n {self.chat_responses}")
        
        try:
            logging.info(f"Attempting to send query to ollama for question analysis: {self.chat_responses}")
            responses = ollama.chat(
                messages=self.chat_responses,
                model=self._text_model,
                stream = True,
                options={"num_ctx": 4096,
                         "temperature": 0.85,
                         "num_predict":-1 }
                )
            response_num = 0
            for response in responses:
                if not response['done']:
                    self.chat_responses.append({"role": "assistant",
                                                "content": response['message']['content']})
                    answer+=response['message']['content']
                    response_num +=1
                else:
                    break
            logging.info(f"Received {response_num} responses from ollama")
            logging.debug(f"Response from ollama: {answer}")
            return answer
        
        except Exception as e:
            logging.error(e)
            return "Query failed - please try again."
