from bmii.ioctl.testbench import *
from bmii import *


class PWM(BMIIModule):
    class PWMIOModule(IOModule):
        def __init__(self):
            IOModule.__init__(self, "PWM")

            self.cregs += CtrlReg("WIDTH", CtrlRegDir.RDWR)
            self.cregs += CtrlReg("COUNTER", CtrlRegDir.RDONLY)

            self.sync += self.cregs.COUNTER.eq(self.cregs.COUNTER + 1)

            self.iosignals += IOSignal("OUT", IOSignalDir.OUT)
            self.iosignals += IOSignal("NOUT", IOSignalDir.OUT)
            self.comb += self.iosignals.OUT.eq(self.cregs.COUNTER < self.cregs.WIDTH)
            self.comb += self.iosignals.NOUT.eq(~self.iosignals.OUT)

    class PWMTestCase(IOModuleTestCase(PWMIOModule())):
        def test_basic(self):
            def gen():
                yield self.tb.iomodule.cregs.WIDTH.eq(42)
                yield

                for i in range(41):
                    self.assertEqual((yield self.tb.iomodule.iosignals.OUT), 1)
                    yield

                for i in range(214):
                    self.assertEqual((yield self.tb.iomodule.iosignals.OUT), 0)
                    yield

                self.assertEqual((yield self.tb.iomodule.iosignals.OUT), 1)

            self.run_with(gen())

    def __init__(self):
        BMIIModule.__init__(self, self.PWMIOModule(), self.PWMTestCase)

    def set(self, value):
        self.drv.WIDTH = value
