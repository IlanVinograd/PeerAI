import socket
import threading
import time

class Client:
    def __init__(self, app):
        self.app = app
        self.server_address = None
        self.client_socket = None
        self.is_connected = False
        self.monitor_thread = None
        self.client_id = f"Client-{id(self)}"

    def connect_to_server(self, host, port):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host, port))
            self.is_connected = True
            self.server_address = (host, port)
            self.app.log(f"Connected to server at {host}:{port}")

            # Start listening for messages from the server
            threading.Thread(target=self.listen_to_server, daemon=True).start()

            # Start monitoring the connection
            self.monitor_thread = threading.Thread(target=self.monitor_connection, daemon=True)
            self.monitor_thread.start()
        except ConnectionRefusedError:
            self.is_connected = False
            self.app.log(f"Connection refused to {host}:{port}")
        except Exception as e:
            self.is_connected = False
            self.app.log(f"Error connecting to server: {e}")

    def monitor_connection(self):
        while self.is_connected:
            try:
                self.client_socket.send(b"PING")
                time.sleep(5)
            except Exception as e:
                self.app.log(f"Lost connection to server {self.server_address}.")
                self.is_connected = False
                self.app.handle_peer_disconnection(self.server_address)  # Cleanup
                break

    def listen_to_server(self):
        try:
            while self.is_connected:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                message = data.decode('utf-8')

                # Handle server shutdown notification
                if message == "REMOVE_CONNECTION": # Where is it used?? Server Shutdown?? need fix.
                    self.app.log(f"Server {self.server_address} is disconnecting.")
                    self.disconnect()
                    break

                self.app.log(f"Message from server: {message}")
        except Exception as e:
            self.app.log(f"Connection error: {e}")
        finally:
            self.disconnect()  # Only disconnect active connections


    def send_message(self, message): # Not in used
        if self.is_connected:
            try:
                self.client_socket.send(message.encode('utf-8'))
            except Exception as e:
                self.app.log(f"Error sending message: {e}")

    def disconnect(self):
        if self.is_connected:
            try:
                self.client_socket.close()
            except Exception as e:
                self.app.log(f"Error closing connection: {e}")
            self.is_connected = False
            self.app.log("Disconnected from server.")
