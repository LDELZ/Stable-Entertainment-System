-- Setup LuaSocket
package.path = "C:/Program Files (x86)/Lua/5.1/lua/?.lua;" .. package.path
package.cpath = "C:/Program Files (x86)/Lua/5.1/clibs/?.dll;C:/Program Files (x86)/Lua/5.1/clibs/?/core.dll;" .. package.cpath

local socket = require("socket")
local host = "127.0.0.1"
local port = 12345

local client = assert(socket.tcp())
client:connect(host, port)
client:settimeout(0)  -- non-blocking receive

-- Helper to read 16-bit values
function read16(address)
    local lo = memory.readbyte(address)
    local hi = memory.readbyte(address + 1)
    return hi * 256 + lo
end

-- Command handler
function handle_command(cmd)
    local cmd_type, addr_str = cmd:match("([^,]+),([^,]+)")
    if cmd_type == "READ16" then
        local addr = tonumber(addr_str)
        if addr then
            local value = read16(addr)
            client:send(string.format("VALUE,%d\n", value))
            print(string.format("Read16 from 0x%04X: %d", addr, value))
        end
    end
end

-- Per-frame logic: check for commands after the frame has completed
function update()
    local data, err = client:receive()
    if data then
        handle_command(data)
    end
end

-- Register after each frame so RAM values reflect the still frame
emu.registerafter(update)
