import asyncio
from socket import socket, AF_INET, SOCK_STREAM
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
import Crypto.Random as Random
import base64
import json
from utilities.Colour import Colour

SECRET_KEY = b'1111111111111111'

class EvaluationClient:
    def __init__(self, server_name, server_port):
        self.BLOCK_SIZE = 16
        self.FORMAT = "utf-8"
        self.SERVER = server_name
        self.PORT = server_port
        self.ADDR = (self.SERVER, self.PORT)
        self.client = socket(AF_INET, SOCK_STREAM)
        self.client.connect(self.ADDR)
        self.send_server("hello")
        print(f"{Colour.ORANGE}Evaluation Client connected{Colour.RESET}", end="\n\n")
    
    def send_server(self, message):
        print(f"{Colour.ORANGE}Sending {message}{Colour.RESET}", end="\n\n")
        encoded_message = message.encode(self.FORMAT)
        padded_data = pad(encoded_message, self.BLOCK_SIZE)
        iv = Random.new().read(AES.block_size) 
        cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
        encoded = base64.b64encode(iv + cipher.encrypt(padded_data))
        msg_length = str(len(encoded)) + "_"
        packet = msg_length.encode(self.FORMAT) + encoded
        self.client.send(packet)

    def recv_message(self):
        msg = ""
        try:
            while True:               
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
            print(f"{Colour.RED}recv_text: Connection Reset{Colour.RESET}", end="\n\n")
        except asyncio.TimeoutError:
            print(f"{Colour.RED}recv_text: Timeout while receiving data{Colour.RESET}", end="\n\n")

        return msg