import tkinter as tk
from tkinter import *
from tkinter.filedialog import askopenfile
import torch

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PeerAI")
        self.geometry("600x400")
        self.model_path = tk.StringVar()
        self.data_path= tk.StringVar()

        # button to load model
        load_model_button = tk.Button(self, text="Load Model",relief="groove" , command=self.get_model)
        load_model_button.place(x=20,y=200)

        # label to display model path.
        label_model_dir = tk.Label(self,font=("Arial", 12), textvariable=self.model_path, relief="sunken", width=50)
        label_model_dir.place(x=100, y=201)

        # button to load data.
        load_data_button = tk.Button(self, text="Load Data",relief="groove" , command=self.get_data)
        load_data_button.place(x=20,y=160)

        # label to display data path.
        label_data_dir = tk.Label(self,font=("Arial", 12), textvariable=self.data_path, relief="sunken", width=50)
        label_data_dir.place(x=100, y=161)

    def get_model(self):
        file = askopenfile()

        if file:
            self.model_path.set(file.name)
            model = torch.load(file.name, weights_only=True) # Load model to 
        else:
            self.model_path.set("No file selected")

    def get_data(self):
        file = askopenfile()

        if file:
            self.data_path.set(file.name)
        else:
            self.data_path.set("No file selected")