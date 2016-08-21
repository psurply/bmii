import unittest
from migen import *
from migen.test.support import SimCase

from bmii.ioctl.south_bridge import SouthBridge

class SouthBridgeCase(SimCase, unittest.TestCase):
    class TestBench(Module):
        def __init__(self):
            self.submodules.dut = SouthBridge("southbridge")

    def test_pinout(self):
        def gen():
            yield self.tb.dut.cregs.PINMUX2H.IO28.eq(0)
            yield self.tb.dut.cregs.PINOUT2H.eq(0)
            yield
            self.assertEqual((yield self.tb.dut.cregs.PINOUT2H.IO28), 0)
            yield self.tb.dut.cregs.PINOUT2H.eq(1)
            yield
            self.assertEqual((yield self.tb.dut.cregs.PINOUT2H.IO28), 1)
        self.run_with(gen())

    def test_pinscan(self):
        def gen():
            yield self.tb.dut.pins.IO18.t.i.eq(0)
            yield
            self.assertEqual((yield self.tb.dut.cregs.PINSCAN1H.IO18), 0)
            yield self.tb.dut.pins.IO18.t.i.eq(1)
            yield
            self.assertEqual((yield self.tb.dut.cregs.PINSCAN1H.IO18), 1)
        self.run_with(gen())
