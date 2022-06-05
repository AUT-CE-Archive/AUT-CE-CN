import os
import socket
import threading
from dotenv import load_dotenv

load_dotenv() # Load .env file

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
BUFFER_SIZE = int(os.getenv("BUFFER_SIZE"))


class Server():

    def __init__(self) -> None:

        # Create socket with IPv4 address
        self._socket =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind on the Host & Port, and start listening
        self._socket.bind((HOST, PORT))
        self.listen()
    

    def listen(self):
        """ Constantly listen for incoming connections """
        
        # Start listening for incoming connections
        self._socket.listen()

        while True:
            client, address = self._socket.accept()
            # client.settimeout(60)
            threading.Thread(target = self.client_handler, args = (client, address)).start()
    

    def client_handler(self, client: socket.socket, address):
        """
            Handle the client connection through a thread

            Parameters:
                client (socket.socket): The client socket
                address (socket._RetAddress): The client address            
            Returns:
                False when the client is disconnected
        """

        while True:
            try:
                data = client.recv(BUFFER_SIZE)
                if data:
                    client.send(data)   # Echo back
                else:
                    raise Exception('Client disconnected')
            except:
                client.close()
                return False



if __name__ == '__main__':
    server = Server()