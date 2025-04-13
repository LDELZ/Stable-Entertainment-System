-- Load lua socket from the required directory
-- If this fails, run emulator_initialize again and accept the lua socket installation
package.path = "C:/Program Files (x86)/Lua/5.1/lua/?.lua;" .. package.path
package.cpath = "C:/Program Files (x86)/Lua/5.1/clibs/?.dll;C:/Program Files (x86)/Lua/5.1/clibs/?/core.dll;" .. package.cpath

local socket = require("socket")
local host = "0.0.0.0"
local port = 12345
local message_index = 1
local slot1 = savestate.create(1)
local held_buttons = nil

local ram_addresses = {
    0x7E00D1, -- Mario's X position in the current level (Lower byte)
	0x7E00D2, -- Mario's X position in the current level (Upper byte)
    0x7E00D3, -- Mario's Y position in the current level (Lower byte)
	0x7E00D4, -- Mario's Y position in the current level (Upper byte)
	0x7E0071, -- Mario animation state flags
	0x7E007B, -- Marios X speed (signed)
	0x7E007D, -- Marios Y speed (signed)
	0x7E1493, -- end of level timer
--     0x7E0010,
--     0x7E0011,
--     0x7E0012,
--     0x7E0013,
--     0x7E0014,
}

-- ###################################################################################
-- DEBUGGING PART:
-- Remove this later; this is just a list of messages that are used for lua testing
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
-- ###################################################################################

function sendOK(client)
    print("Sending okay!")
    client:send("Ok" .. "\n")
    print("Sent okay!")
end

function wait_for_next_adv(msg, client)
    --local msg = messages[message_index]

    -- Parse messages that have arguments
    local adv_cmd, adv_n = msg:match("^(adv);%s*(%d+)$")
    local wait_cmd, wait_n = msg:match("^(wait);%s*(%d+)$")
    local press_cmd, keys = msg:match("^(press);%s*([A-Za-z]+)$")

    local okay = true

    -- Select the corresponding message sent
    if adv_cmd == "adv" then
        local n = tonumber(adv_n)
        print("Received " .. msg .. " - Advancing " .. n .. " frames")
        for i = 1, n do
            if held_buttons then
                joypad.set(1, held_buttons)
            end
            emu.frameadvance()
        end
        held_buttons = nil

    
    elseif wait_cmd == "wait" then
        local seconds = tonumber(wait_n)
        print("Received \"" .. msg .. "\" - Waiting for " .. seconds .. " seconds")
        socket.sleep(seconds)

    elseif msg == "load_save;" then
        print("Received \"" .. msg .. "\" - Loading save state slot 1")
        savestate.load(slot1)
        emu.frameadvance()


    elseif msg == "send_mem;" then
        local parts = {}
        for _, addr in ipairs(ram_addresses) do
            local value = memory.readbyte(addr)
            table.insert(parts, string.format("0x%06X=%d", addr, value))
        end
        print("Received \"" .. msg .. "\" - Sending memory values: " .. table.concat(parts, ", "))
        local return_msg = table.concat(parts, ",") .. "\n"
        client:send(return_msg)
        okay = false
        emu.frameadvance()

--     elseif msg == "screenshot;" then
--         local screenshot = gui.gdscreenshot()
--         print("Len:" .. #screenshot)
--         client:send(screenshot)
--         okay = false

    elseif press_cmd == "press" then
        held_buttons = {}
    
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
    
        joypad.set(1, held_buttons)
    
        -- Print whats being held
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

    
    else
        print("Received \"" .. msg .. "\" - Invalid message; Ignoring it")
        emu.frameadvance()
    end

    if okay then
        sendOK(client)
    end
end

-- ###################################################################################
-- Debugging part:
-- Change this later to just wait for new messages from python
-- Currently all this does is process the messages list
-- while message_index <= #messages do
--     wait_for_next_adv(messages[message_index])
--     message_index = message_index + 1
-- end
local server = assert(socket.bind(host, port))
local tcp = assert(socket.tcp())

local ip, port = server:getsockname()
print("Waiting for connection on " .. ip .. ":" .. port)
local client, err = server:accept()
ip, port = client:getsockname()
client:settimeout(-1)
print("Connected to  " .. ip .. ":" .. port)

while true do
    local line, err =  client:receive("*l")
    if not err then
        wait_for_next_adv(line, client)
    else
        emu.frameadvance()
    end
end

--
-- print("All messages processed. Pausing emulator")
-- emu.pause()
-- ###################################################################################