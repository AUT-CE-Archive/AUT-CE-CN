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


class Server():

    def __init__(self, host: str, port: int) -> None:
        """ Initialize the server """

        self.clients = {}
        self.host = host
        self.port = port

        # Create socket with IPv4 address
        self._socket =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind on the Host & Port, and start listening
        self._socket.bind((host, port))
        self.listen()
    

    def listen(self):
        """ Constantly listen for incoming connections """
        
        # Start listening for incoming connections
        self._socket.listen()

        while True:
            client, address = self._socket.accept()
            host, pid = address

            print(f'{colored("client connected", "green")}: Hooray to {pid}!')

            # Add the client to the clients dictionary to keep track of
            self.clients[pid] = {
                'socket': client,
                'host': host,
                'topics': ['greeting']
            }

            threading.Thread(target = self.client_handler, args = (client, pid)).start()


    def client_handler(self, client: socket.socket, pid: int):
        """
            Handle the client connection through a thread

            Parameters:
                client (socket.socket): The client socket
                pid (int): The client PID
            Returns:
                False when the client is disconnected
        """

        while True:
            try:
                # Read package, decode and serialize
                package = client.recv(BUFFER_SIZE).decode()
                data = json.loads(package)                
                print(f'{colored("package received", "blue")}: client {pid} sent "{data["msg"]}" (topic: "{data["topic"]}").')

                # Get list of client PIDs that are subscribed to the topic
                subscribed_clients = [_pid for _pid in self.clients.keys() if _pid != pid and data['topic'] in self.clients[_pid]['topics']]

                print(f' - The following clients are subscribed to this topic: {subscribed_clients}')

                # Echo to clients that are subscribed to the topic
                for sub_pid in subscribed_clients:
                    print(f'  - sending message to client {sub_pid}:', end = ' ')

                    try:
                        self.clients[sub_pid]['socket'].sendall(data)
                        print(f'{colored("success", "green")}')
                    except:
                        print(f'{colored("failed", "red")}')
            except:
                client.close()
                return False



if __name__ == '__main__':

    try:
        _, host, port = sys.argv
    except:
        # If host and port are not specified, use the default values
        host = DEFAULT_HOST
        port = DEFAULT_PORT

    server = Server(host, int(port))