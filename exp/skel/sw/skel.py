#! /usr/bin/bmii -m

from bmii import *


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


class Skel(BMIIModule):
    """ Skeleton of a BMII Module """

    def __init__(self):
        BMIIModule.__init__(self, SkelIOModule())

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
