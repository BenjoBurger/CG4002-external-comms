from socket import socket, AF_INET, SOCK_STREAM
import sys
from Crypto.Util.Padding import pad
from Crypto.Cipher import AES
import Crypto.Random as Random
import base64

secret_key = b'1111111111111111'

class EvaluationClient:
    def __init__(self, server_name, server_port):
        self.BLOCK_SIZE = 128
        self.FORMAT = "utf-8"
        self.DISCONNECT_MESSAGE = "!dc"
        self.SERVER = server_name
        self.PORT = server_port
        self.ADDR = (self.SERVER, self.PORT)
        self.client = socket(AF_INET, SOCK_STREAM)
        self.client.connect(self.ADDR)
    
    def send(self, message):
        msg_length = len(message)
        msg_length = str(msg_length)
        encoded_data = f"{msg_length}_{message}".encode(self.FORMAT)
        padded_data = pad(encoded_data, self.BLOCK_SIZE)
        print(f"Padding {padded_data}")
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(secret_key,AES.MODE_CBC,iv)
        encoded = base64.b64encode(iv + cipher.encrypt(padded_data))
        print(f"Sending {encoded}")
        self.client.send(encoded)

def main():
    if len(sys.argv) < 3:
        print("Usage: python eval_client.py <server_name> <server_port>")
        sys.exit(1)
    
    server_name = sys.argv[1]
    server_port = int(sys.argv[2])
    client = EvaluationClient(server_name, server_port)
    print("Connected to server")

    while True:
        message = input("> ")
        client.send(message)
        if message == client.DISCONNECT_MESSAGE:
            client.client.close()

if __name__ == "__main__":
    main()