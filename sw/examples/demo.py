#!/usr/bin/env python3

import argparse

from bmii import *
from bmii.modules import pwm
from bmii.modules import fifo

class Demo(BMII):
    def __init__(self):
        BMII.__init__(self)

        self.pwm = pwm.PWM()
        self.add_module(self.pwm)

        self.fifo = fifo.FIFO()
        self.add_module(self.fifo)

        self.ioctl.sb.pins.LED0 += self.pwm.iomodule.iosignals.NOUT

    def toggle_led(self):
        self.modules.southbridge.drv.PINMUXMISC.LED1 = 1
        self.modules.southbridge.drv.PINOUTMISC.LED1 = \
            int(self.modules.southbridge.drv.PINSCANMISC.LED1) ^ 1

    def scan(self):
        print([[int(self.modules.southbridge.drv.PINSCAN1L),
                 int(self.modules.southbridge.drv.PINSCAN1H)],
                [int(self.modules.southbridge.drv.PINSCAN2L),
                 int(self.modules.southbridge.drv.PINSCAN2H)],
                int(self.modules.southbridge.drv.PINSCANMISC)])

    def get_pb_state(self):
        print(self.modules.southbridge.drv.PINSCANMISC.SW == 0)

    def cli(self):
        functions = {
                "toggle_led": self.toggle_led,
                "scan": self.scan,
                "pb": self.get_pb_state
                }

        demo_parser = self.subparser.add_parser(name="demo")
        demo_parser.add_argument("cmd", choices=functions.keys())
        demo_parser.set_defaults(action="demo")

        BMII.cli(self)

        if self.args.action == "demo":
            functions[self.args.cmd]()


if __name__ == "__main__":
    demo = Demo()
    demo.cli()
