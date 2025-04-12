-- Load lua socket from the required directory
-- If this fails, run emulator_initialize again and accept the lua socket installation
package.path = "C:/Program Files (x86)/Lua/5.1/lua/?.lua;" .. package.path
package.cpath = "C:/Program Files (x86)/Lua/5.1/clibs/?.dll;C:/Program Files (x86)/Lua/5.1/clibs/?/core.dll;" .. package.cpath

local socket = require("socket")
local host = "127.0.0.1"
local port = 12345
local message_index = 1
local slot1 = savestate.create(1)
local held_buttons = nil

local ram_addresses = {
    0x7E00D1, -- Mario's X position in the current level (Lower byte)
	0x7E00D2, -- Mario's X position in the current level (Upper byte)
    0x7E00D3, -- Mario's Y position in the current level (Lower byte)
	0x7E00D4, -- Mario's Y position in the current level (Upper byte)
	0x7E0071, -- Mario animation state flagc
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
    "adv; 30",
    "wait; 3",
    "load_save;"
}
-- ###################################################################################

function wait_for_next_adv()
    local msg = messages[message_index]

    if not msg then
        print("No more messages. Pausing emulator.")
        return false
    end

    -- Parse messages that have arguments
    local adv_cmd, adv_n = msg:match("^(adv);%s*(%d+)$")
    local wait_cmd, wait_n = msg:match("^(wait);%s*(%d+)$")
    local press_cmd, keys = msg:match("^(press);%s*([A-Za-z]+)$")
    
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
        return true
    
    elseif wait_cmd == "wait" then
        local seconds = tonumber(wait_n)
        print("Received \"" .. msg .. "\" - Waiting for " .. seconds .. " seconds")
        socket.sleep(seconds)
        return true
    
    elseif msg == "load_save;" then
        print("Received \"" .. msg .. "\" - Loading save state slot 1")
        savestate.load(slot1)
        emu.frameadvance()
        return true

    elseif msg == "send_mem;" then
        local parts = {}
        for _, addr in ipairs(ram_addresses) do
            local value = memory.readbyte(addr)
            table.insert(parts, string.format("0x%06X=%d", addr, value))
        end
        print("Received \"" .. msg .. "\" - Sending memory values: " .. table.concat(parts, ", "))
        emu.frameadvance()
        return true
    
    
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
        return true
    
    else
        print("Received \"" .. msg .. "\" - Invalid message; Ignoring it")
        emu.frameadvance()
        return true
    end
end

-- ###################################################################################
-- Debugging part:
-- Change this later to just wait for new messages from python
-- Currently all this does is process the messages list
while message_index <= #messages do
    wait_for_next_adv()
    message_index = message_index + 1
end

print("All messages processed. Pausing emulator")
emu.pause()
-- ###################################################################################