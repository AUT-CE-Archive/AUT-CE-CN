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

    def __init__(self, host: str, port: int) -> None:

        self.host = host
        self.port = port

        # Create socket with IPv4 address
        self._socket =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Establish a connection to the server
        self._socket.connect((host, port))
        print(f"{colored('connected to server', 'green')}: Hooray to server!")

        package = {
            'msg': "Hello World!",
            'topic': "greeting"
        }

        self._socket.sendall('{"msg": "Hello World!", "topic": "greeting"}\n'.encode())

        threading.Thread(target = self.receiver).start()


    def send_data(self, data: str) -> None:
        """ Send some data to the server """

        self._socket.sendall(data.encode())
    

    def receiver(self):
        """ Receiver thread for asynchronous communication """

        while True:
            data = self._socket.recv(BUFFER_SIZE).decode()

            if '\n' in data:
                message = Message.receive(json.loads(data.strip()))
                print(f"{colored('server broadcast', 'blue')}: {message.msg}")
    



if __name__ == '__main__':

    try:
        _, host, port = sys.argv
    except:
        # If host and port are not specified, use the default values
        host = DEFAULT_HOST
        port = DEFAULT_PORT

    client = Client(host, int(port))