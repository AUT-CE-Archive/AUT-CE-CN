import os
import sys
import json
import socket
import threading
from termcolor import colored
from dotenv import load_dotenv

from models import *

load_dotenv() # Load .env file

# Environment variables (constants)
BUFFER_SIZE = int(os.getenv("BUFFER_SIZE"))
DEFAULT_HOST = os.getenv("HOST")
DEFAULT_PORT = int(os.getenv("PORT"))


class Client():
    """ Initialize the client """

    def __init__(self, host: str, port: int, topics: list) -> None:

        self.host = host
        self.port = port
        self.topics = topics

        # Create socket with IPv4 address
        self._socket =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"{colored('client started', 'blue')} (PID: {port}): listening on {host}:{port}...")

        # Establish a connection to the server
        self._socket.connect((host, port))
        print(f"{colored('connected to server', 'green')}: Hooray to server!")

        # Subscribe
        Message.initialize(
            message = 'Hello World!',
            topic = 'greeting'
        ).send(port, self._socket)

        threading.Thread(target = self.listener).start()


    def send_data(self, data: str) -> None:
        """ Send some data to the server """

        self._socket.sendall(data.encode())
    

    def listener(self):
        """ Listener thread for asynchronous communication """

        while True:
            data = self._socket.recv(BUFFER_SIZE).decode()

            if '\n' in data:
                message = Message(json.loads(data.strip()))
                print(f"{colored('server broadcast', 'blue')}: {message.get('message')}")
    



if __name__ == '__main__':

    try:
        args = sys.argv
        host, post = args[1], args[2]
        topics = args[4:]
    except:
        # If host and port are not specified, use the default values
        host = DEFAULT_HOST
        port = DEFAULT_PORT
        topics = ['all']

    client = Client(host, int(port), topics)