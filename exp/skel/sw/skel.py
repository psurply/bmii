#! /usr/bin/bmii -m

from bmii import *
from bmii.ioctl.testbench import *


class SkelIOModule(IOModule):
    """ Skeleton of an IO Module """

    def __init__(self):
        IOModule.__init__(self, "skel")

        # Control registers
        self.cregs += CtrlReg("STATUS", CtrlRegDir.RDONLY)

        # IO signals
        self.iosignals += IOSignal("IN", IOSignalDir.IN)

        # Internal logic
        self.comb += self.cregs.STATUS.eq(self.iosignals.IN)


class SkelTestCase(IOModuleTestCase(SkelIOModule())):
    """Skel simulation test bench (optional)

    Example:
        $ bmii -m skel simulate skel
    """
    def test_pb(self):
        def gen():
            yield self.tb.iomodule.iosignals.IN.eq(0)
            yield
            yield from self.ibus_read_creg(self.tb.iomodule.cregs.STATUS)
            yield

            self.assertEqual((yield self.tb.ibus_m.miso), 0)

            yield self.tb.iomodule.iosignals.IN.eq(1)
            yield
            yield from self.ibus_read_creg(self.tb.iomodule.cregs.STATUS)
            yield

            self.assertEqual((yield self.tb.ibus_m.miso), 1)

        self.run_with(gen())


class Skel(BMIIModule):
    """ Skeleton of a BMII Module """

    def __init__(self):
        BMIIModule.__init__(self, SkelIOModule(), SkelTestCase)

    @classmethod
    def default(cls, bmii):
        """Define the default connections of the module"""
        skel = cls()
        bmii.add_module(skel)

        bmii.ioctl.sb.pins.SW += skel.iomodule.iosignals.IN

        return skel

    def get_status(self):
        """Get push button status

        Example:
            $ bmii -m skel eval 'self.iomodule.skel.get_status()'
            RELEASED
        """

        if int(self.drv.STATUS):
            return "RELEASED"
        else:
            return "PRESSED"

# List of BMII Module exposed by this file
bmii_modules = [Skel]
