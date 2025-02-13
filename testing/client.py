# remote_bidirectional_client.py
import socket

HOST = "localhost"  # The remote machine's localhost (which forwards to the local machine)
PORT = 9000         # Port to send data to (this is forwarded to the local machine's 8080)

message = "Hello from the remote client!"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((HOST, PORT))
    client_socket.sendall(message.encode())
    print(f"Message sent: {message}")

    # Wait for a response from the local server
    response = client_socket.recv(1024)
    if response:
        print("Received response from local server:", response.decode())