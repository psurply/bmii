from migen import *

from bmii.ioctl.iomodule import *
from bmii.ioctl.pins import *

IO_WIDTH        = 16
IO_BANKS        = 2
LED_WIDTH       = 2

class SouthBridge(IOModule):
    def __init__(self, name):
        IOModule.__init__(self, name)

        self.pins = define_bmii_pins(self.cregs)
        self.submodules += self.pins

    def connect_platform(self, plat):
        io = (plat.request("io1"), plat.request("io2"))
        led = plat.request("led")
        sw = plat.request("sw")

        for b in range(IO_BANKS):
            for i in range(IO_WIDTH):
                name = "IO" + str(b + 1) + hex(i)[2:].upper()
                object.__getattribute__(self.pins, name).connect_realpin(io[b][i])

        for i in range(LED_WIDTH):
            name = "LED" + str(i)
            object.__getattribute__(self.pins, name).connect_realpin(led[i])

        self.pins.SW.connect_realpin(sw)

    def pinout(self):
        return str(self.pins)
