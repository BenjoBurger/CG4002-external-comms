import threading
import asyncio

class RelayNodeThread:
    def __init__(self, threadId, name):
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.name = name
        
    def run(self, queue, threadLock):
        print("Starting: " + self.name + "\n")
        self.recv_message()
        queue.put()
        print("Exiting: " + self.name + "\n")

    def recv_message(self):
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