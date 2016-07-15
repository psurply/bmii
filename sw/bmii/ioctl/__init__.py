import os
import subprocess
from migen import *

from bmii.ioctl.iomodule import *

from .platform import BMIIPlatform
from .north_bridge import NorthBridge
from .south_bridge import SouthBridge

class IOModules():
    def __init__(self, bridges):
        self.modules_nb = 0
        self.bridges = bridges

    def __iadd__(self, iomodule):
        iomodule.set_addr(self.modules_nb)
        object.__setattr__(self, iomodule.name, iomodule)
        for bridge in self.bridges:
            bridge.connect(iomodule)
        self.modules_nb += 1
        return self


class IOCtl(Module):
    def __init__(self):
        self.reset = ResetSignal("sys")

        self.nb = NorthBridge("northbridge")
        self.sb = SouthBridge("southbridge")

        self.iomodules = IOModules([self.nb])
        self.iomodules += self.nb
        self.iomodules += self.sb

        self.submodules.nb = self.nb
        self.submodules.sb = self.sb

    def __iadd__(self, iomodule):
        self.iomodules += iomodule
        self.submodules.__setattr__(iomodule.name, iomodule)
        return self

    def build(self):
        plat = BMIIPlatform()
        self.nb.connect_platform(plat)
        self.sb.connect_platform(plat)

        self.comb += self.reset.eq(plat.request("reset0")
                    | plat.request("reset1"))

        dummy = Signal()
        self.comb += dummy.eq(plat.request("clk0")
                    | plat.request("clk1")
                    | plat.request("clk3"))

        plat.build(self)
        return plat

    def program(self):
        plat = self.build()
        subprocess.run(["quartus_pgm", "-m", "jtag",
                         "-o", "p;build/top.pof"], check=True)
