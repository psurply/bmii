from bmii import *
from bmii.ioctl.testbench import *
from migen.genlib.fifo import *
import sys

class FIFOIOModule(IOModule):
    def __init__(self):
        IOModule.__init__(self, "FIFO")

        self.cregs += CtrlReg("STATUS", CtrlRegDir.RDONLY)
        self.cregs.STATUS[0] = "WRITABLE"
        self.cregs.STATUS[1] = "READABLE"
        self.cregs += CtrlReg("IN", CtrlRegDir.WRONLY)
        self.cregs += CtrlReg("OUT", CtrlRegDir.RDONLY)

        fifo = SyncFIFO(8, 4)
        self.submodules.fifo = fifo

        self.comb += self.cregs.STATUS[0].eq(fifo.writable)
        self.comb += self.cregs.STATUS[1].eq(fifo.readable)
        self.comb += self.cregs.OUT.eq(fifo.dout)
        self.comb += fifo.din.eq(self.cregs.IN)
        self.comb += fifo.we.eq(self.cregs.IN.wr_pulse)
        self.comb += fifo.re.eq(self.cregs.OUT.rd_pulse)


class FIFOTestCase(IOModuleTestCase(FIFOIOModule())):
    def test_basic(self):
        def gen():
            yield from self.ibus_write_creg(self.tb.iomodule.cregs.IN, 0x42)
            yield
            yield

            yield from self.ibus_reset()
            yield

            yield from self.ibus_write_creg(self.tb.iomodule.cregs.IN, 0x13)
            yield
            yield

            yield from self.ibus_reset()
            yield

            yield from self.ibus_read_creg(self.tb.iomodule.cregs.STATUS)
            yield

            self.assertEqual((yield self.tb.ibus_m.miso), 0x3)

            yield from self.ibus_read_creg(self.tb.iomodule.cregs.OUT)
            yield
            yield

            self.assertEqual((yield self.tb.ibus_m.miso), 0x42)

            yield from self.ibus_reset()
            yield

            yield from self.ibus_read_creg(self.tb.iomodule.cregs.OUT)
            yield
            yield

            self.assertEqual((yield self.tb.ibus_m.miso), 0x13)

            yield from self.ibus_reset()
            yield
            yield

        self.run_with(gen())


class FIFO(BMIIModule):
    def __init__(self):
        BMIIModule.__init__(self, FIFOIOModule(), FIFOTestCase)

    def enqueue(self, value):
        assert self.drv.STATUS.WRITABLE, "FIFO is full"
        self.drv.IN = value

    def dequeue(self):
        assert self.drv.STATUS.READABLE, "FIFO is empty"
        return int(self.drv.OUT)
