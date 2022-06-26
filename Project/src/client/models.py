import socket
import json


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



class Ping(Model):

    def __init__(self, socket: socket.socket, address) -> None:
        
        super().__init__(socket, address)

        self.package = {
            'type': 'Ping'
        }


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