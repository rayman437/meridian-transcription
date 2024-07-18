import logging
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog

from bin.controller.MeridianController import MeridianController

class MeridianAnalyzeGUI(tk.Toplevel):
        
    def __init__(self, parent, controller: MeridianController) -> None:
        super().__init__(parent)
        
        self.controller = controller
        
        self.title("Analyze Window")
        self.resizable(True, True)
        
        row = 0

        # Create a frame for the transcript textbox and scrollbar
        transcript_frame = tk.Frame(self)
        transcript_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Create a label for Transcript textbox
        transcript_label = tk.Label(transcript_frame, text="Transcript:")
        transcript_label.pack(side=tk.TOP)
        
        # Create a textbox for Transcript
        self.transcript_textbox = tk.Text(transcript_frame, height=10)
        self.transcript_textbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        transcript_scrollbar = tk.Scrollbar(transcript_frame, command=self.transcript_textbox.yview)
        transcript_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.transcript_textbox.config(yscrollcommand=transcript_scrollbar.set)
        #transcript_frame.grid(column=col, row=row, sticky=tk.W + tk.E)
        row+=1
       
        # Create a frame for the query buttons
        query_button_frame = tk.Frame(self)
        query_button_frame.pack()
        
        # Create buttons
        self.buttons = {
            "load_query": tk.Button(query_button_frame, text="Load Query", command=self.load_query).pack(side=tk.LEFT, ipadx=5),
            "save_query": tk.Button(query_button_frame, text="Save Query", command=self.save_query).pack(side=tk.LEFT, ipadx=5),
            "save_conversation": tk.Button(query_button_frame, text="Save Conversation", command=self.save_conversation).pack(side=tk.LEFT, ipadx=5),
            "clear_conversation": tk.Button(query_button_frame, text="Clear Conversation", command=self.clear_conversation).pack(side=tk.LEFT, ipadx=5),           
            "context_size_label" : tk.Label(query_button_frame, text="Context Size:").pack(side=tk.LEFT, ipadx=5),
        }
 
        self.context_size = tk.StringVar()
        self.context_size.set("4096")
        self.context_size_entry = tk.Entry(query_button_frame, textvariable=self.context_size).pack(side=tk.LEFT, ipadx=5)

        #self.buttons["context_size"].insert(tk.END, "4096")
        row+=1

        # Create a frame for the query textbox and scrollbar
        query_frame = tk.Frame(self)
        query_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        #query_textbox = tk.Text(query_frame, height=int(transcript_textbox['height']) // 2)
        self.query_textbox = tk.Text(query_frame, height=10)
        self.query_textbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        query_scrollbar = tk.Scrollbar(query_frame, command=self.query_textbox.yview)
        query_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.query_textbox.config(yscrollcommand=query_scrollbar.set)
        self.query_textbox.insert(tk.END, "Summarize the information in this session. Ignore any conversation unrelated to the role playing that is occurring during this transcript.")
        self.query_textbox.bind("<Return>", lambda event: self.submit_question())

        #query_frame.grid(column=0, row=row, pady=spacing_y, sticky=tk.W + tk.E )
        row+=1

        # Create a frame for the response textbox and scrollbar
        response_frame = tk.Frame(self)
        # Create a label for Response textbox
        response_label = tk.Label(response_frame, text="Response:")
        response_label.pack(side=tk.TOP)

        # Create a textbox for Response
        #response_textbox = tk.Text(response_frame, height=int(transcript_textbox['height']) // 2)
        self.response_textbox = tk.Text(response_frame, height=10)
        self.response_textbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        response_scrollbar = tk.Scrollbar(response_frame, command=self.response_textbox.yview)
        response_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.response_textbox.config(yscrollcommand=response_scrollbar.set)
        #response_frame.grid(column=0, row=row, pady=spacing_y, sticky=tk.W + tk.E )
        response_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        row+=1

        # Create a frame for the buttons
        button_frame = tk.Frame(self)
        self.load_transcript_button = tk.Button(button_frame, text="Load Transcript", command =self.load_transcript)
        self.load_transcript_button.pack(side=tk.LEFT, ipadx=5)        
        self.submit_question_button = tk.Button(button_frame, text="Submit Question", command = self.submit_question)
        self.submit_question_button.pack(side=tk.LEFT, ipadx=5)
        self.save_response_button = tk.Button(button_frame, text="Save Response", command = self.save_response)
        self.save_response_button.pack(side=tk.LEFT, ipadx=5)        
        self.exit_button = tk.Button(button_frame, text="Exit", command= lambda : self.destroy())
        self.exit_button.pack(side=tk.LEFT, ipadx=5)
        #button_frame.grid(column=0, row=row, pady=spacing_y, sticky=tk.W + tk.E )
        button_frame.pack()
     
    def validate_context_size(self, value):
        if value.isdigit():
            size = int(value)
            if size >= 1 and size <= 16192:
                return True
        messagebox.showerror("Invalid Input", "Please enter a valid integer between 1 and 16192")
        return False
                
    # Define button functions
    def load_transcript(self):
        file_path = filedialog.askopenfilename(filetypes=(('Text Files', '*.txt'), ('All Files', '*.*')), parent=self)
        if file_path:
            with open(file_path, 'r') as file:
                content = file.read()
                self.transcript_textbox.delete("1.0", tk.END)
                self.transcript_textbox.insert(tk.END, content)
        logging.info(f"load_transcript function called for file {file_path}")

    def submit_question(self):
        # Code to be executed when "Submit Question" button is pressed
        logging.info("submit_question function called")
        self.submit_question_button.config(state=tk.DISABLED)
        question = self.query_textbox.get("1.0", tk.END).strip()
        transcript = self.transcript_textbox.get("1.0", tk.END).strip()
        c = -1
        
        if self.validate_context_size(self.context_size.get()):
            context_size = int(self.context_size.get())
        else:
            return
            
        try:
           
            if question and transcript:
                response = self.controller.ask_question(question, transcript, context_size)
                self.response_textbox.delete("1.0", tk.END)
                self.response_textbox.insert(tk.END, response)
            else:
                messagebox.showinfo("Invalid Question", "Please enter a valid question.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            logging.error(e)
            
        self.submit_question_button.config(state=tk.NORMAL)
        logging.info("submit_question function exit")

    def save_response(self):
        logging.info("save_response function called")
        file_path = filedialog.asksaveasfilename(filetypes=(('Text Files', '*.txt'), ('All Files', '*.*')))
        if file_path:
            self.controller.save_data(file_path, self.response_textbox.get("1.0", tk.END))
        else:
            messagebox.showinfo("Invalid File", "Please select a valid file.")

    
    def load_query(self):
        logging.info("load_query function called")
        file_path = filedialog.askopenfilename(filetypes=(('Text Files', '*.txt'), ('All Files', '*.*')), parent=self)
        if file_path:
            self.query_textbox.delete("1.0", tk.END)
            self.query_textbox.insert(tk.END, self.controller.load_data(file_path))    

    def save_query(self):
        logging.info("save_query function called")
        file_path = filedialog.asksaveasfilename(filetypes=(('Text Files', '*.txt'), ('All Files', '*.*')))
        if file_path:
            self.controller.save_data(file_path, self.query_textbox.get("1.0", tk.END))
        else:
            messagebox.showinfo("Invalid File", "Please select a valid file.")
    
    def clear_conversation(self):
        logging.info("Clearing conversation")
        self.controller.clear_conversation()
        self.response_textbox.delete("1.0", tk.END)
        
    def save_conversation(self):
        # Code to be executed when "Save Conversation" button is pressed
        file_path = filedialog.asksaveasfilename(filetypes=(('Text Files', '*.txt'), ('All Files', '*.*')))
        logging.info(f"Saving conversation to file {file_path}")
        if file_path:
            self.controller.save_conversation(file_path)
        else:
            messagebox.showinfo("Invalid File", "Please select a valid file.")
