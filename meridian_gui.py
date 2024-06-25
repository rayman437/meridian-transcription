import tkinter as tk
from tkinter import messagebox, filedialog
from meridian_model import MeridianModel
from dotenv import load_dotenv
from PIL import Image, ImageTk
import os
import random

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
        summarize_button = tk.Button(self, text="Summarize Session", command=self.summarize_session)
        summarize_button.pack()

        transcribe_button = tk.Button(self, text="Transcribe Session", command=self.transcribe_session)
        transcribe_button.pack()

        
        self.model = MeridianModel()
        
        self.mainloop()


    def summarize_session(self):
        # Code to be executed when "Summarize Session" button is pressed
        file_path = filedialog.askopenfilename(filetypes=(('Text Files', '*.txt'), ('All Files', '*.*')))
        if file_path:
            self.model.summarize_session(file_path)
        else:
            messagebox.showinfo("Invalid File", "Please select a valid file.")

    def transcribe_session(self):
        # Code to be executed when "Transcribe Session" button is pressed

        file_path = filedialog.askopenfilename(filetypes=(('Audio Files', '*.flac;*.m4a;*.mp3;*.mp4;*.mpeg;*.mpga;*.oga;*.ogg;*.wav;*.webm'), ('All Files', '*.*')))
        if file_path:
            self.model.transcribe_session(file_path)
        else:
            messagebox.showinfo("Invalid File", "Please select a valid file.")
    

if __name__ == "__main__":
    load_dotenv()
    app = MeridianGUI()
    