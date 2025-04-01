import asyncio
import json
import time
from socket import socket, AF_INET, SOCK_STREAM, timeout as SocketTimeout, gaierror as GAIError
from utilities.Colour import Colour

class RelayClient:
    def __init__(self, server_name, server_port):
        self.FORMAT = "utf-8"
        self.timeout = 10
        self.SERVER = server_name
        self.PORT = server_port
        self.ADDR = (self.SERVER, self.PORT)
        self.client = None
        self.connected = False
        
        # Connection parameters
        self.max_retries = 3
        self.retry_delay = 5
        
        # Attempt to connect
        self._connect()

    def _connect(self):
        """Attempt to establish a connection to the server"""
        retries = 0
        while retries < self.max_retries:
            try:
                print(f"{Colour.CYAN}Attempting to connect to {self.SERVER}:{self.PORT} (Attempt {retries+1}/{self.max_retries}){Colour.RESET}", end="\n\n")
                self.client = socket(AF_INET, SOCK_STREAM)
                self.client.settimeout(self.timeout)  # Set socket timeout
                self.client.connect(self.ADDR)
                self.connected = True
                print(f"{Colour.GREEN}Successfully connected to {self.SERVER}:{self.PORT}{Colour.RESET}", end="\n\n")
                return True
            except SocketTimeout:
                print(f"{Colour.RED}Connection timed out while trying to connect to {self.SERVER}:{self.PORT}{Colour.RESET}", end="\n\n")
            except ConnectionRefusedError:
                print(f"{Colour.RED}Connection refused by {self.SERVER}:{self.PORT}. Is the server running?{Colour.RESET}", end="\n\n")
            except GAIError:
                print(f"{Colour.RED}Address-related error when connecting to {self.SERVER}:{self.PORT}{Colour.RESET}", end="\n\n")
            except OSError as e:
                print(f"{Colour.RED}OS error when connecting to {self.SERVER}:{self.PORT}: {e}{Colour.RESET}", end="\n\n")
            except Exception as e:
                print(f"{Colour.RED}Unexpected error when connecting to {self.SERVER}:{self.PORT}: {e}{Colour.RESET}", end="\n\n")
            
            # Close socket if it was created
            if self.client:
                try:
                    self.client.close()
                except:
                    pass
                self.client = None
            
            retries += 1
            if retries < self.max_retries:
                print(f"{Colour.YELLOW}Retrying in {self.retry_delay} seconds...{Colour.RESET}", end="\n\n")
                self.PORT += 1  # Increment port for next attempt
                self.ADDR = (self.SERVER, self.PORT)
                time.sleep(self.retry_delay)
                
        # If we got here, we failed to connect after max_retries
        raise ConnectionError(f"Failed to connect to {self.SERVER}:{self.PORT} after {self.max_retries} attempts")

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