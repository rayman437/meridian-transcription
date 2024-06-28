# python3

import tkinter as tk
from tkinter import messagebox, filedialog
from bin.MeridianModel import MeridianModel
from dotenv import load_dotenv
from PIL import Image, ImageTk
import os
import random
import logging 

class MeridianGUI(tk.Tk):
    
    def __init__(self):
        super().__init__()
        self.title("Meridian GUI")
        self.geometry("")

        # Randomly pick an image
        # Get the path to the bin folder
        bin_folder = os.path.join(os.getcwd(), "bin/splash_images")

        # Get a list of all .jpg files in the bin folder
        jpg_files = [file for file in os.listdir(bin_folder) if file.endswith(".jpg")]

        # Randomly pick one .jpg file
        random_jpg_file = random.choice(jpg_files)

        # Get the full path to the randomly picked .jpg file
        jpg_file_path = os.path.join(bin_folder, random_jpg_file)
        
        # Add in an image, for funsies
        image = Image.open(jpg_file_path)
        width, height = image.size
        new_height = 300
        new_width = int((width / height) * new_height)
        image = image.resize((new_width, new_height))
        photo = ImageTk.PhotoImage(image)
        image_label = tk.Label(self, image=photo)
        image_label.image = photo  # Keep a reference to the image to prevent garbage collection
        image_label.pack()
        
        # Add your GUI elements here
        button_frame = tk.Frame(self)
        button_frame.pack()

        self.buttons = {
            "summarize_button": tk.Button(button_frame, text="Summarize Session", command=self.summarize_session),
            "transcribe_button": tk.Button(button_frame, text="Transcribe Session", command=self.transcribe_session),
            "load_data_button": tk.Button(button_frame, text="Load Data", command=self.load_data),
            "load_transcript_button": tk.Button(button_frame, text="Load Transcript", command=self.load_summary),
            "load_summary_button": tk.Button(button_frame, text="Load Summary", command=self.load_summary),
            "view_data_button": tk.Button(button_frame, text="View Data", command=self.view_data),
            "analyze_button": tk.Button(button_frame, text="Analyze Session", command=self.analyze_session),
            "save_button": tk.Button(button_frame, text="Save", command=self.save_session),
            "exit_button": tk.Button(button_frame, text="Exit", command=self.exit_application)
        }
        # Calculate the minimum value of n
        n = int(len(self.buttons) ** 0.5) + 1

        # Pack each button into the grid
        for i, (button_name, button) in enumerate(self.buttons.items()):
            row = i // n
            column = i % n
            button.grid(row=row, column=column, padx=10, pady=10)
        
        self.model = MeridianModel()
        
        # Ask the user if they'd like to load a previous campaign
        load_campaign = messagebox.askyesno("Load Campaign", "Would you like to load a previous campaign?")

        if load_campaign:
            # Open a file dialog for the user to select a file
            file_path = filedialog.askopenfilename(filetypes=(('CSV Files', '*.csv'), ('All Files', '*.*')))
            if file_path:
                self.model.load_campaign(file_path)
            else:
                messagebox.showinfo("Invalid File", "Please select a valid file.")
                
        # Continue with execution
        
        self.mainloop()


    def summarize_session(self):
        # Code to be executed when "Summarize Session" button is pressed
        file_path = filedialog.askopenfilename(filetypes=(('Text Files', '*.txt'), ('All Files', '*.*')))
        if file_path:
            try:
                self.model.summarize_audio(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
                logging.error(e)
                return
        else:
            messagebox.showinfo("Invalid File", "Please select a valid file.")
            
    def analyze_session(self):

        # Define button functions
        def load_transcript():
            file_path = filedialog.askopenfilename(filetypes=(('Text Files', '*.txt'), ('All Files', '*.*')))
            if file_path:
                with open(file_path, 'r') as file:
                    content = file.read()
                    transcript_textbox.delete("1.0", tk.END)
                    transcript_textbox.insert(tk.END, content)
            print("load_transcript function called")

        def submit_question():
            # Code to be executed when "Submit Question" button is pressed
            print("submit_question function called")
            submit_question_button.config(state=tk.DISABLED)
            try:
                question = query_textbox.get("1.0", tk.END).strip()
                if question:
                    response = self.model.ask_question(question, transcript_textbox.get("1.0", tk.END).strip())
                    response_textbox.delete("1.0", tk.END)
                    response_textbox.insert(tk.END, response)
                else:
                    messagebox.showinfo("Invalid Question", "Please enter a valid question.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
                logging.error(e)
                
            submit_question_button.config(state=tk.NORMAL)
            print("submit_question function exit")

        def save_response():
            # Code to be executed when "Save Response" button is pressed
            file_path = filedialog.asksaveasfilename(filetypes=(('Text Files', '*.txt'), ('All Files', '*.*')))
            if file_path:
                with open(file_path, 'w') as file:
                    file.write(response_textbox.get("1.0", tk.END))
            else:
                messagebox.showinfo("Invalid File", "Please select a valid file.")
            print("save_response function called")
        
        # Create a new window
        analyze_window = tk.Toplevel(self)
        analyze_window.title("Analyze Session")
        analyze_window.geometry("500x1200")

        # Create a frame inside the window
        frame = tk.Frame(analyze_window)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a frame for the transcript textbox and scrollbar
        transcript_frame = tk.Frame(frame)
        transcript_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Create a label for Transcript textbox
        transcript_label = tk.Label(transcript_frame, text="Transcript:")
        transcript_label.pack(side=tk.TOP, padx=10, pady=10)
        
        # Create a textbox for Transcript
        transcript_textbox = tk.Text(transcript_frame)
        transcript_textbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        transcript_scrollbar = tk.Scrollbar(transcript_frame, command=transcript_textbox.yview)
        transcript_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        transcript_textbox.config(yscrollcommand=transcript_scrollbar.set)

        # Create a frame for the query textbox and scrollbar
        query_frame = tk.Frame(frame)
        query_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Create a label for Query textbox
        query_label = tk.Label(query_frame, text="Query:")
        query_label.pack(side=tk.TOP, padx=10, pady=5)

        # Create a textbox for Query
        query_textbox = tk.Text(query_frame, height=int(transcript_textbox['height']) // 2)
        query_textbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        query_scrollbar = tk.Scrollbar(query_frame, command=query_textbox.yview)
        query_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        query_textbox.config(yscrollcommand=query_scrollbar.set)

        # Create a frame for the response textbox and scrollbar
        response_frame = tk.Frame(frame)
        response_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Create a label for Response textbox
        response_label = tk.Label(response_frame, text="Response:")
        response_label.pack(side=tk.TOP, padx=10, pady=5)

        # Create a textbox for Response
        response_textbox = tk.Text(response_frame, height=int(transcript_textbox['height']) // 2)
        response_textbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        response_scrollbar = tk.Scrollbar(response_frame, command=response_textbox.yview)
        response_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        response_textbox.config(yscrollcommand=response_scrollbar.set)

        # Create a frame for the buttons
        button_frame = tk.Frame(analyze_window)
        button_frame.pack(side=tk.BOTTOM, padx=10, pady=10)
        
        load_transcript_button = tk.Button(button_frame, text="Load Transcript", command =load_transcript)
        load_transcript_button.pack(side=tk.LEFT, padx=10)

        submit_question_button = tk.Button(button_frame, text="Submit Question", command = submit_question)
        submit_question_button.pack(side=tk.LEFT, padx=10)

        save_response_button = tk.Button(button_frame, text="Save Response", command = save_response)
        save_response_button.pack(side=tk.LEFT, padx=10)

        exit_button = tk.Button(button_frame, text="Exit", command= lambda : analyze_window.destroy())
        exit_button.pack(side=tk.LEFT, padx=10)

        # Make the window resizable
        analyze_window.pack_slaves()
        analyze_window.resizable(True, True)


    def transcribe_session(self):
        # Code to be executed when "Transcribe Session" button is pressed
        transcription = None
        
        self.buttons["transcribe_button"].config(state=tk.DISABLED)

        file_path = filedialog.askopenfilename(filetypes=(('Audio Files', '*.flac;*.m4a;*.mp3;*.mp4;*.mpeg;*.mpga;*.oga;*.ogg;*.wav;*.webm'), ('All Files', '*.*')))
        if file_path:
            try:
                transcription = self.model.transcribe_audio(file_path)
            except Exception as e:
                messagebox.showerror("Transcription Error", f"An error occurred: {e}")
                logging.error(e)
                return
        else:
            messagebox.showinfo("Invalid File", "Please select a valid file.")
            
        if transcription is None:
            messagebox.showerror("Transcription Error", f"Failed to transcribe file: {file_path}")
            
        if transcription is not None:
            # Create a new window
            transcription_window = tk.Toplevel(self)
            transcription_window.title("Transcription")
            transcription_window.geometry("500x500")

            # Create a frame inside the window
            frame = tk.Frame(transcription_window)
            frame.pack(fill=tk.BOTH, expand=True)

            # Create a textbox inside the frame
            textbox = tk.Text(frame)
            textbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            
            def save_transcription():
                self.model.save_session(textbox.get("1.0", tk.END))
            
            def write_transcription():
                file_path = filedialog.asksaveasfilename(filetypes=(('Text Files', '*.txt'), ('All Files', '*.*')))
                if file_path:
                    with open(file_path, 'w') as file:
                        transcription = textbox.get("1.0", tk.END)
                        file.write(transcription)
                        
            def exit_transcription():
                self.buttons["transcribe_button"].config(state=tk.NORMAL)
                transcription_window.destroy()
            
            save_button = tk.Button(frame, text="Save", command= save_transcription)
            save_button.pack(side=tk.LEFT, padx=10, pady=10)
            
            write_button = tk.Button(frame, text="Write to file", command= write_transcription)
            write_button.pack(side=tk.LEFT, padx=10, pady=10)

            exit_button = tk.Button(frame, text="Exit", command=  exit_transcription)
            exit_button.pack(side=tk.LEFT, padx=10, pady=10)

            # Insert the transcription into the textbox
            textbox.insert(tk.END, transcription)

            # Make the window resizable
            transcription_window.resizable(True, True)
        else:
            messagebox.showinfo("Transcription Error", "No transcription available.")
    def save_session(self):
        # Code to be executed when "Save" button is pressed
        
        file_path = filedialog.asksaveasfilename(filetypes=(('Text Files', '*.txt'), ('All Files', '*.*')))
        if file_path:
            if os.path.exists(file_path):
                confirm = messagebox.askyesno("File Exists", "The file already exists. Do you want to overwrite it?")
                if confirm:
                    self.model.save_session(file_path)
                    messagebox.showinfo("Saved", "Response saved successfully.")
                else:
                    messagebox.showinfo("Not Saved", "Response not saved.")
            else:
                self.model.save_session(file_path)
                messagebox.showinfo("Saved", "Response saved successfully.")
        else:
            messagebox.showinfo("Invalid File", "Please select a valid file.")       
        
    def exit_application(self):
        confirm = messagebox.askyesno("Save Session", "Do you want to save your current session?")
        if confirm:
            self.save_session()
        self.destroy()
        
    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=(('CSV Files', '*.csv'), ('All Files', '*.*')))
        if file_path:
            self.model.load_campaign(file_path)
        else:
            messagebox.showinfo("Invalid File", "Please select a valid file.")
    
    def view_data(self):
        campaign_info = self.model.get_campaign_info()
        
        if len(campaign_info) == 0:
            messagebox.showinfo("No Data", "There is no data to display.")
            return
        
        class CampaignInfoIterator:
            def __init__(self, campaign_info):
                self.campaign_info = campaign_info
                self.index = 0

            def __iter__(self):
                return self

            def get_next(self) -> str:
                if self.index >= len(self.campaign_info):
                    return self.get_cur_entry()
                else:
                    entry = self.campaign_info[self.index]
                    self.index += 1
                    return entry
                
            def get_previous(self) -> str:
                if self.index <= 0:
                    return self.get_cur_entry()
                else:
                    entry = self.campaign_info[self.index]
                    self.index -= 1
                    return entry
                
            def __getitem__(self, index:int):
                    return self.campaign_info[index]
                
            def get_cur_idx(self) -> int:
                return self.index
            
            def get_cur_entry(self) -> str:
                return self.campaign_info[self.index]
                
        # Inside the view_data method
        campaign_info_iterator = CampaignInfoIterator(campaign_info)
        
        # Create a new window
        info_window = tk.Toplevel(self)
        info_window.title("Campaign Info")
        info_window.geometry("500x500")
        
        # Make the window resizable
        info_window.resizable(True, True)
        
        # Create a frame inside the window
        frame = tk.Frame(info_window)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a textbox inside the frame
        textbox = tk.Text(frame)
        textbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Create a button frame inside the frame
        button_frame = tk.Frame(frame)
        button_frame.pack(side=tk.TOP, pady=10)
        
        # Create previous, next, and exit buttons
        previous_button = tk.Button(button_frame, text="Previous", command = textbox.insert(tk.END, lambda: campaign_info_iterator.get_next()))
        previous_button.pack(side=tk.LEFT, padx=10)

        next_button = tk.Button(button_frame, text="Next", command = textbox.insert(tk.END, lambda: campaign_info_iterator.get_previous()))
        next_button.pack(side=tk.LEFT, padx=10)

        exit_button = tk.Button(button_frame, text="Exit", command = lambda: info_window.destroy())
        exit_button.pack(side=tk.LEFT, padx=10)

        # Load the first entry of the list into the textbox
        textbox.insert(tk.END, campaign_info_iterator.get_cur_entry())
            
    def load_summary(self):
        file_path = filedialog.askopenfilename(filetypes=(('Text Files', '*.txt'), ('All Files', '*.*')))
        if file_path:
            with open(file_path, 'r') as file:
                content = file.read()
            
            # Create a new window
            summary_window = tk.Toplevel(self)
            summary_window.title("Transcript")
            summary_window.geometry("500x500")
            
            # Create a text widget inside the window
            text_widget = tk.Text(summary_window)
            text_widget.pack(fill=tk.BOTH, expand=True)
            
            # Insert the content into the text widget
            text_widget.insert(tk.END, content)
                
            save_to_campaign_button = tk.Button(summary_window, text="Save to Campaign", command= lambda: self.model.save_to_campaign(content) )
            save_to_campaign_button.pack(side=tk.LEFT, padx=10, pady=10)

            exit_transcript_button = tk.Button(summary_window, text="Exit", command=summary_window.destroy)
            exit_transcript_button.pack(side=tk.RIGHT, padx=10, pady=10)
            
            # Make the window resizable
            summary_window.resizable(True, True)
        else:
            messagebox.showinfo("Invalid File", "Please select a valid file.")
        
if __name__ == "__main__":
    load_dotenv()
     
    # Configure the logging package
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
        logging.FileHandler('log.txt'),
        logging.StreamHandler()
    ])
    app = MeridianGUI()
    