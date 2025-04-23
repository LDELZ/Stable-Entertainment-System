--[[******************************************************************************
 * File:        lua_server.py
 * Author:      Brennan Romero, Luke Delzer
 * Class:       Introduction to AI (CS3820), Spring 2025, Dr. Armin Moin
 * Assignment:  Semester Project
 * Due Date:    04-23-2025
 * Description: This program initializes the current SNES9x-rr instance
                as a LuaSocket server. This is required for abstraction of
                agent control. Once the server is active, memory values
                are sent over TCP to SB3 in Python and inputs are received
                from SB3 over the connection.
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
local host = "0.0.0.0"
local port = 12345
local message_index = 1

-- Create a new stave state and release all buttons
local slot1 = savestate.create(1)
local held_buttons = nil

-- Specify which RAM addresses to capture values from the emulator
-- These are sent over the TCP connection to SB3
local ram_addresses = {
    0x7E00D1, -- Mario's X position in the current level (Lower byte)
	0x7E00D2, -- Mario's X position in the current level (Upper byte)
    0x7E00D3, -- Mario's Y position in the current level (Lower byte)
	0x7E00D4, -- Mario's Y position in the current level (Upper byte)
	0x7E0071, -- Mario animation state flags
	0x7E007B, -- Marios X speed (signed)
	0x7E007D, -- Marios Y speed (signed)
	0x7E1493, -- end of level timer
}

-- This variable is used for debugging the lua script functionality only
-- It simulates (stubs) a list of TCP messages the Lua script would hear over TCP
-- These messages are processed to test different emulator actions
local messages = {
    "junk; 0",
    "wait; 2",
    "press; Al",
    "adv; 5",
    "send_mem;",
    "wait; 1",
    "press; r",
    "adv; 15",
    "press; rA",
    "send_mem;",
    "adv; 5",
    "press; r",
    "load_save;"
}

--[[------------------------------------------------------------------------------
* Function: sendOK
* --------------------
* Description:
*	Sends an OK message over the TCP connection back to SB3. This controls waiting
    and timing of the SB3 and emulator agent programs.
*
* Arguments:   The socket object representing the client (SB3)
* Returns:     none
]]
function sendOK(client)
    print("Sending okay!")
    client:send("Ok" .. "\n")
    print("Sent okay!")
end

--[[------------------------------------------------------------------------------
* Function: wait_for_next_adv
* --------------------
* Description:
*	Receives a message over the TCP socket from SB3. Parses the message, and
    executes the corresponding action in the SNES9x emulator environment
*
* Arguments:   The message received, the socket object representing the client (SB3)
* Returns:     none
]]
function wait_for_next_adv(msg, client)

    -- Parse messages that have arguments
    local adv_cmd, adv_n = msg:match("^(adv);%s*(%d+)$")
    local wait_cmd, wait_n = msg:match("^(wait);%s*(%d+)$")
    local press_cmd, keys = msg:match("^(press);%s*([A-Za-z]+)$")

    local okay = true

    -- Select the corresponding message sent
    -- If the message is to advance frames:
    if adv_cmd == "adv" then

        -- Store the number of frames to advance by
        local n = tonumber(adv_n)

        -- Display the message details in the Lua window
        print("Received " .. msg .. " - Advancing " .. n .. " frames")

        -- For each fram to advance by in 'n' (the number of advances)
        -- Check which buttons are held, set the joypad to be holding those buttons
        -- Then while holding those buttons, advance n frames
        for i = 1, n do
            if held_buttons then
                joypad.set(1, held_buttons)
                print(held_buttons)
            end
            emu.frameadvance()
        end

        -- Unhold all buttons for othe next step
        held_buttons = nil

    -- Else if the message is to wait
    -- Wait a specified amount of time (wait_n) that the emulator will not respond for
    elseif wait_cmd == "wait" then
        local seconds = tonumber(wait_n)
        print("Received \"" .. msg .. "\" - Waiting for " .. seconds .. " seconds")
        socket.sleep(seconds)

    -- Else if the message is to load the save state, load it
    elseif msg == "load_save;" then
        print("Received \"" .. msg .. "\" - Loading save state slot 1")
        savestate.load(slot1)
        emu.frameadvance()

    -- Else if the message is to get the memory address values specified in the addresses above
    elseif msg == "send_mem;" then
        local parts = {}

        -- Place the memory values in a table to be sent back for each mem address specified
        for _, addr in ipairs(ram_addresses) do
            local value = memory.readbyte(addr)
            table.insert(parts, string.format("0x%06X=%d", addr, value))
        end

        -- Send the table of memory values back
        print("Received \"" .. msg .. "\" - Sending memory values: " .. table.concat(parts, ", "))
        local return_msg = table.concat(parts, ",") .. "\n"
        client:send(return_msg)
        okay = false


    -- Else if the message is to press the joypad buttons
    elseif press_cmd == "press" then

        -- Reset the buttons being held
        held_buttons = {}
    
        -- For each command (c), set the corresponding button to hold to True
        for c in keys:gmatch(".") do
            if c == "A" then held_buttons.A = true
            elseif c == "B" then held_buttons.B = true
            elseif c == "X" then held_buttons.X = true
            elseif c == "Y" then held_buttons.Y = true
            elseif c == "L" then held_buttons.L = true
            elseif c == "R" then held_buttons.R = true
            elseif c == "u" then held_buttons.up = true
            elseif c == "d" then held_buttons.down = true
            elseif c == "l" then held_buttons.left = true
            elseif c == "r" then held_buttons.right = true
            elseif c == "S" then held_buttons.start = true
            elseif c == "s" then held_buttons.select = true
            end
        end
    
        -- Set all of the held buttons in the actual joypad interface
        joypad.set(1, held_buttons)
    
        -- Print what is being held down this frame in a table
        local held = joypad.getdown(1)
        local line = {}
        for button, state in pairs(held) do
            if state then table.insert(line, button) end
        end
        local line = {}
        for button, state in pairs(held_buttons) do
            if state then table.insert(line, button) end
        end
        print("Received \"" .. msg .. "\" - Holding: " .. table.concat(line, ", ") .. "during next frame advance")

    -- Else the message is invalid, just ignore it
    else
        print("Received \"" .. msg .. "\" - Invalid message; Ignoring it")
        emu.frameadvance()
    end

    -- Send an OK message to the client if the Lua server is functioning properly
    if okay then
        sendOK(client)
    end
end

-- Process the messages list specefied above for debugging purposes only
-- Start the server and connect over the socket
local server = assert(socket.bind(host, port))
local tcp = assert(socket.tcp())
local ip, port = server:getsockname()
print("Waiting for connection on " .. ip .. ":" .. port)

-- Accept the connection
local client, err = server:accept()
ip, port = client:getsockname()
client:settimeout(-1)
print("Connected to  " .. ip .. ":" .. port)

-- Receive messages over the TCP connection
while true do
    local line, err =  client:receive("*l")

    -- Wait until it is ok to advance frames again
    -- Otherwise proceed with advancing frames
    if not err then
        wait_for_next_adv(line, client)
    else
        emu.frameadvance()
    end
end