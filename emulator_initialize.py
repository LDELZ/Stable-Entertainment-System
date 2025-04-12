import os
import requests
import zipfile
import urllib.request
import subprocess
import time
import io

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
ROM_PATCH_PATH = os.path.join(SCRIPT_DIR, "snes9x/Roms/smw_patched.sfc")
LUA_SCRIPT = os.path.join(SCRIPT_DIR, "lua_server.lua")
ROMS_FOLDER = os.path.join(EXTRACT_PATH, "Roms")
COLOR_IMAGE_PATH = "snes9x/Screenshots/smw000.png"
CONFIGURATION_PATH = "snes9x/snes9x.cfg"

LUA_INSTALLER_URL = "https://github.com/rjpcomputing/luaforwindows/releases/download/v5.1.5-52/LuaForWindows_v5.1.5-52.exe"
LUA_INSTALLER_NAME = "LuaForWindows_v5.1.5-52.exe"
LUA_EXPECTED_PATH = r"C:\Program Files (x86)\Lua\5.1"
FLIPS_EXE = "flips.exe"
FLIPS_DIR = "flips"
FLIPS_PATH = os.path.join(FLIPS_DIR, FLIPS_EXE)
FLIPS_URL = "https://dl.smwcentral.net/11474/floating.zip"


def main():
    # Check for emulator executable and install if not available
    get_emulator()
    create_roms_folder()
    create_screenshots_folder()
    create_saves_folder()
    
    # Start emulator briefly to generate config files
    process = subprocess.Popen([SNES9X_EXE])
    time.sleep(1)
    process.terminate()
    process.wait()

    # Configure emulator hotkeys and paths
    set_hotkey(CONFIGURATION_PATH, "ReloadLuaScript", "Backspace")
    set_hotkey(CONFIGURATION_PATH, "MovieRecord", "M")
    set_last_lua_script(CONFIGURATION_PATH, LUA_SCRIPT)
    set_cfg_option(CONFIGURATION_PATH, "MovieDefaultStartFromReset", "FALSE")
    set_cfg_option(CONFIGURATION_PATH, "MessageDisplayTime", 0)
    test_lua_socket_paths()

    # Ensure ROM exists
    while not os.path.isfile(ROM_PATH):
        print(f"ROM file is missing. Please place 'smw.sfc' in: {ROMS_FOLDER}")
        input("Once the file is there, press Enter to continue...")

    print("ROM found!")

    # Patch the ROM if needed
    flips_path = create_flips_folder()
    if not os.path.isfile(ROM_PATCH_PATH):
        print("Patching ROM...")
        patch_game(flips_path)
        print("Patch complete.")
    else:
        print("Patched ROM found")

    print("Emulator initialized!")

def patch_game(flips_path):

    bps_patch = "patch.bps"
    input_rom = r"snes9x\Roms\smw.sfc"
    output_rom = r"snes9x\Roms\smw_patched.sfc"
    cmd = [
        flips_path,
        "--apply",
        bps_patch,
        input_rom,
        output_rom
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    # Output results
    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)

def create_flips_folder():
    if os.path.exists(FLIPS_PATH):
        print("FLIPS already present.")
        return FLIPS_PATH

    print("Downloading FLIPS...")
    os.makedirs(FLIPS_DIR, exist_ok=True)
    r = requests.get(FLIPS_URL)
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        for name in z.namelist():
            if name.endswith(FLIPS_EXE):
                z.extract(name, FLIPS_DIR)
                print(f"Extracted {name} to {FLIPS_DIR}")
                return FLIPS_PATH


def set_cfg_option(cfg_path, option_name, new_value):

    updated_lines = []
    option_found = False

    with open(cfg_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        if line.strip().startswith(option_name):
            key = line.split('=')[0].rstrip()
            updated_lines.append(f"{key} = {new_value}\n")
            option_found = True
        else:
            updated_lines.append(line)

    if not option_found:
        updated_lines.append(f"{option_name} = {new_value}\n")

    with open(cfg_path, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)

    print(f"Set {option_name} = {new_value}")

def set_last_lua_script(cfg_path, script_path):
    with open(cfg_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    updated_lines = []
    key_found = False

    for line in lines:
        if line.strip().startswith("LastScriptFile"):
            updated_line = f"LastScriptFile = {script_path}\n"
            updated_lines.append(updated_line)
            key_found = True
        else:
            updated_lines.append(line)

    if not key_found:
        updated_lines.append(f"LastScriptFile = {script_path}\n")

    with open(cfg_path, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)

    print(f"Set LastScriptFile to: {script_path}")

def download_lua_installer():
    if not os.path.exists(LUA_INSTALLER_NAME):
        print("Downloading Lua for Windows...")
        urllib.request.urlretrieve(LUA_INSTALLER_URL, LUA_INSTALLER_NAME)
        print("Download complete.")
    else:
        print("Installer already downloaded.")
    subprocess.run([LUA_INSTALLER_NAME], check=True)

    if os.path.exists(LUA_INSTALLER_NAME):
        os.remove(LUA_INSTALLER_NAME)
        print("Installer deleted after installation.")

def test_lua_socket_paths():
    lua_paths = [
        "C:/Program Files (x86)/Lua/5.1/lua/socket.lua",
        "C:/Program Files (x86)/Lua/5.1/clibs/socket/core.dll",
    ]

    all_exist = True
    for path in lua_paths:
        if os.path.exists(path):
            print(f"Found: {path}")
        else:
            print(f"Missing: {path}")
            all_exist = False
            download_lua_installer()
    return all_exist

def set_hotkey(cfg_path, hotkey_name, new_value):
    key_line_prefix = f"Key:{hotkey_name}"
    key_found = False

    with open(cfg_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    updated_lines = []
    for line in lines:
        if line.strip().startswith(key_line_prefix):
            # preserve original spacing
            spaces = line.split('=')[0].rstrip()
            updated_line = f"{spaces} = {new_value}\n"
            updated_lines.append(updated_line)
            key_found = True
        else:
            updated_lines.append(line)

    if not key_found:
        updated_lines.append(f"Key:{hotkey_name}   = {new_value}\n")

    with open(cfg_path, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)

    print(f"Updated hotkey: {hotkey_name} to {new_value}")

def create_roms_folder():
    """Create a 'Roms' folder inside the SNES9x extracted directory if it doesn't exist."""
    roms_path = os.path.join(EXTRACT_PATH, "Roms")
    
    if not os.path.exists(roms_path):
        os.makedirs(roms_path)
        
    return roms_path

def create_saves_folder():
    """Create a 'saves' folder inside the SNES9x extracted directory if it doesn't exist."""
    saves_path = os.path.join(EXTRACT_PATH, "Saves")
    
    if not os.path.exists(saves_path):
        os.makedirs(saves_path)

    return saves_path

def create_screenshots_folder():
    """Create a 'Screenshots' folder inside the SNES9x extracted directory if it doesn't exist."""
    roms_path = os.path.join(EXTRACT_PATH, "Screenshots")
    
    if not os.path.exists(roms_path):
        os.makedirs(roms_path)

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
    