'''
******************************************************************************
 * File:        emulator_initialize.py
 * Author:      Brennan Romero, Luke Delzer
 * Class:       Introduction to AI (CS3820), Spring 2025, Dr. Armin Moin
 * Assignment:  Semester Project
 * Due Date:    04-23-2025
 * Description: This program installs the SNES9x emulator and automates changing
                all of the required configurations necessary for agent control
                from SB3. It installs all required dependencies and prompts the
                user to add the required ROM file manually. All dependencies
                must be installed for full functionality.
 * Usage:       Run this program in a Python 3.11.x or higher environment.
                This program must be executed before attempting to train a
                model.
 ******************************************************************************
 '''

# Imports
import os
import requests
import zipfile
import urllib.request
import subprocess
import time
import io

# Define the paths for saving files, images, savestates, lua scripts, roms, emulator executables, and TCP ports
# Install the SNES9x-rr emulator
FILENAME = "snes9x-1.51-rerecording-v7.1-win32.zip"
DOWNLOAD_URL = "https://github.com/TASEmulators/snes9x-rr/releases/download/snes9x-151-v7.1/snes9x-1.51-rerecording-v7.1-win32.zip"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXTRACT_FOLDER = "snes9x"
os.chdir(SCRIPT_DIR)
SAVE_PATH = os.path.join(os.getcwd(), FILENAME)
ZIP_PATH = os.path.join(SCRIPT_DIR, FILENAME)
EXTRACT_PATH = os.path.join(SCRIPT_DIR, EXTRACT_FOLDER)
SNES9X_EXE = os.path.join(EXTRACT_PATH, "snes9x.exe")

# Prompt the user for othe ROM file. No ROM file is provided for legal purposes
ROM_PATH = os.path.join(SCRIPT_DIR, "snes9x/Roms/smw.sfc")
ROM_PATCH_PATH = os.path.join(SCRIPT_DIR, "snes9x/Roms/smw_patched.sfc")
LUA_SCRIPT = os.path.join(SCRIPT_DIR, "lua_server.lua")
ROMS_FOLDER = os.path.join(EXTRACT_PATH, "Roms")

# Specify the SNES9x-rr configuration file path to update button-mappings
COLOR_IMAGE_PATH = "snes9x/Screenshots/smw000.png"
CONFIGURATION_PATH = "snes9x/snes9x.cfg"

# Install Lua and LuaSocket; these must be installed directly to the Windows environment specified in the wizard
LUA_INSTALLER_URL = "https://github.com/rjpcomputing/luaforwindows/releases/download/v5.1.5-52/LuaForWindows_v5.1.5-52.exe"
LUA_INSTALLER_NAME = "LuaForWindows_v5.1.5-52.exe"
LUA_EXPECTED_PATH = r"C:\Program Files (x86)\Lua\5.1"
FLIPS_EXE = "flips.exe"
FLIPS_DIR = "flips"
FLIPS_PATH = os.path.join(FLIPS_DIR, FLIPS_EXE)
FLIPS_URL = "https://dl.smwcentral.net/11474/floating.zip"

'''
------------------------------------------------------------------------------
* Function: main
* --------------------
* Description:
*	Installs the emulator, creates all required emulation directories, opens
    an emulator instance as a subprocess to initialize configurartion files,
    checks for the ROM file, updates all configuration files to agent-specific
    requirements necessary for socket communication and automated control,
    patches the ROM file to implement the custom training level.

*
* Arguments:   none
* Returns:     none
'''
def main():
    # Check for emulator executable and install if not available
    get_emulator()

    # Create the necessary emulator folders
    create_roms_folder()
    create_screenshots_folder()
    create_saves_folder()
    
    # Start emulator briefly to generate config files
    process = subprocess.Popen([SNES9X_EXE])
    time.sleep(1)
    process.terminate()
    process.wait()

    # Configure emulator hotkeys and paths in the configuration file
    set_hotkey(CONFIGURATION_PATH, "ReloadLuaScript", "Backspace")
    set_hotkey(CONFIGURATION_PATH, "MovieRecord", "M")
    set_last_lua_script(CONFIGURATION_PATH, LUA_SCRIPT)
    set_cfg_option(CONFIGURATION_PATH, "MovieDefaultStartFromReset", "FALSE")
    set_cfg_option(CONFIGURATION_PATH, "MessageDisplayTime", 0)

    # Test if LuaSocket is installed and install irt if not
    test_lua_socket_paths()

    # Check that the ROM file exists; prompt the user to provide it if not
    while not os.path.isfile(ROM_PATH):
        print(f"ROM file is missing. Please place 'smw.sfc' in: {ROMS_FOLDER}")
        input("Once the file is there, press Enter to continue...")
    print("ROM found!")

    # Patch the ROM if needed using the 'flips' patcher
    flips_path = create_flips_folder()
    if not os.path.isfile(ROM_PATCH_PATH):
        print("Patching ROM...")
        patch_game(flips_path)
        print("Patch complete.")
    else:
        print("Patched ROM found")

    # Signal that the emulator is correctly initialized
    print("Emulator initialized!")

'''
------------------------------------------------------------------------------
* Function: patch_game
* --------------------
* Description:
*	Open 'flips' as a subprocess and specify the original ROM file and patch
    file in order to patch the ROM with the custom training level.
*
* Arguments:   The directory path to the 'flips' patcher
* Returns:     none
'''
def patch_game(flips_path):

    # Specify the paths to the ROM, patch file, and flips patcher
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

    # Open flips as a subprocess and patch the ROM
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Output the patch status to output or error logs for odebugging
    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)

'''
------------------------------------------------------------------------------
* Function: create_flips_folder
* --------------------
* Description:
*	Creates the directory for the 'flips' ROM patcher and downloads 'flips'
    if not already present.
*
* Arguments:   none
* Returns:     none
'''
def create_flips_folder():

    # Check if 'flips' is already installed
    if os.path.exists(FLIPS_PATH):
        print("FLIPS already present.")
        return FLIPS_PATH

    # Download and install 'flips' if not
    print("Downloading FLIPS...")
    os.makedirs(FLIPS_DIR, exist_ok=True)
    r = requests.get(FLIPS_URL)
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        for name in z.namelist():
            if name.endswith(FLIPS_EXE):
                z.extract(name, FLIPS_DIR)
                print(f"Extracted {name} to {FLIPS_DIR}")
                return FLIPS_PATH

'''
------------------------------------------------------------------------------
* Function: set_cfg_option
* --------------------
* Description:
*	Opens the SNES9x-rr configuration file and changes a line in the file.
    SNES9x-rr uses a text configuration file for specifying hotkeys and inputs.
    Changing this file ensures that the desired control buttons and paths to Lua
    files are defined. This enables full automation without user configuration
    of directories and hotkeys. Hotkey remapping is required to prevent overlap
    with SB3 controls. Lua path specification is required to automatically
    load a Lua script at startup.
*
* Arguments:   Configuration file path, the option to change, the new option value
* Returns:     none
'''
def set_cfg_option(cfg_path, option_name, new_value):

    updated_lines = []
    option_found = False

    # Open the configuration file in read mode
    with open(cfg_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Search for the option name to change
    
    for line in lines:
        if line.strip().startswith(option_name):
            key = line.split('=')[0].rstrip()
            updated_lines.append(f"{key} = {new_value}\n")
            option_found = True
        else:
            updated_lines.append(line)

    # If it does not exist, add the option as a new line to the bottom
    if not option_found:
        updated_lines.append(f"{option_name} = {new_value}\n")

    # Now open the configuration file in write mode to update the option line
    with open(cfg_path, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)

    print(f"Set {option_name} = {new_value}")

'''
------------------------------------------------------------------------------
* Function: set_last_lua_script
* --------------------
* Description:
*	Opens the SNES9x-rr configuration file and changes a line in the file.
    SNES9x-rr uses a text configuration file for specifying hotkeys and inputs.
    Changing this file ensures that the desired control buttons and paths to Lua
    files are defined. This enables full automation without user configuration
    of directories. This function changes the most recently used Lua script so
    that it automatically loads when starting the emulator again.
*
* Arguments:   Configuration file path, the lua script path
* Returns:     none
'''
def set_last_lua_script(cfg_path, script_path):

    # Open the configuration file in read mode
    with open(cfg_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    updated_lines = []
    key_found = False

    # Search for the LastScriptFile line to update
    for line in lines:
        if line.strip().startswith("LastScriptFile"):
            updated_line = f"LastScriptFile = {script_path}\n"
            updated_lines.append(updated_line)
            key_found = True
        else:
            updated_lines.append(line)

    # If not found, add the last script line to the end
    if not key_found:
        updated_lines.append(f"LastScriptFile = {script_path}\n")

    # Open the configuration file in write mode to update the line
    with open(cfg_path, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)

    print(f"Set LastScriptFile to: {script_path}")

'''
------------------------------------------------------------------------------
* Function: download_lua_installer
* --------------------
* Description:
*	Downloads the Lua and LuaSocket installers and installs them if not
    already present. This is a required dependency for Lua scripting
*
* Arguments:   none
* Returns:     none
'''
def download_lua_installer():

    # Check if the Lua installer already exists
    if not os.path.exists(LUA_INSTALLER_NAME):
        print("Downloading Lua for Windows...")
        urllib.request.urlretrieve(LUA_INSTALLER_URL, LUA_INSTALLER_NAME)
        print("Download complete.")
    else:
        print("Installer already downloaded.")
    subprocess.run([LUA_INSTALLER_NAME], check=True)

    # Remove the installer once complete
    if os.path.exists(LUA_INSTALLER_NAME):
        os.remove(LUA_INSTALLER_NAME)
        print("Installer deleted after installation.")

'''
------------------------------------------------------------------------------
* Function: test_lua_socket_paths
* --------------------
* Description:
*	Test if Lua and LuaSocket are already installed on the system, and if not,
    install them to the default directory
*
* Arguments:   none
* Returns:     none
'''
def test_lua_socket_paths():

    # Specify the required default directory
    lua_paths = [
        "C:/Program Files (x86)/Lua/5.1/lua/socket.lua",
        "C:/Program Files (x86)/Lua/5.1/clibs/socket/core.dll",
    ]

    # Check that both required Lua socket paths exist
    # If not, download and run the installer
    all_exist = True
    for path in lua_paths:
        if os.path.exists(path):
            print(f"Found: {path}")
        else:
            print(f"Missing: {path}")
            all_exist = False
            download_lua_installer()
    return all_exist

'''
------------------------------------------------------------------------------
* Function: set_hotkey
* --------------------
* Description:
*	Opens the SNES9x-rr configuration file and changes a line in the file.
    SNES9x-rr uses a text configuration file for specifying hotkeys and inputs.
    Changing this file ensures that the desired control buttons and paths to Lua
    files are defined. This enables full automation without user configuration
    of directories and hotkeys. Hotkey remapping is required to prevent overlap
    with SB3 controls. Lua path specification is required to automatically
    load a Lua script at startup.
*
* Arguments:   Configuration file path, the hotkey to change, the new hotkey value
* Returns:     none
'''
def set_hotkey(cfg_path, hotkey_name, new_value):

    # Specify the name of the Key to change in the format of the configuration file
    key_line_prefix = f"Key:{hotkey_name}"
    key_found = False

    # Open the configuration file in read mode to search for the hotkey line
    with open(cfg_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Update the line with the new hotkey value
    # If the line does not exist, append it to the end
    updated_lines = []
    for line in lines:
        if line.strip().startswith(key_line_prefix):
            spaces = line.split('=')[0].rstrip()
            updated_line = f"{spaces} = {new_value}\n"
            updated_lines.append(updated_line)
            key_found = True
        else:
            updated_lines.append(line)
    if not key_found:
        updated_lines.append(f"Key:{hotkey_name}   = {new_value}\n")

    # Open the configuration file in write mode to update the hotkey line
    with open(cfg_path, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)
    print(f"Updated hotkey: {hotkey_name} to {new_value}")

'''
------------------------------------------------------------------------------
* Function: create_roms_folder
* --------------------
* Description:
*	Create a 'Roms' folder inside the SNES9x extracted directory if it does not
    exist.Generates a blank directory for SNES9x-rr to initialize files into. 
    The ROM file must be placed in this directory, which the user will be 
    prompted to do when running the program.
*
* Arguments:   none
* Returns:     none
'''
def create_roms_folder():
    roms_path = os.path.join(EXTRACT_PATH, "Roms")
    if not os.path.exists(roms_path):
        os.makedirs(roms_path)
    return roms_path

'''
------------------------------------------------------------------------------
* Function: create_saves_folder
* --------------------
* Description:
*	Create a 'Saves' folder inside the SNES9x extracted directory if it does not
    exist.Generates a blank directory for SNES9x-rr to initialize files into. 
    The ROM file must be placed in this directory, which the user will be 
    prompted to do when running the program.
*
* Arguments:   none
* Returns:     none
'''
def create_saves_folder():
    saves_path = os.path.join(EXTRACT_PATH, "Saves")
    if not os.path.exists(saves_path):
        os.makedirs(saves_path)
    return saves_path

'''
------------------------------------------------------------------------------
* Function: create_screenshots_folder
* --------------------
* Description:
*	Create a 'Screenshots' folder inside the SNES9x extracted directory if it does not
    exist.Generates a blank directory for SNES9x-rr to initialize files into. 
    The ROM file must be placed in this directory, which the user will be 
    prompted to do when running the program.
*
* Arguments:   none
* Returns:     none
'''
def create_screenshots_folder():
    roms_path = os.path.join(EXTRACT_PATH, "Screenshots")
    if not os.path.exists(roms_path):
        os.makedirs(roms_path)
    return roms_path

'''
------------------------------------------------------------------------------
* Function: get_emulator
* --------------------
* Description:
*	Downloads the source zip file for the SNES9x-rr emulator if it does not
    exist and SNES9x-rr is not ocurrently installed.
*
* Arguments:   none
* Returns:     none
'''
def get_emulator():
    print(f"Current working directory set to: {os.getcwd()}")
    if is_snes9x_present():
        print("SNES9x is ready to use!")
    else:
        print("SNES9x.exe is missing! Downloading required emulator")
        if not is_zip_present():
            download_file()
        extract_zip()

'''
------------------------------------------------------------------------------
* Function: is_snes9x_present
* --------------------
* Description:
*	Checks if snes9x.exe is in the extracted directory.
*
* Arguments:   none
* Returns:     none
'''
def is_snes9x_present():
    print("Checking for snes9x.exe")
    if os.path.isfile(SNES9X_EXE):
        print(f"SNES9x found at: {SNES9X_EXE}")
        return True
    else:
        print(f"SNES9x is NOT found in {EXTRACT_PATH}")
        return False

'''
------------------------------------------------------------------------------
* Function: download_file
* --------------------
* Description:
*	Downloads the SNES9x ZIP into the current directory
*
* Arguments:   none
* Returns:     none
'''
def download_file():
    print(f"Downloading {FILENAME} to {SAVE_PATH}...")
    response = requests.get(DOWNLOAD_URL, stream=True)
    if response.status_code == 200:
        with open(SAVE_PATH, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Download complete: {SAVE_PATH}")
    else:
        print(f"Failed to download. HTTP Status Code: {response.status_code}")

'''
------------------------------------------------------------------------------
* Function: is_zip_present
* --------------------
* Description:
*	Check if the SNES9x ZIP file is in the current directory
*
* Arguments:   none
* Returns:     none
'''
def is_zip_present():
    if os.path.isfile(SAVE_PATH):
        print(f"File is present at: {SAVE_PATH}")
        return True
    else:
        print(f"File NOT found in current directory: {SAVE_PATH}")
        return False

'''
------------------------------------------------------------------------------
* Function: is_zip_present
* --------------------
* Description:
*	Extract SNES9x ZIP file into the script's directory and delete the ZIP 
    afterward
*
* Arguments:   none
* Returns:     none
'''
def extract_zip():

    # Check if the extracted ZIP exists
    if not os.path.exists(EXTRACT_PATH):
        os.makedirs(EXTRACT_PATH)
    print(f"Extracting {FILENAME} to {EXTRACT_PATH}...")
    
    # Extract the ZIP file if it exists
    with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
        zip_ref.extractall(EXTRACT_PATH)
    print(f"Extraction complete! Files are in: {EXTRACT_PATH}")

    # Delete the ZIP file after extraction
    if os.path.isfile(ZIP_PATH):
        os.remove(ZIP_PATH)
        print(f"Deleted ZIP file: {ZIP_PATH}")
    else:
        print("ZIP file not found for deletion.")

# Executes starting at main when the program is executed
if __name__ == "__main__":
    main()
    