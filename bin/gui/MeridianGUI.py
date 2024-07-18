# python3

import tkinter as tk
from tkinter import messagebox, filedialog
from bin.controller.MeridianController import MeridianController
from bin.gui.MeridianAnalyzeGUI import MeridianAnalyzeGUI
from dotenv import load_dotenv
from PIL import Image, ImageTk
import os
import random
import logging 
import time

class MeridianGUI(tk.Tk):
    
    def __init__(self):
        super().__init__()
        self.title("Meridian GUI")

        # Ask the user if they'd like to use local or remote transcription
        transcription_choice = messagebox.askyesno("Transcription Choice", "Would you like to use local transcription?", parent=self)
        service = ""
        if transcription_choice:
            # Code for local transcription
            service = "local"
        else:
            # Code for remote transcription
            service = "remote"
            
        self.controller = MeridianController(transcription_service=service)
        self.model = None
        
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

        # Calculate the number of rows and columns in the grid
        num_buttons = len(self.buttons)
        num_columns = int(num_buttons ** 0.5)
        num_rows = (num_buttons + num_columns - 1) // num_columns

        # Create a grid of buttons
        for i, (button_name, button) in enumerate(self.buttons.items()):
            row = i // num_columns
            column = i % num_columns
            button.grid(row=row, column=column, padx=10, pady=10)

        self.lock_buttons()
        self.set_topmost(self, True)

        # Ask the user if they'd like to load a previous campaign
        self.attributes("-topmost", True)
        load_campaign = messagebox.askyesno("Load Campaign", "Would you like to load a previous campaign?", parent=self)
    
        if load_campaign:
            # Open a file dialog for the user to select a file
            file_path = filedialog.askopenfilename(filetypes=(('CSV Files', '*.csv'), ('All Files', '*.*')))
            if file_path:
                self.get_controller().load_campaign(file_path)
            else:
                messagebox.showinfo("Invalid File", "Please select a valid file.")
         
        self.unlock_buttons()    
        self.set_topmost(self, False)
      
        # Continue with execution
 
        self.mainloop()
    
    
    def get_controller(self) -> MeridianController:
        return self.controller                

    def set_topmost(self, window:tk.Tk, boolean_arg=True):
        if window is None:
            self.attributes("-topmost", boolean_arg)
        else:
            window.attributes("-topmost", boolean_arg)
        
    def lock_buttons(self):
        for button in self.buttons.values():
            button.config(state=tk.DISABLED)

    def unlock_buttons(self):
        for button in self.buttons.values():
            button.config(state=tk.NORMAL)
            
    def summarize_session(self):
        # Code to be executed when "Summarize Session" button is pressed
        file_path = filedialog.askopenfilename(filetypes=(('Text Files', '*.txt'), ('All Files', '*.*')))
        summary = None
        if file_path:
            try:
                summary = self.get_controller().summarize_session(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
                logging.error(e)
                return
        else:
            messagebox.showinfo("Invalid File", "Please select a valid file.")
            
        if summary is not None:
            messagebox.showinfo("Summary", summary)
        else:
            messagebox.showinfo("No Summary", "A problem occured - no summary was generated.")
            
    def analyze_session(self):
        # Create a new window
        analyze_window = MeridianAnalyzeGUI(parent=self, controller=self.get_controller())
        analyze_window.mainloop()
       

    def transcribe_session(self):
        # Code to be executed when "Transcribe Session" button is pressed
        
        self.buttons["transcribe_button"].config(state=tk.DISABLED)

        # Create a new window
        transcription_title = "Ready to transcribe"
        transcription_window = tk.Toplevel(self)
        transcription_window.title(transcription_title)
        transcription_window.resizable(True, True)
        
        # Create a frame inside the window
        frame = tk.Frame(transcription_window)
        frame.pack(fill=tk.BOTH, expand=True)

        # Create a textbox inside the frame
        textbox = tk.Text(frame)
        textbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        def save_transcription():
            self.get_controller().save_session(textbox.get("1.0", tk.END))
        
        def write_transcription():
            file_path = filedialog.asksaveasfilename(filetypes=(('Text Files', '*.txt'), ('All Files', '*.*')))
            if file_path:
                self.get_controller().save_data(file_path, textbox.get("1.0", tk.END))  
                    
        def exit_transcription():
            self.buttons["transcribe_button"].config(state=tk.NORMAL)
            transcription_window.destroy()
        
        # Function to validate the input value
        def validate_num_speakers() -> int:
      
            num_speakers = int(num_speakers_entry.get())
            if num_speakers < 1 or num_speakers > 8:
                raise ValueError(f"Number of Speakers must be an integer between 1 and 8. Value provided: {num_speakers}")
            return num_speakers

        def do_transcription(num_speakers:int=None):
    
            while True:
                # Ask the user for the transcription file

                file_path = filedialog.askopenfilename(filetypes=(('Audio Files', '*.flac;*.m4a;*.mp3;*.mp4;*.mpeg;*.mpga;*.oga;*.ogg;*.wav;*.webm'), ('All Files', '*.*')), parent=transcription_window)
                if file_path:
                    try:
                        num_speakers = validate_num_speakers()
                        # Display an info message warning that transcription will take a while
                        transcription_window.title("Transcribing.....")
                        messagebox.showinfo("Transcription", "Program may hang while transcription is going on - this is normal. Please be patient...")
                        textbox.delete("1.0", tk.END)
                        start_time = time.time()
                        logging.info("GUI: Calling transcribe_audio function")
                        transcription = self.get_controller().transcribe_audio(file_path, num_speakers)
                        logging.info(f"GUI: Transcription completed after {time.time() - start_time} seconds")
        
                        # Display a notification with the transcription duration
                        transcription_window.title(transcription_title)
                        if transcription is not None:
                            messagebox.showinfo("Transcription Complete", f"Transcription completed in {time.time() - start_time} seconds.")
                            textbox.insert(tk.END, transcription)
                        else:
                            messagebox.showerror("Transcription Error", "An error occurred during transcription.")
                            

                        break
                    except Exception as e:
                        messagebox.showerror("Transcription Error", f"An error occurred: {e}")
                        logging.error(e)
        
                if transcription is None:
                    answer = messagebox.askretrycancel("Transcription Error", f"Could not do transcription for {file_path}. Try again?")
                    logging.info(f"Failed transcription: user response = {answer}")
                    if answer == 'cancel':
                        break
   
        transcription_button = tk.Button(frame, text="Transcribe Audio", command= do_transcription)
        transcription_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Create an input box for Number of Speakers
        num_speakers_label = tk.Label(frame, text="Number of Speakers:")
        num_speakers_label.pack(side=tk.LEFT, padx=10, pady=10)
        num_speakers_entry = tk.Entry(frame)
        num_speakers_entry.pack(side=tk.LEFT, padx=10, pady=10)
           
        save_button = tk.Button(frame, text="Save", command= save_transcription)
        save_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        write_button = tk.Button(frame, text="Write to file", command= write_transcription)
        write_button.pack(side=tk.LEFT, padx=10, pady=10)

        exit_button = tk.Button(frame, text="Exit", command=  exit_transcription)
        exit_button.pack(side=tk.LEFT, padx=10, pady=10)
                        
            
    def save_session(self):
        # Code to be executed when "Save" button is pressed
        
        directory_path = filedialog.askdirectory(initialdir='./data')
        if directory_path:
            if os.path.exists(directory_path):
                confirm = messagebox.askyesno("File Exists", "The file already exists. Do you want to overwrite it?")
                if confirm:
                    self.get_controller().save_session(directory_path)
                    messagebox.showinfo("Saved", "Session saved successfully.")
                    return True
                else:
                    messagebox.showinfo("Not Saved", "Session not saved.")
                    return None
            else:
                self.get_controller().save_session(directory_path)
                messagebox.showinfo("Saved", "Session saved successfully.")
                return True
        else:
            messagebox.showinfo("Invalid File", "Please select a valid file.") 
            return None      
        
    def exit_application(self):
        
        exit = False
        while not exit:
            if messagebox.askyesno("Save Session", "Do you want to save your current session?"):
                if self.save_session():
                    exit = True
            else:
                exit = True
        
        self.destroy()
        

    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=(('CSV Files', '*.csv'), ('All Files', '*.*')))
        if file_path:
            self.get_controller().load_campaign(file_path)
        else:
            messagebox.showinfo("Invalid File", "Please select a valid file.")
    
    def view_data(self):
        campaign_info = self.get_controller().get_campaign_info()
        
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
                
            save_to_campaign_button = tk.Button(summary_window, text="Save to Campaign", command= lambda: self.get_controller().save_to_campaign(content) )
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
    