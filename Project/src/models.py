import socket
import json
from termcolor import colored

from logger import logger


class Base():

    def __init__(self, data: dict) -> None:
        '''
            constructor

            parameters:
                data (dict): the data used for the payload of the object
        ''' 

        self.payload = data
    

    def get(self, field: str) -> str:
        return self.payload[field] if field in self.payload.keys() else None
    

    @property
    def serialized(self) -> str:
        """ Serialize the payload """
        return json.dumps(self.payload)
    
    @property
    def package(self) -> bytes:
        """ Encode the serialized payload """
        return f'{str(self.serialized)}\n'.encode()    



class Message(Base):
    def __init__(self, data: dict) -> None:
        '''
            constructor

            parameters:
                data (dict): the data used for the payload of the object [message, topics]
        '''
        super().__init__(data)
    

    @classmethod
    def initialize(cls, message: str, topic: str):
        """
            Overlaod the initialize method to construct the payload

            parameters:
                message (str): the emssage for the payload
                topic (str): the topic for the payload's message
        """

        return cls({
            'message': message,
            'topic': topic,
            'type': 'message'
        })


    @logger(on_success = f'{colored("succeess", "green")}\n', on_failure = f'{colored("failed", "red")}\n')
    def send(self, pid: int, socket: socket) -> None:
        '''
            Send the message to the given socket

            parameters:
                pid (int): the pid of the client
                socket (socket): the socket to send the message to                
        '''

        print(f' - sending message to {pid}', end = ': ')
        socket.sendall(self.package)
    

    def broadcast(self, clients: dict) -> None:
        '''
            Broadcast the message to all clients

            parameters:
                clients (dict): the clients to broadcast to
        '''

        for pid, socket in clients:            
            self.send(pid, socket)

        print('')



class Subscribe(Base):

    def __init__(self, data: dict) -> None:
        '''
            Constructor
            
            parameters:
                data (dict): the data used for the payload of the object [topics]
        '''
        super().__init__(data)
    

    @classmethod
    def initialize(cls, topics: list):
        """
            Overlaod the initialize method to construct the payload

            parameters:
                topics (list): list of topics to subscribe to
        """

        return cls({
            'topics': topics,
            'type': 'subscribe'
        })
    

    @logger(on_success = f'{colored("succeess", "green")}', on_failure = f'{colored("failed", "red")}')
    def send(self, socket: socket) -> None:
        '''
            Send the message to the given socket

            parameters:
                socket (socket): the socket to send the message to
        '''

        print(f' - Subscribing on {", ".join(self.payload["topics"])}', end = ': ')
        socket.sendall(self.package)