import socket
import json

HOST = "127.0.0.1"
PORT = 65432

# Example list of inputs
inputs_to_send = ['START', 'START', 'START']

# Convert list to JSON string
message = json.dumps(inputs_to_send)  

# Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Send the JSON-encoded list
client_socket.sendall(message.encode())
print(f"Sent: {message}")

# Close the connection
client_socket.close()
