import os
import socket
import threading
from dotenv import load_dotenv

load_dotenv() # Load .env file

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
BUFFER_SIZE = int(os.getenv("BUFFER_SIZE"))


class Client():

    def __init__(self) -> None:
        
        # IPv4 address
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as _socket:
            
            # Establish a connection to the server
            _socket.connect((HOST, PORT))

            # Send data to the server
            _socket.sendall(b"Hello, world!")

            # Receive data from the server and shut down
            data = _socket.recv(1024)
            print(data.decode())



if __name__ == '__main__':
    client = Client()