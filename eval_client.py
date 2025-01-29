from socket import socket, AF_INET, SOCK_STREAM
import sys
from Crypto.Util.Padding import pad
from Crypto.Cipher import AES
import Crypto.Random as Random
import base64

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
    
    def send(self, message):
        encoded_msg = message.encode(self.FORMAT) # Encode message
        padded_data = pad(encoded_msg, self.BLOCK_SIZE) # Pad message
        iv = Random.new().read(AES.block_size) 
        cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
        encoded = base64.b64encode(iv + cipher.encrypt(padded_data))
        msg_length = str(len(encoded)) + "_"
        packet = msg_length.encode(self.FORMAT) + encoded
        print(f"Sending {packet}")
        self.client.send(packet)

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
        if message == client.DISCONNECT_MESSAGE:
            client.client.close()
            break
        client.send(message)

if __name__ == "__main__":
    main()