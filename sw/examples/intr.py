from bmii import *


class TimerIOModule(IOModule):
    def __init__(self, width):
        IOModule.__init__(self, "timer")

        cnt = Signal(width)
        self.sync += cnt.eq(cnt + 1)

        self.intrs += IntRequest("OVF", cnt == 0)


class Timer(BMIIModule):
    def __init__(self, width):
        BMIIModule.__init__(self, TimerIOModule(width))

    @interrupt_handler("OVF")
    def handle_overflow(self, bmii):
        logging.info("Timer overflow")

    @classmethod
    def default(cls, bmii):
        timer = cls(26)
        bmii.add_module(timer)

        bmii.ioctl.nb.interrupts += timer.iomodule.intrs.OVF

        return timer


class IntPushButtonIOModule(IOModule):
    def __init__(self):
        IOModule.__init__(self, "int_push_button")

        self.iosignals += IOSignal("IN", IOSignalDir.IN)

        pressed = Signal()
        released = Signal()

        self.submodules.pressed = LevelToPulse(~self.iosignals.IN, pressed)
        self.submodules.released = NLevelToPulse(~self.iosignals.IN, released)

        self.intrs += IntRequest("PRESSED", pressed)
        self.intrs += IntRequest("RELEASED", released)


class IntPushButton(BMIIModule):
    def __init__(self):
        BMIIModule.__init__(self, IntPushButtonIOModule())

    @interrupt_handler("PRESSED")
    def handle_pressed(self, bmii):
        logging.info("Push button pressed")

    @interrupt_handler("RELEASED")
    def handle_released(self, bmii):
        logging.info("Push button released")

    @classmethod
    def default(cls, bmii):
        ipb = cls()
        bmii.add_module(ipb)

        bmii.ioctl.sb.pins.SW += ipb.iomodule.iosignals.IN
        bmii.ioctl.nb.interrupts += ipb.iomodule.intrs.PRESSED
        bmii.ioctl.nb.interrupts += ipb.iomodule.intrs.RELEASED

        return ipb


bmii_modules = [IntPushButton, Timer]

if __name__ == "__main__":
    b = BMII.default()
    ipb = IntPushButton.default(b)
    timer = Timer.default(b)

    b.cli()
