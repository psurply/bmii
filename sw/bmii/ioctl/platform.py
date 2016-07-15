from migen.build.generic_platform import *
from migen.build.altera import AlteraPlatform
from migen.build.altera.programmer import USBBlaster

_io = [
    ("clk0",    0, Pins("12"),              IOStandard("3.3-V LVTTL")),
    ("clk1",    1, Pins("14"),              IOStandard("3.3-V LVTTL")),
    ("clk2",    2, Pins("62"),              IOStandard("3.3-V LVTTL")),
    ("clk3",    3, Pins("64"),              IOStandard("3.3-V LVTTL")),

    ("led",     0, Pins("52 53"),           IOStandard("3.3-V LVTTL")),

    ("sw",      0, Pins("5"),               IOStandard("3.3-V LVTTL")),
    ("reset0",  0, Pins("4"),               IOStandard("3.3-V LVTTL")),
    ("reset1",  0, Pins("44"),              IOStandard("3.3-V LVTTL")),

    ("ifclk",   0, Pins("73"),              IOStandard("3.3-V LVTTL")),
    ("fd",      0, Pins("72 71 70 69 21 20 19 18"),
                                            IOStandard("3.3-V LVTTL")),
    ("ctl",     0, Pins("17 16 15"),
                                            IOStandard("3.3-V LVTTL")),
    ("rdy",     0, Pins("75 74"),
                                            IOStandard("3.3-V LVTTL")),
    ("intr",    0, Pins("7 6"),             IOStandard("3.3-V LVTTL")),

    ("io1",     0, Pins("27 26 29 28 33 30 35 34 38 36 41 40 47 42 49 48"),
                                            IOStandard("3.3-V LVTTL")),
    ("io2",     0, Pins("99 100 97 98 92 96 89 91 86 87 84 85 82 83 78 81"),
                                            IOStandard("3.3-V LVTTL")),
]

class BMIIPlatform(AlteraPlatform):
    default_clk_name = "clk2"
    default_clk_preriod = 24

    def __init__(self):
        AlteraPlatform.__init__(self, "5M570ZT100C5", _io)

    def create_programmer(self):
        return USBBlaster()
