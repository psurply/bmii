from migen import *
from migen.genlib.coding import PriorityEncoder

from bmii.ioctl.iomodule import *
from bmii.ioctl.ibus import IBus

FD_WIDTH    = 8
INTR_WIDTH  = 2


class IntCircuit(Module):
    def __init__(self):
        self.intr = Signal()
        self.intr_number = Signal(8)
        self.ack = Signal()
        self.eoi_request = Signal()
        self.eoi_number = Signal(8)
        self.intrs = []

    def __iadd__(self, intr):
        self.intrs.append(intr)
        intr_index = len(self.intrs)
        self.comb += intr.ack.eq(self.ack & (self.intr_number == intr_index))
        self.comb += intr.eoi.eq(self.eoi_request & (self.eoi_number == intr_index))

        return self

    def generate_circuit(self):
        int_priority_encoder = PriorityEncoder(len(self.intrs) + 1)
        self.submodules += int_priority_encoder

        for i in range(len(self.intrs)):
            self.comb += int_priority_encoder.i[i + 1].eq(self.intrs[i])

        self.comb += self.intr_number.eq(int_priority_encoder.o)
        self.comb += self.intr.eq(reduce(or_, [0] + self.intrs))

    def get_handlers(self, intr_number):
        return self.intrs[intr_number - 1].handlers

    def display(self):
        print("Interrupts:")
        for i in range(len(self.intrs)):
            print("  {}: {}".format(i, self.intrs[i].name))


class NorthBridge(IOModule):
    def __init__(self, name):
        IOModule.__init__(self, name)
        self.ibus_slaves = []

        self.cregs += CtrlReg("IDCODE", CtrlRegDir.RDONLY)
        self.comb += self.cregs.IDCODE.eq(0xA5)
        self.cregs += CtrlReg("SCRATCH", CtrlRegDir.RDWR)
        self.cregs += CtrlReg("EOI", CtrlRegDir.WRONLY)

        self.ibus_m = Record(IBus)

        self.fdt = TSTriple(FD_WIDTH)
        self.fd = Signal(FD_WIDTH)

        self.ifclk = Signal()
        self.act = Signal()
        self.wr = Signal()
        self.la = Signal()
        self.ioctl_rdy = Signal()
        self.iomodule_rdy = Signal()

        # Interrupts
        self.intr = Signal(INTR_WIDTH)
        self.interrupts = IntCircuit()
        self.submodules += self.interrupts
        self.comb += self.intr[0].eq(~self.interrupts.intr)
        self.comb += self.interrupts.ack.eq(self.la & self.act)
        self.comb += self.interrupts.eoi_request.eq(self.cregs.EOI.wr_pulse)
        self.comb += self.interrupts.eoi_number.eq(self.cregs.EOI)

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

        # Data bus
        self.comb += self.fdt.oe.eq((~self.ioctl_rdy & ~self.wr & ~self.la)
                | (~self.act & self.interrupts.intr))

        self.comb += self.ibus_m.mosi.eq(self.fdt.i)
        self.comb += \
                If(self.interrupts.intr,
                    self.fdt.o.eq(self.interrupts.intr_number)).\
                Else(self.fdt.o.eq(self.ibus_m.miso))


    def connect(self, iomodule):
        if not iomodule.shadowed:
            self.ibus_slaves.append(iomodule.ibus)

    def connect_platform(self, plat):
        self.comb += self.ibus_m.connect(*self.ibus_slaves)
        self.specials += self.fdt.get_tristate(plat.request("fd"))

        self.interrupts.generate_circuit()

        ctl = plat.request("ctl")
        rdy = plat.request("rdy")

        self.comb += plat.request("ifclk").eq(self.ifclk)

        self.comb += self.act.eq(ctl[0])
        self.comb += self.wr.eq(ctl[1])
        self.comb += self.la.eq(ctl[2])

        self.comb += rdy[0].eq(self.ioctl_rdy)
        self.comb += rdy[1].eq(self.iomodule_rdy)

        self.comb += plat.request("intr").eq(self.intr)
