from App.Network.server import Server
from App.Network.client import Client
import tkinter as tk
from tkinter import *
from tkinter.filedialog import askopenfile, askdirectory
from tkinter import ttk
from datetime import datetime
import os
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
        self.server = None
        self.server_running = False
        self.connected_peers = []
        self.client = Client(self)

        style = ttk.Style(self)
        style.configure("TNotebook.Tab", relief="groove")

        self.nb = ttk.Notebook(self)

        # Initialize frames (Tabs)
        config_frame = tk.Frame(self.nb)
        network_frame = tk.Frame(self.nb)
        model_frame = tk.Frame(self.nb)
        data_frame = tk.Frame(self.nb)

        # Frames (Tabs) to notebook
        self.nb.add(config_frame, text="Config")
        self.nb.add(network_frame, text="Network")
        self.nb.add(model_frame, text="Model")
        self.nb.add(data_frame, text="Data")
        self.nb.pack(expand=1, fill='both')

        # SERVER:
        # Activate server buutton
        self.server_button = tk.Button(
            network_frame, text="Activate Server", relief="groove", command=self.toggle_server
        )
        self.server_button.place(x=20, y=200)

        # Enter server port
        self.port_var = tk.StringVar(value="54321")
        tk.Label(network_frame, text="Port:").place(x=20, y=160)
        tk.Entry(network_frame, textvariable=self.port_var, width=10).place(x=70, y=160)

        # CLIENT:
        # Client peer/server connected table
        self.peer_table = ttk.Treeview(network_frame, columns=("Host", "Port"), show="headings")
        self.peer_table.heading("Host", text="Host")
        self.peer_table.heading("Port", text="Port")
        self.peer_table.place(x=300, y=160, width=400, height=300)

        # Input  box for connecting to peer host
        tk.Label(network_frame, text="Peer Host:").place(x=20, y=300)
        self.peer_host_var = tk.StringVar(value="127.0.0.1")
        tk.Entry(network_frame, textvariable=self.peer_host_var, width=15).place(x=100, y=300)

        # Input  box for connecting to peer port
        tk.Label(network_frame, text="Peer Port:").place(x=20, y=340)
        self.peer_port_var = tk.StringVar(value="54321")
        tk.Entry(network_frame, textvariable=self.peer_port_var, width=10).place(x=100, y=340)

        # Connect to peer button
        tk.Button(network_frame, text="Connect to Peer", command=self.connect_to_peer).place(x=20, y=380)
        
        # CONFIG FRAME:
        # Buttons:
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

        # LOG:
        # Log Info with Scrollbar in Config Frame
        log_frame = tk.Frame(config_frame)
        log_frame.place(x=75, y=535, width=655, height=50)

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

        # Log Info with Scrollbar in Network Frame
        log_frame_network = tk.Frame(network_frame)
        log_frame_network.place(x=75, y=535, width=655, height=50)

        self.log_text_widget_network = tk.Text(
            log_frame_network,
            font=("Arial", 10),
            wrap="word",
            state="disabled",
            height=5,
            width=55,
        )
        self.log_text_widget_network.pack(side="left", fill="both", expand=True)

        log_scrollbar_network = tk.Scrollbar(log_frame_network, orient="vertical", command=self.log_text_widget_network.yview)
        log_scrollbar_network.pack(side="right", fill="y")
        self.log_text_widget_network.configure(yscrollcommand=log_scrollbar_network.set)

        # Config label
        config_label = tk.Label(config_frame, text="Configuration Settings", font=("Arial", 16))
        config_label.place(x=200, y=50)

        # MODEL FRAME:
        # Model label
        model_label = tk.Label(model_frame, text="Model Information", font=("Arial", 16))
        model_label.pack(pady=20)

        # DATA FRAME:
        # Data label
        data_label = tk.Label(data_frame, text="Data Information", font=("Arial", 16))
        data_label.pack(pady=20)
    
    # FUNCTIONS:
    def log(self, message):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{current_time}] {message}\n"

        # Log to Config Frame
        self.log_text_widget.configure(state="normal")
        self.log_text_widget.insert("end", log_entry)
        self.log_text_widget.configure(state="disabled")
        self.log_text_widget.see("end")

        # Log to Network Frame
        self.log_text_widget_network.configure(state="normal")
        self.log_text_widget_network.insert("end", log_entry)
        self.log_text_widget_network.configure(state="disabled")
        self.log_text_widget_network.see("end")
        
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
            self.data_files = os.listdir(folder)
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

    def toggle_server(self):
        if self.server_running:
            self.stop_server()
        else:
            self.start_server()

    def start_server(self):
        try:
            port = int(self.port_var.get())
            self.server = Server(self)
            self.server.start_server(port)
            self.server_running = True
            self.server_button.config(text="Shutdown Server")
            self.log("Server started successfully.")
        except ValueError:
            self.log("Invalid port. Please enter a valid number.")
        except Exception as e:
            self.log(f"Error starting server: {e}")

    def stop_server(self):
        if self.server and self.server.is_running:  # Check if the server is running
            self.server.stop_server()  # Call the server's stop_server method
            self.server_running = False  # Update the App's server_running flag
            self.server_button.config(text="Activate Server")
            self.log("Server stopped successfully.")

            # Clear only the local server's peer table
            self.clear_peer_table()

    def connect_to_peer(self):
        host = self.peer_host_var.get()
        port = self.peer_port_var.get()
        try:
            port = int(port)
            # Attempt to connect to the peer
            self.client.connect_to_server(host, port)
            if self.client.is_connected:  # Add only if the connection is successful
                self.add_peer_to_table(host, port)
            else:
                self.log(f"Failed to connect to peer {host}:{port}.")
        except ValueError:
            self.log("Invalid port. Please enter a valid number.")
        except Exception as e:
            self.log(f"Unexpected error: {e}")


    def add_peer_to_table(self, host, port):
        # Add peer to the table and the connected peers list
        if (host, port) not in self.connected_peers:  # Prevent duplicates
            self.connected_peers.append((host, port))
            self.peer_table.insert("", "end", values=(host, port))

    def clear_peer_table(self):
        # Clear the Treeview
        for item in self.peer_table.get_children():
            self.peer_table.delete(item)
        # Clear the connected peers list
        self.connected_peers = []
        self.log("Peer table cleared.")

    def handle_peer_disconnection(self, peer_address): # Needs invistigation + Probably was for remove peers when server shutdown.
        host, port = peer_address

        # Only remove from active connections, not the peer table
        if (host, port) in self.connected_peers:
            self.connected_peers.remove((host, port))

        self.log(f"Active connection to {host}:{port} removed.")
