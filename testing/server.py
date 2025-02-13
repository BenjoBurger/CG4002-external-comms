# local_bidirectional_server.py
import socket

HOST = "localhost"  # Listen on your local machine
PORT = 8080         # Port to listen on (forwarded from remote machine)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Local server listening on {HOST}:{PORT}...")

    while True:
        conn, addr = server_socket.accept()
        with conn:
            print(f"Connected by {addr}")
            data = conn.recv(1024)
            if data:
                print("Received from remote:", data.decode())

                # Send a response back to the remote client
                response = "Hello from the local server!"
                conn.sendall(response.encode())
                print("Sent response:", response)