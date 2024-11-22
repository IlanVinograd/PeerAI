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
        self.data_path = tk.StringVar()
        self.model_params = None

        # Button to load model
        load_model_button = tk.Button(self, text="Load Model", relief="groove", command=self.get_model)
        load_model_button.place(x=20, y=200)

        # Button to open model params
        open_model_params = tk.Button(self, relief="groove", text=":", command=self.get_model_params)
        open_model_params.place(x=558, y=200)

        # Label to display model path
        label_model_dir = tk.Label(self, font=("Arial", 12), textvariable=self.model_path, relief="sunken", width=50)
        label_model_dir.place(x=100, y=201)

        # Button to load data
        load_data_button = tk.Button(self, text="Load Data", relief="groove", command=self.get_data)
        load_data_button.place(x=20, y=160)

        # Label to display data path
        label_data_dir = tk.Label(self, font=("Arial", 12), textvariable=self.data_path, relief="sunken", width=50)
        label_data_dir.place(x=100, y=161)

    def get_model(self):
        file = askopenfile()

        if file:
            self.model_path.set(file.name)
            try:
                # Load model and extract parameters
                model = torch.load(file.name, map_location=torch.device('cpu'))
                self.model_params = model.state_dict() if hasattr(model, "state_dict") else model
                print("Model loaded successfully.")
            except Exception as e:
                self.model_path.set(f"Error loading model: {str(e)}")
                self.model_params = None
        else:
            self.model_path.set("No file selected")
            self.model_params = None

    def get_data(self):
        file = askopenfile()

        if file:
            self.data_path.set(file.name)
        else:
            self.data_path.set("No file selected")

    def get_model_params(self):
        model_params_window = Toplevel(self)
        model_params_window.title("Model Params")
        model_params_window.geometry("600x600")

        if self.model_params is None:
            # Show an error message if no model is loaded
            Label(model_params_window, text="No model loaded! Please load a model first.", font=("Arial", 12), fg="red").pack(pady=20)
            return

        # Create a scrollable frame
        canvas = Canvas(model_params_window)
        scrollbar = Scrollbar(model_params_window, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Display model parameters
        for key, value in self.model_params.items():
            # Determine if the tensor is a weight or bias based on its name
            param_type = "Weight" if "weight" in key.lower() else "Bias" if "bias" in key.lower() else "Parameter"
            param_info = (
                f"Name: {key}\n"
                f"Type: {param_type}\n"
                f"Shape: {tuple(value.shape)}\n"
                f"Values: {value.tolist()[:3]}{'...' if value.numel() > 3 else ''}"
            )
            param_label = Label(scrollable_frame, text=param_info, font=("Arial", 10), anchor="w", justify="left", wraplength=550)
            param_label.pack(anchor="w", padx=10, pady=5, fill="x")