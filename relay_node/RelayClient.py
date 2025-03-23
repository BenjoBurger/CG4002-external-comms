import asyncio
import json
from socket import socket, AF_INET, SOCK_STREAM, timeout as SocketTimeout
from utilities.Colour import Colour

class RelayClient:
    def __init__(self, server_name, server_port):
        self.FORMAT = "utf-8"
        self.timeout = 10
        self.SERVER = server_name
        self.PORT = server_port
        self.ADDR = (self.SERVER, self.PORT)
        self.client = socket(AF_INET, SOCK_STREAM)
        self.client.connect(self.ADDR)
        # self.client.settimeout(self.timeout)

    def send_message(self, message):
        packet = f"{len(message)}_{message}"
        self.client.send(packet.encode(self.FORMAT))

    def recv_message(self):
        msg = ""
        try:
            while True:
                # recv length followed by '_' followed by cypher
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
        except SocketTimeout:
            print(f"{Colour.RED}recv_text: No response received within {self.timeout} seconds{Colour.RESET}", end="\n\n")
        return msg

    def close(self):
        self.client.close()
        print(f"{Colour.CYAN}Relay Client Closed{Colour.RESET}", end="\n\n")