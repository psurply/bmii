from migen import *

from .iomodule import IOModule, IOSignal, IOSignalDir, CtrlReg, CtrlRegDir
from .ibus import IBus

FD_WIDTH    = 8
INTR_WIDTH  = 2

class NorthBridge(IOModule):
    def __init__(self, name):
        IOModule.__init__(self, name)
        self.ibus_slaves = []

        self.cregs += CtrlReg("IDCODE", CtrlRegDir.RDONLY)
        self.cregs += CtrlReg("SCRATCH", CtrlRegDir.RDWR)

        self.ifclk = Signal()
        self.act = Signal()
        self.wr = Signal()
        self.la = Signal()
        self.ioctl_rdy = Signal()
        self.iomodule_rdy = Signal()
        self.intr = Signal(INTR_WIDTH)

        self.fdt = TSTriple(FD_WIDTH)
        self.fd = Signal(FD_WIDTH)

        self.ibus_m = Record(IBus)

        self.comb += self.cregs.IDCODE.eq(0xA5)

        self.sync += self.ifclk.eq(~self.ifclk)
        self.comb += self.ioctl_rdy.eq(~self.act)

        # Latch address
        self.sync += If(self.act & self.la,
                self.ibus_m.maddr.eq(self.fdt.i[0:3]),
                self.ibus_m.raddr.eq(self.fdt.i[3:8]))

        # Request IO module
        self.comb += self.ibus_m.req.eq(~self.ioctl_rdy & ~self.la)

        # Operation type
        self.comb += self.ibus_m.wr.eq(self.wr)
        self.comb += self.fdt.oe.eq(~self.ioctl_rdy & ~self.wr & ~self.la)

        self.comb += self.ibus_m.mosi.eq(self.fdt.i)
        self.comb += self.fdt.o.eq(self.ibus_m.miso)

        self.iosignals += IOSignal("TEST0", IOSignalDir.OUT)
        self.comb += self.iosignals.TEST0.eq(self.ibus_m.maddr[0])
        self.iosignals += IOSignal("TEST1", IOSignalDir.OUT)
        self.comb += self.iosignals.TEST1.eq(self.cregs.SCRATCH[0])

    def connect(self, iomodule):
        self.ibus_slaves.append(iomodule.ibus)

    def connect_platform(self, plat):
        self.comb += self.ibus_m.connect(*self.ibus_slaves)
        self.specials += self.fdt.get_tristate(plat.request("fd"))

        ctl = plat.request("ctl")
        rdy = plat.request("rdy")

        self.comb += plat.request("ifclk").eq(self.ifclk)

        self.comb += self.act.eq(ctl[0])
        self.comb += self.wr.eq(ctl[1])
        self.comb += self.la.eq(ctl[2])

        self.comb += rdy[0].eq(self.ioctl_rdy)
        self.comb += rdy[1].eq(self.iomodule_rdy)

        self.comb += plat.request("intr").eq(self.intr)
