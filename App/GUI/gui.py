import os
from datetime import datetime
import tkinter as tk
from tkinter import *
from tkinter.filedialog import askopenfile, askdirectory
from tkinter import ttk
import torch

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PeerAI")
        self.geometry("824x668")
        self.model_path = tk.StringVar()
        self.data_path = tk.StringVar()
        self.model_params = None
        self.data_files = []

        style = ttk.Style(self)
        style.configure("TNotebook.Tab", relief="groove")

        self.nb = ttk.Notebook(self)

        # Initialize frames
        config_frame = tk.Frame(self.nb)
        model_frame = tk.Frame(self.nb)
        data_frame = tk.Frame(self.nb)

        # Frames to notebook
        self.nb.add(config_frame, text="Config")
        self.nb.add(model_frame, text="Model")
        self.nb.add(data_frame, text="Data")
        self.nb.pack(expand=1, fill='both')

        load_model_button = tk.Button(config_frame, text="Load Model", relief="groove", command=self.get_model)
        load_model_button.place(x=20, y=200)

        open_model_params = tk.Button(config_frame, relief="groove", text=":", command=self.get_model_params)
        open_model_params.place(x=558, y=200)

        label_model_dir = tk.Label(config_frame, font=("Arial", 12), textvariable=self.model_path, relief="sunken", width=50)
        label_model_dir.place(x=100, y=201)

        load_data_button = tk.Button(config_frame, text="Load Data", relief="groove", command=self.get_data)
        load_data_button.place(x=20, y=160)

        view_data_params = tk.Button(config_frame, relief="groove", text=":", command=self.get_data_params)
        view_data_params.place(x=558, y=160)

        label_data_dir = tk.Label(config_frame, font=("Arial", 12), textvariable=self.data_path, relief="sunken", width=50)
        label_data_dir.place(x=100, y=161)

        # Log Info with Scrollbar
        log_frame = tk.Frame(config_frame)
        log_frame.place(x=75, y=565, width=655, height=70)

        self.log_text_widget = tk.Text(
            log_frame,
            font=("Arial", 10),
            wrap="word",
            state="disabled",
            height=5,
            width=55,
        )
        self.log_text_widget.pack(side="left", fill="both", expand=True)

        log_scrollbar = tk.Scrollbar(log_frame, orient="vertical", command=self.log_text_widget.yview)
        log_scrollbar.pack(side="right", fill="y")
        self.log_text_widget.configure(yscrollcommand=log_scrollbar.set)

        config_label = tk.Label(config_frame, text="Configuration Settings", font=("Arial", 16))
        config_label.place(x=200, y=50)

        model_label = tk.Label(model_frame, text="Model Information", font=("Arial", 16))
        model_label.pack(pady=20)

        data_label = tk.Label(data_frame, text="Data Information", font=("Arial", 16))
        data_label.pack(pady=20)

    def log(self, message):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{current_time}] {message}\n"

        # Enable the Text widget to allow inserting text
        self.log_text_widget.configure(state="normal")
        self.log_text_widget.insert("end", log_entry)  # Add the log entry at the end
        self.log_text_widget.configure(state="disabled")  # Disable editing again

        # Scroll to the end
        self.log_text_widget.see("end")

    def get_model(self):
        file = askopenfile()
        if file and file.name.lower().endswith('.pth'):
            self.model_path.set(file.name)

            try:
                model = torch.load(file.name, weights_only=True, map_location=torch.device('cpu'))
                self.model_params = model.state_dict() if hasattr(model, "state_dict") else model
                self.log(f"Model loaded successfully")
            except Exception as e:
                self.model_path.set(f"Error loading model: {str(e)}")
                self.log(f"Error loading model: {str(e)}")
                self.model_params = None

        elif file and not file.name.lower().endswith('.pth'):
            self.model_path.set("Not Valid file")
            self.log("Invalid file type selected.")
            self.model_params = None

        else:
            self.model_path.set("No file selected")
            self.log("No file selected.")
            self.model_params = None

    def get_data(self):
        folder = askdirectory()

        if folder:
            self.data_path.set(folder)
            self.data_files = os.listdir(folder)  # List all files in the folder
            self.log(f"Folder loaded successfully: {folder}")
        else:
            self.data_path.set("No folder selected")
            self.log("No folder selected.")

    def get_data_params(self):
        # Create a new window for data parameters
        data_params_window = Toplevel(self)
        data_params_window.title("Data Params")
        data_params_window.geometry("600x600")

        # If no folder is selected, display a message and exit
        if not self.data_files:
            Label(data_params_window, text="No folder loaded! Please load a folder first.", font=("Arial", 12), fg="red").pack(pady=20)
            self.log("Data Params: No folder loaded.")
            return

        # Create a scrollable frame for data params 
        canvas = Canvas(data_params_window)
        scrollbar = Scrollbar(data_params_window, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Display files in the folder
        for file in self.data_files:
            file_summary = f"File: {file}\n"
            file_label = Label(scrollable_frame, text=file_summary, font=("Arial", 10), anchor="w", justify="left", wraplength=550)
            file_label.pack(anchor="w", padx=10, pady=5, fill="x")
        self.log("Data Params: Displaying data files.")

    def get_model_params(self):
        # Create a new window for model parameters
        model_params_window = Toplevel(self)
        model_params_window.title("Model Params")
        model_params_window.geometry("600x600")

        # If no model is loaded, display a message and exit
        if self.model_params is None:
            Label(model_params_window, text="No model loaded! Please load a model first.", font=("Arial", 12), fg="red").pack(pady=20)
            self.log("Model Params: No model loaded.")
            return

        # Create a scrollable frame for model params
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
            param_shape = tuple(value.shape)
            param_preview = value.flatten().tolist()[:5]  # Show the first 5 elements as a preview

            # Display parameter summary
            param_summary = (
                f"\nName: {key}\n"
                f"Type: {param_type}\n"
                f"Shape: {param_shape}\n"
                f"Preview: {param_preview}...\n\n"
                f"-------------------------------------------------------------------------------------------------------------------------------\n"
            )

            param_label = Label(scrollable_frame, text=param_summary, font=("Arial", 10), anchor="w", justify="left", wraplength=550)
            param_label.pack(anchor="w", padx=10, pady=5, fill="x")
        
        self.log("Model Params: Displaying model parameters.")