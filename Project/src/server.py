import os
import sys
import time
import json
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
            print(f'{colored(f"client {pid}", "white")}: {colored("connected", "green")}')

            # Add the client to the clients dictionary to keep track of
            self.clients[pid] = {
                'socket': client,
                'host': host,
                'topics': ['greeting'],
                'pingpong': {
                    'start': False,
                    'last_ping': None,
                    'count': 0,
                    'pid': None
                },
                'connected': True
            }

            threading.Thread(target = self.client_handler, args = (client, pid)).start()            
            threading.Thread(target = self.ping_pong, args = ()).start()
    

    def ping_pong(self):

        while True:
            print(colored('Pinging clients...', 'magenta'))

            for pid, props in self.clients.items():
                
                # Skip disconnected clients
                if not self.clients[pid]['connected']: continue

                # If not reply is received within the TIMEOUT, then increase COUNT
                if self.clients[pid]['pingpong']['start'] and self.clients[pid]['pingpong']['last_ping'] - time.time() > TIMEOUT:
                    self.clients[pid]['pingpong']['count'] += 1
                    print(f"- {colored(f'client {pid}', 'yellow')}: ping-pong failed (count = {self.clients[pid]['pingpong']['count']})")
                

                # Disconnect the client if the COUNT is greater than 3
                if self.clients[pid]['pingpong']['count'] == 3:
                    self.clients[pid]['connected'] = False
                    print(f"- {colored(f'client {pid}', 'red')}: diconnected [reason: ping-pong failed for 3 times]")

                self.clients[pid]['pingpong']['last_ping'] = time.time() # Record time before sending ping
                self.clients[pid]['pingpong']['start'] = True
                
                # Send the ping
                print('- pinged the client:', pid, end = ' - ')
                PingPong.initialize().send(pid, props['socket'])

            time.sleep(TIMEOUT)


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
                for segment in [s for s in package.split('\n') if s != '']:

                    data = json.loads(segment)
                    print(f'{colored(f"client {pid}", "white")}: {data}.')

                    if data['type'] == 'subscribe':
                        subscribe = Subscribe(data)

                        # Subscribe user to the topics
                        self.clients[pid] = subscribe.to_topics(self.clients[pid])

                        # Send acknowledgement
                        subscribe.send_ack(pid, self.clients[pid]['socket'])

                    elif data['type'] == 'message':
                        message = Message(data)

                        # Send acknowledgement
                        message.send_ack(pid, self.clients[pid]['socket'])

                        # list of client PIDs that are subscribed to the topic (except the sender himself)
                        subscribed_clients = [(_pid, props['socket']) for _pid, props in self.clients.items() if props['connected'] and _pid != pid and message.get('topic') in props['topics']]
                        print(f'- The following clients are subscribed to this topic: {[_pid for _pid, _ in subscribed_clients]}. broadcasting now...')

                        # broadcast the message to all subscribed clients
                        message.broadcast(subscribed_clients)
                    
                    elif data['type'] == 'pingpong':
                        pingpong = PingPong(data)

                        if pingpong.get('kind') == 'pong':
                            self.clients[pingpong.pid]['pingpong']['last_ping'] = time.time()   # Record time after receiving pong
                            self.clients[pingpong.pid]['pingpong']['count'] = 0                 # Reset the COUNT




if __name__ == '__main__':

    server = Server(HOST, int(PORT))