-- Setup LuaSocket
package.path = "C:/Program Files (x86)/Lua/5.1/lua/?.lua;" .. package.path
package.cpath = "C:/Program Files (x86)/Lua/5.1/clibs/?.dll;C:/Program Files (x86)/Lua/5.1/clibs/?/core.dll;" .. package.cpath

local socket = require("socket")
local host = "127.0.0.1"
local port = 12345

local client = assert(socket.tcp())
client:connect(host, port)
client:settimeout(0)

local unpack = table.unpack or unpack

-- Addresses to monitor
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

-- Per-frame send
local function send_ram_values()
    local frame = emu.framecount()
    local parts = { "Frame=" .. frame }

    for i = 1, #ram_addresses do
        local addr = ram_addresses[i]
        local value = memory.readbyte(addr)
        table.insert(parts, string.format("0x%06X=%d", addr, value))
    end

    local message = table.concat(parts, ",") .. "\n"
    -- Wait for the client to be ready to receive
    if client:receive("*l") then
        client:send(message)
    end
    print("Sent: " .. message:sub(1, -2))
end

emu.registerafter(send_ram_values)
