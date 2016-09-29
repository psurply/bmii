from enum import Enum
from migen import *

from bmii.ioctl.ibus import IBus
from bmii.ioctl.utils import *

REGSIZE = 8

class CtrlRegField(Signal):
    def __init__(self, name, size, offset):
        self.name = name
        self.size = size
        self.offset = offset
        Signal.__init__(self, size, name)

    def __repr__(self):
        return "<CtrlRegField " + self.name + " at " + hex(id(self)) + ">"


class CtrlRegDir(Enum):
    RDONLY  = 0
    WRONLY  = 1
    RDWR    = 2


class CtrlReg(Signal):
    def __init__(self, name, direction):
        self.name = name
        self.addr = 0
        self.direction = direction
        self.iomodule = None
        self.wr = Signal()
        self.wr_pulse = Signal()
        self.rd = Signal()
        self.rd_pulse = Signal()
        Signal.__init__(self, REGSIZE, name)

    def __setitem__(self, key, value):
        n = len(self)
        size = 0
        offset = 0
        if isinstance(key, int):
            if key >= n:
                raise IndexError
            size = 1
            offset = key
        elif isinstance(key, slice):
            start, stop, step = key.indices(n)
            if step == 1:
                size = stop - start
            offset = start
        else:
            raise TypeError("Cannot use type {} ({}) as key".format(
                type(key), repr(key)))

        field = CtrlRegField(value, size, offset)
        self.cregs.comb += field.eq(self[key])
        object.__setattr__(self, field.name, field)
        return self

    def __repr__(self):
        return "<CtrlReg " + self.name + "@" + hex(self.addr) + " at " + hex(id(self)) + ">"


class CtrlRegs(Module):
    def __init__(self, iomodule, ibus, select):
        self.ibus = ibus
        self.select = select
        self.reg_nb = 0
        self.iomodule = iomodule

    def __iadd__(self, creg):
        creg.cregs = self
        creg.addr = self.reg_nb
        creg.iomodule = self.iomodule

        if (creg.direction in [CtrlRegDir.WRONLY, CtrlRegDir.RDWR]):
            self.comb += creg.wr.eq(self.select
                    & self.ibus.wr
                    & (self.ibus.raddr == creg.addr))
            self.submodules += NLevelToPulse(creg.wr, creg.wr_pulse)
            self.sync += If(creg.wr,
                    creg.eq(self.ibus.mosi))

        if (creg.direction in [CtrlRegDir.RDONLY, CtrlRegDir.RDWR]):
            self.comb += creg.rd.eq(self.select
                    & ~self.ibus.wr
                    & (self.ibus.raddr == creg.addr))
            self.submodules += LevelToPulse(creg.rd, creg.rd_pulse)
            self.comb += If(creg.rd,
                    self.ibus.miso.eq(creg))

        object.__setattr__(self, creg.name, creg)
        self.reg_nb += 1
        return self


class IOSignalDir(Enum):
    IN  = 0
    OUT = 1
    DIRCTL = 2


class IOSignal(Signal):
    def __init__(self, name, direction):
        self.name = name
        self.direction = direction
        Signal.__init__(self, 1, name)

    def __repr__(self):
        return "<{} {}>".format(self.name, self.direction)


class IOSignals(Module):
    def __iadd__(self, iosignal):
        object.__setattr__(self, iosignal.name, iosignal)
        return self


class IOModule(Module):
    def __init__(self, name, shadowed=False):
        self.name = name
        self.addr = 0
        self.shadowed = shadowed
        self.ibus = Record(IBus)

        self.select = Signal()
        self.cregs = CtrlRegs(self, self.ibus, self.select)
        self.iosignals = IOSignals()
        self.submodules += self.cregs
        self.submodules += self.iosignals

    def set_addr(self, addr):
        self.addr = addr
        if not self.shadowed:
            self.comb += self.select.eq(self.ibus.req &
                    (self.ibus.maddr == self.addr))

    def __repr__(self):
        return "<IOModule " + self.name + "@" + hex(self.addr) + " at " + hex(id(self)) + ">"
