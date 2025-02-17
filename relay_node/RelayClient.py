from socket import socket, AF_INET, SOCK_STREAM
import asyncio
from utilities.Colour import Colour

class RelayClient:
    def __init__(self, server_name, server_port):
        self.FORMAT = "utf-8"
        self.SERVER = server_name
        self.PORT = server_port
        self.ADDR = (self.SERVER, self.PORT)
        self.client = socket(AF_INET, SOCK_STREAM)
        self.client.connect(self.ADDR)
        print(f"{Colour.CYAN}Relay Client Connected{Colour.RESET}", end="\n\n")

    def send_message(self, message):
        self.client.send(f"{len(message)}_{message}".encode(self.FORMAT))

    def recv_message(self):
        msg = ""
        try:
            while True:
                # get length of message            
                data = b''
                while not data.endswith(b'_'):
                    _d = self.client.recv(1)
                    if not _d:
                        data = b''
                        break
                    data += _d
                if len(data) == 0:
                    break
                data = data.decode(self.FORMAT)
                length = int(data[:-1])
                data = b''
                # get message
                while len(data) < length:
                    _d = self.client.recv(length - len(data))
                    if not _d:
                        data = b''
                        break
                    data += _d
                if len(data) == 0:
                    break
                msg = data.decode(self.FORMAT)
                break
        except ConnectionResetError:
            print(f'{Colour.RED}recv_text: Connection Reset{Colour.RESET}', end="\n\n")
        except asyncio.TimeoutError:
            print(f'{Colour.RED}recv_text: Timeout while receiving data{Colour.RESET}', end="\n\n")

        return msg
    
    def close(self):
        self.client.close()
        print(f"{Colour.CYAN}Relay Client Closed{Colour.RESET}", end="\n\n")