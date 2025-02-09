import asyncio
from socket import socket, AF_INET, SOCK_STREAM
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
import Crypto.Random as Random
import base64
import json

SECRET_KEY = b'1111111111111111'

class EvaluationClient:
    def __init__(self, server_name, server_port):
        self.BLOCK_SIZE = 16
        self.FORMAT = "utf-8"
        self.DISCONNECT_MESSAGE = "!dc"
        self.SERVER = server_name
        self.PORT = server_port
        self.ADDR = (self.SERVER, self.PORT)
        self.client = socket(AF_INET, SOCK_STREAM)
        self.client.connect(self.ADDR)
        self.send_server("hello".encode(self.FORMAT))
        print("Connected to server")
    
    def send_server(self, message):
        print(f"Encoding {message}")
        padded_data = pad(message, self.BLOCK_SIZE)
        iv = Random.new().read(AES.block_size) 
        cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
        encoded = base64.b64encode(iv + cipher.encrypt(padded_data))
        msg_length = str(len(encoded)) + "_"
        packet = msg_length.encode(self.FORMAT) + encoded
        print(f"Sending {packet}")
        self.client.send(packet)

    def recv_server(self):
        """
        This function receives a message from the Ultra96 and decrypts it
        """
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
                data = data.decode("utf-8")
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
                msg = data.decode("utf8")  # Decode raw bytes to UTF-8
                break
        except ConnectionResetError:
            print('recv_text: Connection Reset')
        except asyncio.TimeoutError:
            print('recv_text: Timeout while receiving data')

        return msg