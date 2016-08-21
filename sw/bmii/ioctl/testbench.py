import unittest
from migen import *
from migen.test.support import SimCase

from bmii.ioctl.ibus import IBus
from bmii.ioctl.iomodule import IOModule



def make_testbench(iomodule):
    def __init__(self):
        self.iomodule = iomodule
        self.iomodule.set_addr(1)
        assert self.iomodule is not None, "IOModuleTestCase not initialized"
        self.submodules += self.iomodule

        self.ibus_m = Record(IBus)

        self.comb += self.ibus_m.connect(self.iomodule.ibus)
        self.comb += self.ibus_m.maddr.eq(self.iomodule.addr)

    return type("TestBench", (Module,), {"__init__": __init__})


def IOModuleTestCase(iomodule):
    def ibus_write_creg(self, creg, value):
        return [self.tb.ibus_m.raddr.eq(creg.addr),
                self.tb.ibus_m.mosi.eq(value),
                self.tb.ibus_m.wr.eq(1),
                self.tb.ibus_m.req.eq(1)]

    def ibus_reset(self):
        return [self.tb.ibus_m.raddr.eq(0),
                self.tb.ibus_m.mosi.eq(0),
                self.tb.ibus_m.wr.eq(0),
                self.tb.ibus_m.req.eq(0)]

    def ibus_read_creg(self, creg):
        return [self.tb.ibus_m.raddr.eq(creg.addr),
                self.tb.ibus_m.wr.eq(0),
                self.tb.ibus_m.req.eq(1)]

    return type("IOModuleTestCase", (SimCase, unittest.TestCase), {
                "ibus_write_creg": ibus_write_creg,
                "ibus_read_creg": ibus_read_creg,
                "ibus_reset": ibus_reset,
                "TestBench": make_testbench(iomodule)})
