import socket
import json
from termcolor import colored

from logger import logger


class Base(object):

    def __init__(self, data: dict) -> None:
        self.payload = data
    

    def get(self, field: str) -> str:
        """ getter """
        return self.payload[field] if field in self.payload.keys() else None


    @logger(on_success = f'{colored("succeess", "green")}\n', on_failure = f'{colored("failed", "red")}\n')
    def send(self, pid: int, socket: socket) -> None:
        '''
            Send the message to the given socket

            parameters:
                pid (int): the pid of the client
                socket (socket): the socket to send the message to                
        '''

        socket.sendall(self.package)


    def send_ack(self, pid: int, socket: socket) -> None:
        '''
            Send acknowledgement to the client

            parameters:
                pid (int): the pid of the client
                socket (socket): the socket to send the message to
        '''

        print(f'- sending acknowledgement for the received {self.get("type")}', end = ': ')
        Ack.initialize(self.get("type")).send(pid, socket)
    

    @property
    def serialized(self) -> str:
        """ Serialize the payload """
        return json.dumps(self.payload)
    
    @property
    def package(self) -> bytes:
        """ Encode the serialized payload """
        return f'{str(self.serialized)}\n'.encode()


class Ack(Base):

    def __init__(self, data: dict) -> None:
        super().__init__(data)
    

    @classmethod
    def initialize(cls, kind: str):
        """
            Overlaod the initialize method to construct the payload

            parameters:
                kind (str): the kind of acknowledgement to send
        """

        return cls({
            'type': 'acknowledgement',
            'kind': kind
        })


    def notify(self) -> None:
        """
            Notify the user that the ack has been received
        """

        kinds = {
            'subscribe': 'subscription acknowledgement received',
            'message': 'message acknowledgement received'
        }

        print(f"\n{colored('server', 'blue')}: {kinds[self.payload.get('kind')]}")



class Message(Base):
    def __init__(self, data: dict) -> None:
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
    

    def broadcast(self, clients: dict) -> None:
        '''
            Broadcast the message to all clients

            parameters:
                clients (dict): the clients to broadcast to
        '''

        for pid, socket in clients:
            print(f'  - sending to clinet {pid}', end = ': ')
            self.send(pid, socket)
    

    def show_broadcast(self) -> None:
        '''
            Show the broadcast message
        '''

        print(f"\n{colored('server broadcast', 'blue')}: {self.get('message')}")
    

    def get_ack(self) -> Ack:
        """
            Get the acknowledgement for the message
        """

        return Ack.initialize('message')



class Subscribe(Base):

    def __init__(self, data: dict) -> None:
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
    

    def to_topics(self, client: dict) -> dict:
        """
            subscribe the given client to the topics in the payload
        """

        client['topics'] = self.payload.get('topics')
        print(f'- subscribed to {", ".join(client["topics"])}')

        return client



class PingPong(Base):

    def __init__(self, data: dict) -> None:
        super().__init__(data)
    

    @classmethod
    def initialize(cls, kind: str = 'ping', count: int = 0):
        """
            Overlaod the initialize method to construct the payload
        """

        return cls({
            'type': 'pingpong',
            'kind': kind,
            'count': count
        })
    
    def update(self):
        """
            Update the payload with the new count
        """

        if self.get('kind') == 'pong':
            self.payload['count'] += 1
    

    @property
    def pid(self) -> int:
        return self.payload['pid']
    

    @property
    def count(self) -> int:
        return self.payload['count']