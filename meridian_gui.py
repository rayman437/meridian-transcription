import tkinter as tk
from tkinter import messagebox, filedialog
from meridian_model import MeridianModel

class MeridianGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Meridian GUI")
        self.geometry("400x300")
        
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
    app = MeridianGUI()
    