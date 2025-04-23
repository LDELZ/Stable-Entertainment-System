--[[******************************************************************************
 * File:        memory_server.py
 * Author:      Brennan Romero, Luke Delzer
 * Class:       Introduction to AI (CS3820), Spring 2025, Dr. Armin Moin
 * Assignment:  Semester Project
 * Due Date:    04-23-2025
 * Description: This program initializes the current SNES9x-rr instance
                as a LuaSocket server. This is required for abstraction of
                agent control. Once the server is active, memory values
                are sent over TCP to SB3 in Python and inputs are received
                from SB3 over the connection. This version is used
                exclusively for memory passing/
 * Usage:       This program is automatically used by the SNES9x emulator
                and is not intended for use on its own.
 ******************************************************************************
 ]]

-- Load lua socket from the required directory
-- If this fails, run emulator_initialize again and accept the lua socket installation
package.path = "C:/Program Files (x86)/Lua/5.1/lua/?.lua;" .. package.path
package.cpath = "C:/Program Files (x86)/Lua/5.1/clibs/?.dll;C:/Program Files (x86)/Lua/5.1/clibs/?/core.dll;" .. package.cpath

-- Specify the TCP values to make SNES9x a server
local socket = require("socket")
local host = "127.0.0.1"
local port = 12345
local client = assert(socket.tcp())
client:connect(host, port)
client:settimeout(0)

-- Unpack the table of memory values to check and return values on
local unpack = table.unpack or unpack

-- Specify which RAM addresses to capture values from the emulator
-- These are sent over the TCP connection to SB3
local ram_addresses = {
    0x7E00D1, -- Mario's X position in the current level (Lower byte)
	0x7E00D2, -- Mario's X position in the current level (Upper byte)
    0x7E00D3, -- Mario's Y position in the current level (Lower byte)
	0x7E00D4, -- Mario's Y position in the current level (Upper byte)
	0x7E0071, -- Mario animation state flagc
}

--[[------------------------------------------------------------------------------
* Function: send_ram_values
* --------------------
* Description:
*	Receives a message over the TCP socket from SB3. Parses the message, and
    executes the corresponding action in the SNES9x emulator environment
*
* Arguments:   The message received, the socket object representing the client (SB3)
* Returns:     none
]]
local function send_ram_values()

    -- Get the current frame number; this associates the RAM values to when they happened
    local frame = emu.framecount()
    local parts = { "Frame=" .. frame }

    -- For each RAM address specified in ram_addresses, read the value from the address
    -- Insert each read value into a table to send over the TCP connection to SB3
    for i = 1, #ram_addresses do
        local addr = ram_addresses[i]
        local value = memory.readbyte(addr)
        table.insert(parts, string.format("0x%06X=%d", addr, value))
    end

    -- Concatenate the table of RAM values
    local message = table.concat(parts, ",") .. "\n"
    
    -- Wait for the client to be ready to receive the table and send when ready
    if client:receive("*l") then
        client:send(message)
    end
    print("Sent: " .. message:sub(1, -2))
end

-- Send the RAM values by calling send_ram_values after every frame
-- This line is required for SNES9x-rr Lua control and is executed after every frame render
emu.registerafter(send_ram_values)
