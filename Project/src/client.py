import os
import sys
import json
import time
import socket
import threading
from termcolor import colored
from dotenv import load_dotenv

from models import *

load_dotenv() # Load .env file

# Environment variables (constants)
BUFFER_SIZE = int(os.getenv("BUFFER_SIZE"))
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
TIMEOUT = int(os.getenv('TIMEOUT'))


class Client():
    """ Initialize the client """

    def __init__(self, host: str, port: int, topics: list) -> None:

        self.host = host
        self.port = port
        self.topics = topics
        self.await_ack_time = time.time()

        # Create socket with IPv4 address
        self._socket =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"{colored('client started', 'blue')} (PID: {port}): listening on {host}:{port}...")

        # Establish a connection to the server
        self._socket.connect((host, port))
        print(f"{colored(f'server', 'white')}: {colored('connected', 'green')}")

        # Subscribe to topics
        print(f'subscribing to server on {", ".join(topics)}', end = ': ')
        Subscribe.initialize(
            topics = topics
        ).send(port, self._socket)
        self.await_ack_time = time.time()

        threading.Thread(target = self.listener).start()
        threading.Thread(target = self.timeout).start()

        while True:
            # Read input from user
            topic, message = [token.strip() for token in input('Write message to broadcast in format of TOPIC:MESSAGE: ').split(':')]

            # Transmit message to server
            print(f'transmitting message to server', end = ': ')
            Message.initialize(
                message = message,
                topic = topic
            ).send(port, self._socket)
            self.await_ack_time = time.time()


    def timeout(self):
        """ Timeout thread for asynchronous communication """

        while True:
            if self.await_ack_time is not None and time.time() - self.await_ack_time > TIMEOUT:
                print(f'{colored(f"server", "white")}:" {colored("timeout", "red")}')
                sys.exit()
            time.sleep(TIMEOUT)

    
    def listener(self):
        """ Listener thread for asynchronous communication """

        while True:
            package = self._socket.recv(BUFFER_SIZE).decode()

            if '\n' in package:
                for segment in [s for s in package.split('\n') if s != '']:
                    
                    # Serialize
                    data = json.loads(segment.strip())

                    if data['type'] == 'acknowledgement':
                        Ack(data).notify()
                        self.await_ack_time = None

                    elif data['type'] == 'message':
                        Message(data).show_broadcast()                        
                        
    



if __name__ == '__main__':

    client = Client(HOST, PORT, sys.argv[1:])