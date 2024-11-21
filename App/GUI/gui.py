import tkinter as tk
from tkinter import *
from tkinter.filedialog import askopenfile

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PeerAI")
        self.geometry("600x400")
        self.model = tk.StringVar()

        # button to load model
        load_model_button = tk.Button(self, text="Load Model",relief="groove" , command=self.get_model)
        load_model_button.place(x=20,y=200)

        # label to display model path.
        label_model_dir = tk.Label(self,font=("Arial", 12), textvariable=self.model, relief="sunken", width=50)
        label_model_dir.place(x=100, y=201)

    
    def get_model(self):
        file = askopenfile()

        if file:
            self.model.set(file.name)
            print(self.model.get())
        else:
            self.model.set("No file selected")