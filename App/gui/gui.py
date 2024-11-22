import tkinter as tk
from tkinter import *
from tkinter.filedialog import askopenfile
from tkinter import ttk
import torch
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PeerAI")
        self.geometry("600x400")
        self.model_path = tk.StringVar()
        self.data_path = tk.StringVar()
        self.model_params = None

        style = ttk.Style(self)
        style.configure("TNotebook.Tab", relief="groove")

        self.nb = ttk.Notebook(self)

        # Initialize frames
        config_frame = tk.Frame(self.nb)
        model_frame = tk.Frame(self.nb)
        data_frame = tk.Frame(self.nb)

        # Add frames to notebook
        self.nb.add(config_frame, text="Config")
        self.nb.add(model_frame, text="Model")
        self.nb.add(data_frame, text="Data")
        self.nb.pack(expand=1, fill='both')

        # Add widgets to config_frame
        load_model_button = tk.Button(config_frame, text="Load Model", relief="groove", command=self.get_model)
        load_model_button.place(x=20, y=200)

        open_model_params = tk.Button(config_frame, relief="groove", text=":", command=self.get_model_params)
        open_model_params.place(x=558, y=200)

        label_model_dir = tk.Label(config_frame, font=("Arial", 12), textvariable=self.model_path, relief="sunken", width=50)
        label_model_dir.place(x=100, y=201)

        load_data_button = tk.Button(config_frame, text="Load Data", relief="groove", command=self.get_data)
        load_data_button.place(x=20, y=160)

        label_data_dir = tk.Label(config_frame, font=("Arial", 12), textvariable=self.data_path, relief="sunken", width=50)
        label_data_dir.place(x=100, y=161)

        config_label = tk.Label(config_frame, text="Configuration Settings", font=("Arial", 16))
        config_label.place(x=200, y=50)

        model_label = tk.Label(model_frame, text="Model Information", font=("Arial", 16))
        model_label.pack(pady=20)

        data_label = tk.Label(data_frame, text="Data Information", font=("Arial", 16))
        data_label.pack(pady=20)

    def get_model(self):
        file = askopenfile()
        if file and file.name.lower().endswith('.pth'):
            self.model_path.set(file.name)
            try:
                model = torch.load(file.name, weights_only=True, map_location=torch.device('cpu'))
                self.model_params = model.state_dict() if hasattr(model, "state_dict") else model
                print("Model loaded successfully.")
            except Exception as e:
                self.model_path.set(f"Error loading model: {str(e)}")
                self.model_params = None

        elif file and not file.name.lower().endswith('.pth'):
            self.model_path.set("Not Valid file")
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
            Label(model_params_window, text="No model loaded! Please load a model first.", font=("Arial", 12), fg="red").pack(pady=20)
            return
        canvas = Canvas(model_params_window)
        scrollbar = Scrollbar(model_params_window, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        for key, value in self.model_params.items():
            param_type = "Weight" if "weight" in key.lower() else "Bias" if "bias" in key.lower() else "Parameter"
            param_info = f"Name: {key}\nType: {param_type}\nShape: {tuple(value.shape)}\nValues: {value.tolist()[:3]}{'...' if value.numel() > 3 else ''}"
            param_label = Label(scrollable_frame, text=param_info, font=("Arial", 10), anchor="w", justify="left", wraplength=550)
            param_label.pack(anchor="w", padx=10, pady=5, fill="x")