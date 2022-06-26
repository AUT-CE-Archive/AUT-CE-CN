import socket
import json
from termcolor import colored


class Message():
    """
        Message class
    """

    def __init__(self, msg: str, topic: str) -> None:
        '''
            constructor

            parameters:
                msg (str): the message
                topic (str): the topic for the message
        '''

        self.msg = msg
        self.topic = topic 


    @classmethod
    def receive(cls, data: dict):
        '''
            Interpret the raw data and set the message and topic

            parameters:
                raw_data (bytes): the raw data
        '''

        return cls(data['msg'], data['topic'])


    def send(self, pid: int, socket: socket) -> None:
        '''
            Send the message to the given socket

            parameters:
                socket (socket): the socket to send the message to
        '''

        serialized = json.dumps({
            'msg': self.msg,
            'topic': self.topic
        })
        
        print(f' - sending message to client {pid}', end = ': ')

        try:
            socket.sendall(f'{str(serialized)}\n'.encode())
            print(f'{colored("succeess", "green")}')
        except:
            print(f'{colored("failed", "red")}')
    

    def broadcast(self, clients: dict) -> None:
        '''
            Broadcast the message to all clients

            parameters:
                clients (dict): the clients to broadcast to
        '''

        for pid, socket in clients:
            self.send(pid, socket)
        print('')











class Model():

    def __init__(self, socket: socket.socket, address: str) -> None:
        
        self.socket = socket
        self.address = address
    

    def json2str(self, data: str) -> str:
        """ Convert the string to json """
        
        return json.loads(data)
    
    
    def json_encode(self, data: str) -> str:
        """ Convert the string from json """
        
        return json.dumps(data)
    

    def json_decode(self, data: str) -> None:
        """ Send JSON serialized data """
        
        self.socket.send(data.encode())
    

    def send(self, data: str) -> None:
        """ Send data """
        
        self.socket.send(data.encode())



class Subscribe(Model):

    def __init__(self, socket: socket.socket, address) -> None:
        
        super().__init__(socket, address)
    

    def send(self) -> None:
        pass


    def response_failure(self) -> None:
        pass

    def response_success(self) -> None:
        pass



class Pong(Model):

    def __init__(self, socket: socket.socket, address) -> None:
        
        super().__init__(socket, address)

        self.package = {
            'type': 'Pong'
        }


    def response_failure(self) -> None:
        pass

    def response_success(self) -> None:
        pass