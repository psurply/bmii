from bmii import *
from bmii.modules import pwm

class BasicModule(BMIIModule):
    class BasicIOModule(IOModule):
        def __init__(self):
            IOModule.__init__(self, "basic")

            self.cregs += CtrlReg("STATUS", CtrlRegDir.RDONLY)
            self.cregs.STATUS[0] = "SW"

            self.iosignals += IOSignal("BMIN", IOSignalDir.IN)
            self.iosignals += IOSignal("BMOUT", IOSignalDir.OUT)

            self.comb += self.iosignals.BMOUT.eq(self.iosignals.BMIN)
            self.comb += self.cregs.STATUS[0].eq(self.iosignals.BMIN)

    def __init__(self):
        BMIIModule.__init__(self, self.BasicIOModule())

if __name__ == "__main__":
    b = BMII()
    bm = BasicModule()
    pwm = pwm.PWM()

    b.add_module(bm)
    b.add_module(pwm)

    b.ioctl.sb.pins.LED0 += bm.iomodule.iosignals.BMOUT
    b.ioctl.sb.pins.LED1 += pwm.iomodule.iosignals.OUT
    b.ioctl.sb.pins.SW += bm.iomodule.iosignals.BMIN

    b.ioctl.program()
