from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import json
import asyncio
from utilities.Colour import Colour

class RelayServer:
    def __init__(self, server_port):
        self.FORMAT = "utf-8"
        self.timeout = 5
        self.PORT = server_port
        self.ADDR = ('', self.PORT)
        self.client = socket(AF_INET, SOCK_STREAM)
        self.client.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.client.bind(self.ADDR)
        self.client.listen()
        # self.client.settimeout(self.timeout)

    def send_message(self, message, socket):
        json_message = json.dumps(message)
        packet = f"{len(json_message)}_{json_message}"
        socket.send(packet.encode(self.FORMAT))
    
    def recv_message(self, conn_socket):
        msg = ""
        try:
            while True:
                # recv length followed by '_' followed by cypher                    
                data = b''
                while not data.endswith(b'_'):
                    _d = conn_socket.recv(1)
                    if not _d:
                        data = b''
                        break
                    data += _d
                if len(data) == 0:
                    break
                data = data.decode(self.FORMAT)
                length = int(data[:-1])
                data = b''
                while len(data) < length:
                    _d = conn_socket.recv(length - len(data))
                    if not _d:
                        data = b''
                        break
                    data += _d
                if len(data) == 0:
                    break
                msg = data.decode(self.FORMAT)  # Decode raw bytes to UTF-8
                break
        except ConnectionResetError:
            print(f"{Colour.RED}recv_text: Connection Reset{Colour.RESET}", end="\n\n")
        except asyncio.TimeoutError:
            print(f"{Colour.RED}recv_text: No response received within {self.timeout} seconds{Colour.RESET}", end="\n\n")
        return msg