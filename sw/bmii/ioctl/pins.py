from migen import *
from bmii.ioctl.iomodule import CtrlReg, CtrlRegDir, IOSignalDir

PINMUX_WIDTH = 2

class Pin(Module):
    def __init__(self, name, mux_out_select, scan,
            regout=0, direction=0, mux_dir_select=0):
        self.name = name

        self.t = TSTriple()
        self.mux_out = Array(Signal() for x in range(PINMUX_WIDTH))
        self.mux_dir = Array(Signal() for x in range(PINMUX_WIDTH))

        self.comb += self.mux_out[1].eq(regout)
        self.comb += self.t.o.eq(self.mux_out[mux_out_select])

        self.comb += self.mux_dir[0].eq(0)
        self.comb += self.mux_dir[1].eq(direction)
        self.comb += self.t.oe.eq(self.mux_dir[mux_dir_select])

        self.comb += scan.eq(self.t.i)

    def __iadd__(self, iosignal):
        if iosignal.direction == IOSignalDir.IN:
            self.comb += iosignal.eq(self.t.i)
        elif iosignal.direction == IOSignalDir.OUT:
            self.comb += self.mux_out[0].eq(iosignal)
            self.comb += self.mux_dir[0].eq(1)
        elif iosignal.direction == IOSignalDir.DIRCTL:
            self.comb += self.mux_dir[0].eq(iosignal)
        return self

    def connect_realpin(self, real_pin):
        self.specials += self.t.get_tristate(real_pin)


class Pins(Module):
    def __iadd__(self, pin):
        object.__setattr__(self, pin.name, pin)
        self.submodules += pin
        return self

def define_bmii_pins(cr):
    cr += CtrlReg("PINDIR1L", CtrlRegDir.RDWR)
    cr.PINDIR1L[0] = "IO10"
    cr.PINDIR1L[1] = "IO11"
    cr.PINDIR1L[2] = "IO12"
    cr.PINDIR1L[3] = "IO13"
    cr.PINDIR1L[4] = "IO14"
    cr.PINDIR1L[5] = "IO15"
    cr.PINDIR1L[6] = "IO16"
    cr.PINDIR1L[7] = "IO17"

    cr += CtrlReg("PINDIR1H", CtrlRegDir.RDWR)
    cr.PINDIR1H[0] = "IO18"
    cr.PINDIR1H[1] = "IO19"
    cr.PINDIR1H[2] = "IO1A"
    cr.PINDIR1H[3] = "IO1B"
    cr.PINDIR1H[4] = "IO1C"
    cr.PINDIR1H[5] = "IO1D"
    cr.PINDIR1H[6] = "IO1E"
    cr.PINDIR1H[7] = "IO1F"

    cr += CtrlReg("PINDIR2L", CtrlRegDir.RDWR)
    cr.PINDIR2L[0] = "IO20"
    cr.PINDIR2L[1] = "IO21"
    cr.PINDIR2L[2] = "IO22"
    cr.PINDIR2L[3] = "IO23"
    cr.PINDIR2L[4] = "IO24"
    cr.PINDIR2L[5] = "IO25"
    cr.PINDIR2L[6] = "IO26"
    cr.PINDIR2L[7] = "IO27"

    cr += CtrlReg("PINDIR2H", CtrlRegDir.RDWR)
    cr.PINDIR2H[0] = "IO28"
    cr.PINDIR2H[1] = "IO29"
    cr.PINDIR2H[2] = "IO2A"
    cr.PINDIR2H[3] = "IO2B"
    cr.PINDIR2H[4] = "IO2C"
    cr.PINDIR2H[5] = "IO2D"
    cr.PINDIR2H[6] = "IO2E"
    cr.PINDIR2H[7] = "IO2F"

    cr += CtrlReg("PINSCAN1L", CtrlRegDir.RDONLY)
    cr.PINSCAN1L[0] = "IO10"
    cr.PINSCAN1L[1] = "IO11"
    cr.PINSCAN1L[2] = "IO12"
    cr.PINSCAN1L[3] = "IO13"
    cr.PINSCAN1L[4] = "IO14"
    cr.PINSCAN1L[5] = "IO15"
    cr.PINSCAN1L[6] = "IO16"
    cr.PINSCAN1L[7] = "IO17"

    cr += CtrlReg("PINSCAN1H", CtrlRegDir.RDONLY)
    cr.PINSCAN1H[0] = "IO18"
    cr.PINSCAN1H[1] = "IO19"
    cr.PINSCAN1H[2] = "IO1A"
    cr.PINSCAN1H[3] = "IO1B"
    cr.PINSCAN1H[4] = "IO1C"
    cr.PINSCAN1H[5] = "IO1D"
    cr.PINSCAN1H[6] = "IO1E"
    cr.PINSCAN1H[7] = "IO1F"

    cr += CtrlReg("PINSCAN2L", CtrlRegDir.RDONLY)
    cr.PINSCAN2L[0] = "IO20"
    cr.PINSCAN2L[1] = "IO21"
    cr.PINSCAN2L[2] = "IO22"
    cr.PINSCAN2L[3] = "IO23"
    cr.PINSCAN2L[4] = "IO24"
    cr.PINSCAN2L[5] = "IO25"
    cr.PINSCAN2L[6] = "IO26"
    cr.PINSCAN2L[7] = "IO27"

    cr += CtrlReg("PINSCAN2H", CtrlRegDir.RDONLY)
    cr.PINSCAN2H[0] = "IO28"
    cr.PINSCAN2H[1] = "IO29"
    cr.PINSCAN2H[2] = "IO2A"
    cr.PINSCAN2H[3] = "IO2B"
    cr.PINSCAN2H[4] = "IO2C"
    cr.PINSCAN2H[5] = "IO2D"
    cr.PINSCAN2H[6] = "IO2E"
    cr.PINSCAN2H[7] = "IO2F"

    cr += CtrlReg("PINSCANMISC", CtrlRegDir.RDONLY)
    cr.PINSCANMISC[0] = "LED0"
    cr.PINSCANMISC[1] = "LED1"
    cr.PINSCANMISC[2] = "SW"

    cr += CtrlReg("PINMUX1L", CtrlRegDir.RDWR)
    cr.PINMUX1L[0] = "IO10"
    cr.PINMUX1L[1] = "IO11"
    cr.PINMUX1L[2] = "IO12"
    cr.PINMUX1L[3] = "IO13"
    cr.PINMUX1L[4] = "IO14"
    cr.PINMUX1L[5] = "IO15"
    cr.PINMUX1L[6] = "IO16"
    cr.PINMUX1L[7] = "IO17"

    cr += CtrlReg("PINMUX1H", CtrlRegDir.RDWR)
    cr.PINMUX1H[0] = "IO18"
    cr.PINMUX1H[1] = "IO19"
    cr.PINMUX1H[2] = "IO1A"
    cr.PINMUX1H[3] = "IO1B"
    cr.PINMUX1H[4] = "IO1C"
    cr.PINMUX1H[5] = "IO1D"
    cr.PINMUX1H[6] = "IO1E"
    cr.PINMUX1H[7] = "IO1F"

    cr += CtrlReg("PINMUX2L", CtrlRegDir.RDWR)
    cr.PINMUX2L[0] = "IO20"
    cr.PINMUX2L[1] = "IO21"
    cr.PINMUX2L[2] = "IO22"
    cr.PINMUX2L[3] = "IO23"
    cr.PINMUX2L[4] = "IO24"
    cr.PINMUX2L[5] = "IO25"
    cr.PINMUX2L[6] = "IO26"
    cr.PINMUX2L[7] = "IO27"

    cr += CtrlReg("PINMUX2H", CtrlRegDir.RDWR)
    cr.PINMUX2H[0] = "IO28"
    cr.PINMUX2H[1] = "IO29"
    cr.PINMUX2H[2] = "IO2A"
    cr.PINMUX2H[3] = "IO2B"
    cr.PINMUX2H[4] = "IO2C"
    cr.PINMUX2H[5] = "IO2D"
    cr.PINMUX2H[6] = "IO2E"
    cr.PINMUX2H[7] = "IO2F"

    cr += CtrlReg("PINDIRMUX1L", CtrlRegDir.RDWR)
    cr.PINDIRMUX1L[0] = "IO10"
    cr.PINDIRMUX1L[1] = "IO11"
    cr.PINDIRMUX1L[2] = "IO12"
    cr.PINDIRMUX1L[3] = "IO13"
    cr.PINDIRMUX1L[4] = "IO14"
    cr.PINDIRMUX1L[5] = "IO15"
    cr.PINDIRMUX1L[6] = "IO16"
    cr.PINDIRMUX1L[7] = "IO17"

    cr += CtrlReg("PINDIRMUX1H", CtrlRegDir.RDWR)
    cr.PINDIRMUX1H[0] = "IO18"
    cr.PINDIRMUX1H[1] = "IO19"
    cr.PINDIRMUX1H[2] = "IO1A"
    cr.PINDIRMUX1H[3] = "IO1B"
    cr.PINDIRMUX1H[4] = "IO1C"
    cr.PINDIRMUX1H[5] = "IO1D"
    cr.PINDIRMUX1H[6] = "IO1E"
    cr.PINDIRMUX1H[7] = "IO1F"

    cr += CtrlReg("PINDIRMUX2L", CtrlRegDir.RDWR)
    cr.PINDIRMUX2L[0] = "IO20"
    cr.PINDIRMUX2L[1] = "IO21"
    cr.PINDIRMUX2L[2] = "IO22"
    cr.PINDIRMUX2L[3] = "IO23"
    cr.PINDIRMUX2L[4] = "IO24"
    cr.PINDIRMUX2L[5] = "IO25"
    cr.PINDIRMUX2L[6] = "IO26"
    cr.PINDIRMUX2L[7] = "IO27"

    cr += CtrlReg("PINDIRMUX2H", CtrlRegDir.RDWR)
    cr.PINDIRMUX2H[0] = "IO28"
    cr.PINDIRMUX2H[1] = "IO29"
    cr.PINDIRMUX2H[2] = "IO2A"
    cr.PINDIRMUX2H[3] = "IO2B"
    cr.PINDIRMUX2H[4] = "IO2C"
    cr.PINDIRMUX2H[5] = "IO2D"
    cr.PINDIRMUX2H[6] = "IO2E"
    cr.PINDIRMUX2H[7] = "IO2F"

    cr += CtrlReg("PINMUXMISC", CtrlRegDir.RDWR)
    cr.PINMUXMISC[0] = "LED0"
    cr.PINMUXMISC[1] = "LED1"

    cr += CtrlReg("PINOUT1L", CtrlRegDir.RDWR)
    cr.PINOUT1L[0] = "IO10"
    cr.PINOUT1L[1] = "IO11"
    cr.PINOUT1L[2] = "IO12"
    cr.PINOUT1L[3] = "IO13"
    cr.PINOUT1L[4] = "IO14"
    cr.PINOUT1L[5] = "IO15"
    cr.PINOUT1L[6] = "IO16"
    cr.PINOUT1L[7] = "IO17"

    cr += CtrlReg("PINOUT1H", CtrlRegDir.RDWR)
    cr.PINOUT1H[0] = "IO18"
    cr.PINOUT1H[1] = "IO19"
    cr.PINOUT1H[2] = "IO1A"
    cr.PINOUT1H[3] = "IO1B"
    cr.PINOUT1H[4] = "IO1C"
    cr.PINOUT1H[5] = "IO1D"
    cr.PINOUT1H[6] = "IO1E"
    cr.PINOUT1H[7] = "IO1F"

    cr += CtrlReg("PINOUT2L", CtrlRegDir.RDWR)
    cr.PINOUT2L[0] = "IO20"
    cr.PINOUT2L[1] = "IO21"
    cr.PINOUT2L[2] = "IO22"
    cr.PINOUT2L[3] = "IO23"
    cr.PINOUT2L[4] = "IO24"
    cr.PINOUT2L[5] = "IO25"
    cr.PINOUT2L[6] = "IO26"
    cr.PINOUT2L[7] = "IO27"

    cr += CtrlReg("PINOUT2H", CtrlRegDir.RDWR)
    cr.PINOUT2H[0] = "IO28"
    cr.PINOUT2H[1] = "IO29"
    cr.PINOUT2H[2] = "IO2A"
    cr.PINOUT2H[3] = "IO2B"
    cr.PINOUT2H[4] = "IO2C"
    cr.PINOUT2H[5] = "IO2D"
    cr.PINOUT2H[6] = "IO2E"
    cr.PINOUT2H[7] = "IO2F"

    cr += CtrlReg("PINOUTMISC", CtrlRegDir.RDWR)
    cr.PINOUTMISC[0] = "LED0"
    cr.PINOUTMISC[1] = "LED1"

    pins = Pins()
    pins += Pin("IO10", cr.PINMUX1L.IO10, cr.PINSCAN1L[0], cr.PINOUT1L.IO10, cr.PINDIR1L.IO10, cr.PINDIRMUX1L.IO10)
    pins += Pin("IO11", cr.PINMUX1L.IO11, cr.PINSCAN1L[1], cr.PINOUT1L.IO11, cr.PINDIR1L.IO11, cr.PINDIRMUX1L.IO11)
    pins += Pin("IO12", cr.PINMUX1L.IO12, cr.PINSCAN1L[2], cr.PINOUT1L.IO12, cr.PINDIR1L.IO12, cr.PINDIRMUX1L.IO12)
    pins += Pin("IO13", cr.PINMUX1L.IO13, cr.PINSCAN1L[3], cr.PINOUT1L.IO13, cr.PINDIR1L.IO13, cr.PINDIRMUX1L.IO13)
    pins += Pin("IO14", cr.PINMUX1L.IO14, cr.PINSCAN1L[4], cr.PINOUT1L.IO14, cr.PINDIR1L.IO14, cr.PINDIRMUX1L.IO14)
    pins += Pin("IO15", cr.PINMUX1L.IO15, cr.PINSCAN1L[5], cr.PINOUT1L.IO15, cr.PINDIR1L.IO15, cr.PINDIRMUX1L.IO15)
    pins += Pin("IO16", cr.PINMUX1L.IO16, cr.PINSCAN1L[6], cr.PINOUT1L.IO16, cr.PINDIR1L.IO16, cr.PINDIRMUX1L.IO16)
    pins += Pin("IO17", cr.PINMUX1L.IO17, cr.PINSCAN1L[7], cr.PINOUT1L.IO17, cr.PINDIR1L.IO17, cr.PINDIRMUX1L.IO17)
    pins += Pin("IO18", cr.PINMUX1H.IO18, cr.PINSCAN1H[0], cr.PINOUT1H.IO18, cr.PINDIR1H.IO18, cr.PINDIRMUX1H.IO18)
    pins += Pin("IO19", cr.PINMUX1H.IO19, cr.PINSCAN1H[1], cr.PINOUT1H.IO19, cr.PINDIR1H.IO19, cr.PINDIRMUX1H.IO19)
    pins += Pin("IO1A", cr.PINMUX1H.IO1A, cr.PINSCAN1H[2], cr.PINOUT1H.IO1A, cr.PINDIR1H.IO1A, cr.PINDIRMUX1H.IO1A)
    pins += Pin("IO1B", cr.PINMUX1H.IO1B, cr.PINSCAN1H[3], cr.PINOUT1H.IO1B, cr.PINDIR1H.IO1B, cr.PINDIRMUX1H.IO1B)
    pins += Pin("IO1C", cr.PINMUX1H.IO1C, cr.PINSCAN1H[4], cr.PINOUT1H.IO1C, cr.PINDIR1H.IO1C, cr.PINDIRMUX1H.IO1C)
    pins += Pin("IO1D", cr.PINMUX1H.IO1D, cr.PINSCAN1H[5], cr.PINOUT1H.IO1D, cr.PINDIR1H.IO1D, cr.PINDIRMUX1H.IO1D)
    pins += Pin("IO1E", cr.PINMUX1H.IO1E, cr.PINSCAN1H[6], cr.PINOUT1H.IO1E, cr.PINDIR1H.IO1E, cr.PINDIRMUX1H.IO1E)
    pins += Pin("IO1F", cr.PINMUX1H.IO1F, cr.PINSCAN1H[7], cr.PINOUT1H.IO1F, cr.PINDIR1H.IO1F, cr.PINDIRMUX1H.IO1F)

    pins += Pin("IO20", cr.PINMUX2L.IO20, cr.PINSCAN2L[0], cr.PINOUT2L.IO20, cr.PINDIR2L.IO20, cr.PINDIRMUX2L.IO20)
    pins += Pin("IO21", cr.PINMUX2L.IO21, cr.PINSCAN2L[1], cr.PINOUT2L.IO21, cr.PINDIR2L.IO21, cr.PINDIRMUX2L.IO21)
    pins += Pin("IO22", cr.PINMUX2L.IO22, cr.PINSCAN2L[2], cr.PINOUT2L.IO22, cr.PINDIR2L.IO22, cr.PINDIRMUX2L.IO22)
    pins += Pin("IO23", cr.PINMUX2L.IO23, cr.PINSCAN2L[3], cr.PINOUT2L.IO23, cr.PINDIR2L.IO23, cr.PINDIRMUX2L.IO23)
    pins += Pin("IO24", cr.PINMUX2L.IO24, cr.PINSCAN2L[4], cr.PINOUT2L.IO24, cr.PINDIR2L.IO24, cr.PINDIRMUX2L.IO24)
    pins += Pin("IO25", cr.PINMUX2L.IO25, cr.PINSCAN2L[5], cr.PINOUT2L.IO25, cr.PINDIR2L.IO25, cr.PINDIRMUX2L.IO25)
    pins += Pin("IO26", cr.PINMUX2L.IO26, cr.PINSCAN2L[6], cr.PINOUT2L.IO26, cr.PINDIR2L.IO26, cr.PINDIRMUX2L.IO26)
    pins += Pin("IO27", cr.PINMUX2L.IO27, cr.PINSCAN2L[7], cr.PINOUT2L.IO27, cr.PINDIR2L.IO27, cr.PINDIRMUX2L.IO27)
    pins += Pin("IO28", cr.PINMUX2H.IO28, cr.PINSCAN2H[0], cr.PINOUT2H.IO28, cr.PINDIR2H.IO28, cr.PINDIRMUX2H.IO28)
    pins += Pin("IO29", cr.PINMUX2H.IO29, cr.PINSCAN2H[1], cr.PINOUT2H.IO29, cr.PINDIR2H.IO29, cr.PINDIRMUX2H.IO29)
    pins += Pin("IO2A", cr.PINMUX2H.IO2A, cr.PINSCAN2H[2], cr.PINOUT2H.IO2A, cr.PINDIR2H.IO2A, cr.PINDIRMUX2H.IO2A)
    pins += Pin("IO2B", cr.PINMUX2H.IO2B, cr.PINSCAN2H[3], cr.PINOUT2H.IO2B, cr.PINDIR2H.IO2B, cr.PINDIRMUX2H.IO2B)
    pins += Pin("IO2C", cr.PINMUX2H.IO2C, cr.PINSCAN2H[4], cr.PINOUT2H.IO2C, cr.PINDIR2H.IO2C, cr.PINDIRMUX2H.IO2C)
    pins += Pin("IO2D", cr.PINMUX2H.IO2D, cr.PINSCAN2H[5], cr.PINOUT2H.IO2D, cr.PINDIR2H.IO2D, cr.PINDIRMUX2H.IO2D)
    pins += Pin("IO2E", cr.PINMUX2H.IO2E, cr.PINSCAN2H[6], cr.PINOUT2H.IO2E, cr.PINDIR2H.IO2E, cr.PINDIRMUX2H.IO2E)
    pins += Pin("IO2F", cr.PINMUX2H.IO2F, cr.PINSCAN2H[7], cr.PINOUT2H.IO2F, cr.PINDIR2H.IO2F, cr.PINDIRMUX2H.IO2F)

    pins += Pin("LED0", cr.PINMUXMISC.LED0, cr.PINSCANMISC[0], cr.PINOUTMISC.LED0, 1, 1)
    pins += Pin("LED1", cr.PINMUXMISC.LED1, cr.PINSCANMISC[1], cr.PINOUTMISC.LED1, 1, 1)
    pins += Pin("SW", 0, cr.PINSCANMISC[2])

    return pins

# vim: textwidth=120
