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
        print(f"{colored(f'server started (PID: {port})', 'blue')}: listening on {host}:{port}...")
        self.listen()        
    

    def listen(self):
        """ Constantly listen for incoming connections """
        
        # Start listening for incoming connections
        self._socket.listen()

        while True:
            client, (host, pid) = self._socket.accept()
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
            
            # Read package, decode and serialize
            package = client.recv(BUFFER_SIZE).decode()

            if package != '':
                data = json.loads(package)
                print(f'client {pid}: {data}.')

                self.broadcaster(pid, data)


    def broadcaster(self, sender_pid: int, data: dict):
        """
            Broadcast the data to all clients

            Parameters:
                sender_pid (int): The PID of the sender
                data (str): The data to broadcast
        """

        # Interpret the data
        message = Message(data)

        # list of client PIDs that are subscribed to the topic (except the sender himself)
        subscribed_clients = [(pid, props['socket']) for pid, props in self.clients.items() if sender_pid != pid and message.get('topic') in props['topics']]
        print(f' - The following clients are subscribed to this topic: {[pid for pid, _ in subscribed_clients]}')

        # broadcast the message to all subscribed clients
        message.broadcast(subscribed_clients)




if __name__ == '__main__':

    try:
        _, host, port = sys.argv
    except:
        # If host and port are not specified, use the default values
        host = DEFAULT_HOST
        port = DEFAULT_PORT

    server = Server(host, int(port))