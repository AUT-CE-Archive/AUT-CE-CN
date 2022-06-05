import os
import socket
import threading
from dotenv import load_dotenv

load_dotenv() # Load .env file

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))


class Server():

    def __init__(self) -> None:

        # IPv4 address
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as _socket:
            
            # Bind on the Host & Port, and listen for incoming connections
            _socket.bind((HOST, PORT))
            _socket.listen()

            # Block until a connection is made
            conn, addr = _socket.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    conn.sendall(data)
                    print(data.decode())



if __name__ == '__main__':
    server = Server()