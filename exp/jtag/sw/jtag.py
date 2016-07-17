#!/usr/bin/env python3

from bmii import *
from bmii.modules import jtag

class BMIIJTAG(BMII):
    def __init__(self):
        BMII.__init__(self)

        self.jtag = jtag.JTAG()
        self.add_module(self.jtag)

        self.ioctl.sb.pins.IO10 += self.jtag.iomodule.iosignals.TMS
        self.ioctl.sb.pins.IO11 += self.jtag.iomodule.iosignals.TCK
        self.ioctl.sb.pins.IO12 += self.jtag.iomodule.iosignals.TRST
        self.ioctl.sb.pins.IO13 += self.jtag.iomodule.iosignals.TDI
        self.ioctl.sb.pins.IO21 += self.jtag.iomodule.iosignals.TDO

    def idcode(self):
        self.jtag.reset()
        self.jtag.irwrite(0b110, 10)
        return self.jtag.drread(32)


if __name__ == "__main__":
    bjtag = BMIIJTAG()
    #bjtag.cli()
    print(hex(bjtag.idcode()))
