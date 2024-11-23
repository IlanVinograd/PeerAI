import socket
import threading

class Server():
    def __init__(self, app, host="127.0.0.1"):
        self.app = app
        self.server_host = host
        self.server_port = None  # Port to be chosen by the user
        self.server_socket = None
        self.is_running = False
        self.server_thread = None

    def start_server(self, port):
        self.server_port = port
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.server_host, self.server_port))
            self.server_socket.listen(5)
            self.is_running = True
            self.app.log(f"Server started on {self.server_host}:{self.server_port}")

            self.server_thread = threading.Thread(target=self.accept_clients, daemon=True)
            self.server_thread.start()
        except Exception as e:
            self.app.log(f"Error starting server: {e}")

    def accept_clients(self):
        try:
            while self.is_running:
                try:
                    self.server_socket.settimeout(1.0)  # Timeout in seconds
                    client_socket, client_address = self.server_socket.accept()
                    self.app.log(f"Connection from {client_address}")
                    threading.Thread(target=self.handle_client, args=(client_socket,)).start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.is_running:  # Log errors only if the server is still running
                        self.app.log(f"Error accepting clients: {e}")
        except Exception as e:
            self.app.log(f"Error in accept_clients: {e}")

    def handle_client(self, client_socket):
        try:
            while self.is_running:
                data = client_socket.recv(1024)
                if not data:
                    break
                message = data.decode('utf-8')
                self.app.log(f"Received: {message}")
                client_socket.send(f"ECHO: {message}".encode('utf-8'))
        except Exception as e:
            self.app.log(f"Client error: {e}")
        finally:
            client_socket.close()

    def stop_server(self):
        if self.is_running:
            self.is_running = False
            if self.server_socket:
                try:
                    self.server_socket.close()
                except Exception as e:
                    self.app.log(f"Error closing server socket: {e}")
            self.app.log("Server stopped.")