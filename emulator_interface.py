import os
import requests
import zipfile
import subprocess
from pynput.keyboard import Controller, Key
import time
from PIL import Image
import socket

FILENAME = "snes9x-1.51-rerecording-v7.1-win32.zip"
DOWNLOAD_URL = "https://github.com/TASEmulators/snes9x-rr/releases/download/snes9x-151-v7.1/snes9x-1.51-rerecording-v7.1-win32.zip"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXTRACT_FOLDER = "snes9x"
os.chdir(SCRIPT_DIR)
SAVE_PATH = os.path.join(os.getcwd(), FILENAME)
ZIP_PATH = os.path.join(SCRIPT_DIR, FILENAME)
EXTRACT_PATH = os.path.join(SCRIPT_DIR, EXTRACT_FOLDER)
SNES9X_EXE = os.path.join(EXTRACT_PATH, "snes9x.exe")
ROM_PATH = os.path.join(SCRIPT_DIR, "snes9x/Roms/smw.sfc")
LUA_SCRIPT = os.path.join(SCRIPT_DIR, "bot.lua")
ROMS_FOLDER = os.path.join(EXTRACT_PATH, "Roms")
NUM_FRAMES = 5
CONFIG_PATH = "snes9x.cfg"
COLOR_IMAGE_PATH = "snes9x/Screenshots/smw000.png"
keyboard = Controller()
HOST = "127.0.0.1"
PORT = 65432

def main():
    # Check for emulator executable and install if not available
    # Create required folder paths and start emulator
    get_emulator()
    create_roms_folder()
    create_screenshots_folder()
    create_saves_folder()
    start_snes9x()

    # Wait for emulator to load
    # Uncomment the following line to load the save state if one exists
    time.sleep(6)
    #button_short_press(Key.f1)

    # Create a starting screenshot to overwrite each advance
    button_short_press(Key.f12)
    
    # Open the client python script in a subprocess. This is where the AI code should be
    subprocess.Popen(["python", "client.py"])

    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)

    print(f"Listening for connections on {HOST}:{PORT}...")
    conn, addr = server_socket.accept()
    print(f"Connected by {addr}")

    # Execute advance frames to put emulator in frame advance mode
    button_short_press("\\")
    button_short_press(Key.ctrl_r)

    print("Press right ctrl key to advance frames...")
    while True:
        try:
            while True:
                data = conn.recv(1024).decode().strip()
                if not data:
                    break
                print(f"Received input: {data}")

                # Set flag if "delete" command is received
                if data == "Key.ctrl_r":
                    print("Advance message received, advancing frames now...")
                    # Check if the file exists before deleting it
                    if os.path.exists(COLOR_IMAGE_PATH):
                        os.remove(COLOR_IMAGE_PATH)

                    # Advance n frames
                    for _ in range(NUM_FRAMES):
                        button_short_press("\\")

                    # Save the current screenshot to Screenshots folder & convert to grayscale
                    button_short_press(Key.f12)
                    time.sleep(1)
                    convert_grayscale()

        except KeyboardInterrupt:
                print("Server shutting down.")
                conn.close()
                server_socket.close()
                return

def convert_grayscale():
    # Ensure the color image exists before processing
    if not os.path.exists(COLOR_IMAGE_PATH):
        print(f"Warning: Color image not found at {COLOR_IMAGE_PATH}")
        return

    # Load the original image
    image = Image.open(COLOR_IMAGE_PATH)

    # Convert to grayscale
    gray_image = image.convert("L")

    # Overwrite the original file with the grayscale version
    gray_image.save(COLOR_IMAGE_PATH)  # Saves over the color image

    print(f"Replaced {COLOR_IMAGE_PATH} with its grayscale version")


def button_short_press(button):
    keyboard.press(button)
    time.sleep(0.05)
    keyboard.release(button)

def button_timed_press(button, duration):
    keyboard.press(button)
    time.sleep(duration)
    keyboard.release(button)

def button_hold(button):
    keyboard.press(button)

def button_release(button):
    keyboard.release(button)

def start_snes9x():
    """Launch SNES9x with a ROM and a Lua script."""
    
    if not os.path.exists(ROMS_FOLDER):
        os.makedirs(ROMS_FOLDER)
        print(f"'Roms' folder created at: {ROMS_FOLDER}")

    while not os.path.isfile(ROM_PATH):
        print(f"ROM file is missing. Please place 'smw.sfc' in {ROMS_FOLDER}.")
        input("Press Enter after adding the ROM file...")

    if not os.path.isfile(LUA_SCRIPT):
        print(f"Warning: Lua script '{LUA_SCRIPT}' not found. Running without it.")
        subprocess.Popen([SNES9X_EXE, ROM_PATH], cwd=EXTRACT_PATH)
    else:
        print(f"Launching SNES9x with ROM: {ROM_PATH} and Lua script: {LUA_SCRIPT}")
        subprocess.Popen([SNES9X_EXE, "-lua", LUA_SCRIPT, ROM_PATH], cwd=EXTRACT_PATH)

def create_roms_folder():
    """Create a 'Roms' folder inside the SNES9x extracted directory if it doesn't exist."""
    roms_path = os.path.join(EXTRACT_PATH, "Roms")
    
    if not os.path.exists(roms_path):
        os.makedirs(roms_path)
        print(f"'Roms' folder created at: {roms_path}")
    else:
        print(f"'Roms' folder already exists at: {roms_path}")

    return roms_path

def create_saves_folder():
    """Create a 'saves' folder inside the SNES9x extracted directory if it doesn't exist."""
    saves_path = os.path.join(EXTRACT_PATH, "Saves")
    
    if not os.path.exists(saves_path):
        os.makedirs(saves_path)
        print(f"'Saves' folder created at: {saves_path}")
    else:
        print(f"'Saves' folder already exists at: {saves_path}")

    return saves_path

def create_screenshots_folder():
    """Create a 'Screenshots' folder inside the SNES9x extracted directory if it doesn't exist."""
    roms_path = os.path.join(EXTRACT_PATH, "Screenshots")
    
    if not os.path.exists(roms_path):
        os.makedirs(roms_path)
        print(f"'Screenshots' folder created at: {roms_path}")
    else:
        print(f"'Screenshots' folder already exists at: {roms_path}")

    return roms_path

def get_emulator():
    print(f"Current working directory set to: {os.getcwd()}")
    if is_snes9x_present():
        print("SNES9x is ready to use!")
    else:
        print("SNES9x.exe is missing! Downloading required emulator")
        if not is_zip_present():
            download_file()
        extract_zip()

def is_snes9x_present():
    """Check if snes9x.exe is in the extracted directory."""
    print("Checking for snes9x.exe")
    if os.path.isfile(SNES9X_EXE):
        print(f"SNES9x found at: {SNES9X_EXE}")
        return True
    else:
        print(f"SNES9x is NOT found in {EXTRACT_PATH}")
        return False

def download_file():
    """Download SNES9x ZIP into the current directory."""
    print(f"Downloading {FILENAME} to {SAVE_PATH}...")

    response = requests.get(DOWNLOAD_URL, stream=True)
    if response.status_code == 200:
        with open(SAVE_PATH, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Download complete: {SAVE_PATH}")
    else:
        print(f"Failed to download. HTTP Status Code: {response.status_code}")

def is_zip_present():
    """Check if the SNES9x ZIP file is in the current directory."""
    if os.path.isfile(SAVE_PATH):
        print(f"File is present at: {SAVE_PATH}")
        return True
    else:
        print(f"File NOT found in current directory: {SAVE_PATH}")
        return False

def extract_zip():
    """Extract SNES9x ZIP file into the script's directory and delete the ZIP afterward."""
    if not os.path.exists(EXTRACT_PATH):
        os.makedirs(EXTRACT_PATH)

    print(f"Extracting {FILENAME} to {EXTRACT_PATH}...")

    with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
        zip_ref.extractall(EXTRACT_PATH)

    print(f"Extraction complete! Files are in: {EXTRACT_PATH}")

    if os.path.isfile(ZIP_PATH):
        os.remove(ZIP_PATH)
        print(f"Deleted ZIP file: {ZIP_PATH}")
    else:
        print("ZIP file not found for deletion.")

if __name__ == "__main__":
    main()
    