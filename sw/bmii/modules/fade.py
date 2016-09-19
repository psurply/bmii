from bmii import *


class Fade(BMIIModule):
    class FadeIOModule(IOModule):
        def __init__(self):
            IOModule.__init__(self, "fade")

            self.cregs += CtrlReg("COUNTER", CtrlRegDir.RDONLY)

            self.sync += self.cregs.COUNTER.eq(self.cregs.COUNTER + 1)

            width = Signal(8)
            fadecounter = Signal(32)
            fadedir = Signal()
            self.sync += If(fadedir, fadecounter.eq(fadecounter - 1))\
                    .Else(fadecounter.eq(fadecounter + 1))
            self.sync += If(width == 0, fadedir.eq(0))\
                    .Elif(width == 0xFF, fadedir.eq(1))
            self.comb += width.eq(fadecounter[16:24])

            self.iosignals += IOSignal("OUT", IOSignalDir.OUT)
            self.iosignals += IOSignal("NOUT", IOSignalDir.OUT)

            self.comb += self.iosignals.OUT.eq(self.cregs.COUNTER < width)
            self.comb += self.iosignals.NOUT.eq(~self.iosignals.OUT)

    def __init__(self):
        BMIIModule.__init__(self, self.FadeIOModule())
