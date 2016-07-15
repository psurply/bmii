import unittest
from migen import *
from migen.test.support import SimCase

from bmii.ioctl.north_bridge import NorthBridge
from bmii.ioctl.south_bridge import SouthBridge
from bmii.ioctl.iomodule import IOModule, CtrlReg, CtrlRegDir

class NorthBridgeUSBCTLCase(SimCase, unittest.TestCase):
    class TestBench(Module):
        def __init__(self):
            self.fd_in = Signal(8)
            self.fd_out = Signal(8)

            self.act = Signal()
            self.wr = Signal()
            self.la = Signal()

            self.ioctl_rdy = Signal()
            self.iomodule_rdy = Signal()

            self.miso = Signal(8)

            self.submodules.dut = NorthBridge("northbridge")

            self.comb += self.fd_in.eq(self.dut.fdt.o)
            self.comb += self.dut.fdt.i.eq(self.fd_out)
            self.comb += self.dut.act.eq(self.act)
            self.comb += self.dut.wr.eq(self.wr)
            self.comb += self.dut.la.eq(self.la)
            self.comb += self.ioctl_rdy.eq(self.dut.ioctl_rdy)
            self.comb += self.iomodule_rdy.eq(self.dut.iomodule_rdy)
            self.comb += self.dut.ibus_m.miso.eq(self.miso)

    def test_ask_command(self):
        def gen():
            for i in range(10):
                yield
                self.assertEqual((yield self.tb.dut.ifclk), 1)
                yield
                self.assertEqual((yield self.tb.dut.ifclk), 0)
            yield
            self.assertEqual((yield self.tb.dut.ioctl_rdy), 1)

        self.run_with(gen())

    def test_select_module(self):
        def gen():
            module_addr = 2
            reg_addr = 8

            yield self.tb.act.eq(0)
            yield self.tb.fd_out.eq((reg_addr << 3) | (module_addr))
            yield self.tb.wr.eq(1)
            yield self.tb.la.eq(1)
            yield

            yield self.tb.act.eq(1)
            yield
            self.assertEqual((yield self.tb.dut.ioctl_rdy), 1)
            yield
            self.assertEqual((yield self.tb.dut.ioctl_rdy), 0)

            yield self.tb.act.eq(0)
            yield self.tb.fd_out.eq(0)
            yield self.tb.wr.eq(0)
            yield self.tb.la.eq(1)
            yield
            self.assertEqual((yield self.tb.dut.ioctl_rdy), 0)
            self.assertEqual((yield self.tb.dut.fdt.oe), 0)

            yield
            self.assertEqual((yield self.tb.dut.ioctl_rdy), 1)
            self.assertEqual((yield self.tb.dut.ibus_m.maddr), module_addr)
            self.assertEqual((yield self.tb.dut.ibus_m.raddr), reg_addr)

        self.run_with(gen())

    def test_write(self):
        def gen():
            value = 42

            yield self.tb.act.eq(0)
            yield self.tb.fd_out.eq(value)
            yield self.tb.wr.eq(1)
            yield self.tb.la.eq(0)
            yield
            self.assertEqual((yield self.tb.dut.ibus_m.req), 0)

            yield self.tb.act.eq(1)
            yield
            self.assertEqual((yield self.tb.dut.ibus_m.req), 0)
            self.assertEqual((yield self.tb.dut.ibus_m.mosi), value)

            yield
            self.assertEqual((yield self.tb.dut.ibus_m.req), 1)
            self.assertEqual((yield self.tb.dut.ibus_m.mosi), value)
            self.assertEqual((yield self.tb.dut.fdt.oe), 0)

            yield self.tb.act.eq(0)
            yield self.tb.fd_out.eq(0)
            yield self.tb.wr.eq(0)
            yield self.tb.la.eq(0)
            yield
            self.assertEqual((yield self.tb.dut.ibus_m.req), 1)

            yield
            self.assertEqual((yield self.tb.dut.ibus_m.req), 0)

        self.run_with(gen())


    def test_read(self):
        def gen():
            value = 42

            yield self.tb.miso.eq(value)

            yield self.tb.act.eq(0)
            yield self.tb.fd_out.eq(0)
            yield self.tb.wr.eq(0)
            yield self.tb.la.eq(0)
            yield
            self.assertEqual((yield self.tb.dut.ibus_m.req), 0)

            yield self.tb.act.eq(1)
            yield
            self.assertEqual((yield self.tb.dut.ibus_m.req), 0)

            yield
            self.assertEqual((yield self.tb.dut.ibus_m.req), 1)
            self.assertEqual((yield self.tb.fd_in), value)
            self.assertEqual((yield self.tb.dut.fdt.oe), 1)

            yield self.tb.act.eq(0)
            yield self.tb.fd_out.eq(0)
            yield self.tb.wr.eq(0)
            yield self.tb.la.eq(0)
            yield
            self.assertEqual((yield self.tb.dut.ibus_m.req), 1)

            yield
            self.assertEqual((yield self.tb.dut.ibus_m.req), 0)

        self.run_with(gen())


class NorthBridgeIOModuleCase(SimCase, unittest.TestCase):
    class TestBench(Module):
        class DummyIOModule(IOModule):
            def __init__(self, name):
                IOModule.__init__(self, name)
                self.cregs += CtrlReg("REG1", CtrlRegDir.RDONLY)
                self.comb += self.cregs.REG1.eq(0x42)

                self.cregs += CtrlReg("REG2", CtrlRegDir.WRONLY)
                self.cregs.REG2[0:4] = "AL"
                self.cregs.REG2[4:8] = "AH"

                self.cregs += CtrlReg("REG3", CtrlRegDir.RDWR)
                self.cregs.REG3[0:4] = "BL"
                self.cregs.REG3[4:8] = "BH"

        def __init__(self):
            nb = NorthBridge("northbridge")
            diom = self.DummyIOModule("dummyiomodule")
            diom.set_addr(1)
            nb.connect(nb)
            nb.connect(diom)

            self.fd_in = Signal(8)
            self.fd_out = Signal(8)

            self.act = Signal()
            self.wr = Signal()
            self.la = Signal()

            self.ioctl_rdy = Signal()
            self.iomodule_rdy = Signal()

            self.submodules.dut = nb
            self.submodules.diom = diom

            self.comb += self.fd_in.eq(self.dut.fdt.o)
            self.comb += self.dut.fdt.i.eq(self.fd_out)
            self.comb += self.dut.act.eq(self.act)
            self.comb += self.dut.wr.eq(self.wr)
            self.comb += self.dut.la.eq(self.la)
            self.comb += self.ioctl_rdy.eq(self.dut.ioctl_rdy)
            self.comb += self.iomodule_rdy.eq(self.dut.iomodule_rdy)

    def test_write(self):
        def gen():
            value = 0x2A

            yield self.tb.dut.ibus_m.maddr.eq(1)
            yield self.tb.dut.ibus_m.raddr.eq(1)

            yield self.tb.act.eq(0)
            yield self.tb.fd_out.eq(value)
            yield self.tb.wr.eq(1)
            yield self.tb.la.eq(0)
            yield
            self.assertEqual((yield self.tb.diom.select), 0)

            yield self.tb.act.eq(1)
            yield
            self.assertEqual((yield self.tb.dut.ibus_m.req), 0)
            self.assertEqual((yield self.tb.dut.ibus_m.mosi), value)

            yield
            self.assertEqual((yield self.tb.dut.ibus_m.req), 1)
            self.assertEqual((yield self.tb.dut.ibus_m.mosi), value)
            self.assertEqual((yield self.tb.dut.fdt.oe), 0)

            yield self.tb.act.eq(0)
            yield self.tb.fd_out.eq(0)
            yield self.tb.wr.eq(0)
            yield self.tb.la.eq(0)
            yield
            self.assertEqual((yield self.tb.diom.select), 1)

            yield
            self.assertEqual((yield self.tb.diom.select), 0)

            yield self.tb.dut.ibus_m.req.eq(0)
            yield
            self.assertEqual((yield self.tb.diom.cregs.REG2), value)

        self.run_with(gen())

    def test_read(self):
        def gen():
            yield self.tb.dut.ibus_m.maddr.eq(1)
            yield self.tb.dut.ibus_m.raddr.eq(0)

            yield self.tb.act.eq(0)
            yield self.tb.wr.eq(0)
            yield self.tb.la.eq(0)
            yield
            self.assertEqual((yield self.tb.diom.select), 0)

            yield self.tb.act.eq(1)
            yield
            self.assertEqual((yield self.tb.dut.ibus_m.req), 0)

            yield

            yield self.tb.act.eq(0)
            yield self.tb.fd_out.eq(0)
            yield self.tb.wr.eq(0)
            yield self.tb.la.eq(0)
            yield
            self.assertEqual((yield self.tb.diom.select), 1)
            self.assertEqual((yield self.tb.fd_in), 0x42)

            yield
            self.assertEqual((yield self.tb.diom.select), 0)

        self.run_with(gen())

    def test_read_wronly(self):
        def gen():
            yield self.tb.dut.ibus_m.maddr.eq(1)
            yield self.tb.dut.ibus_m.raddr.eq(1)
            yield self.tb.diom.cregs.REG3.eq(0x2A)

            yield self.tb.act.eq(0)
            yield self.tb.wr.eq(0)
            yield self.tb.la.eq(0)
            yield
            self.assertEqual((yield self.tb.diom.select), 0)

            yield self.tb.act.eq(1)
            yield
            self.assertEqual((yield self.tb.dut.ibus_m.req), 0)

            yield

            yield self.tb.act.eq(0)
            yield self.tb.fd_out.eq(0)
            yield self.tb.wr.eq(0)
            yield self.tb.la.eq(0)
            yield
            self.assertEqual((yield self.tb.diom.select), 1)
            self.assertEqual((yield self.tb.fd_in), 0)

            yield
            self.assertEqual((yield self.tb.diom.select), 0)

        self.run_with(gen())

    def test_write(self):
        def gen():
            value = 0x2A

            yield self.tb.dut.ibus_m.maddr.eq(1)
            yield self.tb.dut.ibus_m.raddr.eq(0)

            yield self.tb.act.eq(0)
            yield self.tb.fd_out.eq(value)
            yield self.tb.wr.eq(1)
            yield self.tb.la.eq(0)
            yield
            self.assertEqual((yield self.tb.diom.select), 0)

            yield self.tb.act.eq(1)
            yield
            self.assertEqual((yield self.tb.dut.ibus_m.req), 0)
            self.assertEqual((yield self.tb.dut.ibus_m.mosi), value)

            yield
            self.assertEqual((yield self.tb.dut.ibus_m.req), 1)
            self.assertEqual((yield self.tb.dut.ibus_m.mosi), value)
            self.assertEqual((yield self.tb.dut.fdt.oe), 0)

            yield self.tb.act.eq(0)
            yield self.tb.fd_out.eq(0)
            yield self.tb.wr.eq(0)
            yield self.tb.la.eq(0)
            yield
            self.assertEqual((yield self.tb.diom.select), 1)

            yield
            self.assertEqual((yield self.tb.diom.select), 0)

            yield self.tb.dut.ibus_m.req.eq(0)
            yield
            self.assertEqual((yield self.tb.diom.cregs.REG1), 0x42)

        self.run_with(gen())
