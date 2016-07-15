from enum import IntEnum
from bmii import *
from migen.genlib.fifo import *
from migen.genlib.fsm import *
from bitarray import bitarray

class TAPState(IntEnum):
    RESET       = 0
    IDLE        = 1
    DRSELECT    = 2
    DRCAPTURE   = 3
    DRSHIFT     = 4
    DREXIT1     = 5
    DRPAUSE     = 6
    DREXIT2     = 7
    DRUPDATE    = 8
    IRSELECT    = 9
    IRCAPTURE   = 10
    IRSHIFT     = 11
    IREXIT1     = 12
    IRPAUSE     = 13
    IREXIT2     = 14
    IRUPDATE    = 15


class JTAGIOModule(IOModule):
    def __init__(self, buff_size=64):
        IOModule.__init__(self, "JTAG")

        self.cregs += CtrlReg("STATE", CtrlRegDir.RDONLY)
        self.cregs += CtrlReg("TDR", CtrlRegDir.WRONLY)
        self.cregs.TDR[0] = "TMS"
        self.cregs.TDR[1] = "TDI"
        self.cregs += CtrlReg("RDR", CtrlRegDir.RDONLY)
        self.cregs.RDR[0] = "TDO"
        self.cregs.RDR[1] = "VALID"
        self.cregs += CtrlReg("CTRL", CtrlRegDir.WRONLY)
        self.cregs.CTRL[0] = "TRST"

        self.iosignals += IOSignal("TCK", IOSignalDir.OUT)
        self.iosignals += IOSignal("TMS", IOSignalDir.OUT)
        self.iosignals += IOSignal("TDI", IOSignalDir.OUT)
        self.iosignals += IOSignal("TDO", IOSignalDir.IN)
        self.iosignals += IOSignal("TRST", IOSignalDir.OUT)

        recv_queue = SyncFIFO(1, buff_size)
        self.submodules.fifo = recv_queue

        tck_pulse = Signal()
        self.comb += tck_pulse.eq(self.cregs.TDR.wr_pulse)
        tck = Signal(10)
        self.sync += If(tck_pulse, tck.eq(1)).Elif(tck != 0, tck.eq(tck + 1))

        self.comb += self.iosignals.TCK.eq(~(tck != 0))
        self.comb += self.iosignals.TMS.eq(~self.cregs.TDR.TMS)
        self.comb += self.iosignals.TDI.eq(~self.cregs.TDR.TDI)
        self.comb += self.iosignals.TRST.eq(~self.cregs.CTRL.TRST)

        self.comb += self.cregs.RDR[0].eq(recv_queue.dout)
        self.comb += self.cregs.RDR[1].eq(recv_queue.readable)
        self.comb += recv_queue.re.eq(self.cregs.RDR.rd_pulse)

        self.comb += recv_queue.we.eq(tck_pulse & \
                ((self.cregs.STATE == TAPState.DRSHIFT) | \
                 (self.cregs.STATE == TAPState.IRSHIFT)))
        self.comb += recv_queue.din.eq(self.iosignals.TDO)

        tap = FSM()
        self.submodules += tap

        def tr(s1, s2):
            return If(tck_pulse,
                    If(self.cregs.TDR.TMS, NextState(s1)).Else(NextState(s2)))

        tap.act("RESET",
                self.cregs.STATE.eq(TAPState.RESET),
                tr("RESET", "IDLE"))
        tap.act("IDLE",
                self.cregs.STATE.eq(TAPState.IDLE),
                tr("DRSELECT", "IDLE"))
        tap.act("DRSELECT",
                self.cregs.STATE.eq(TAPState.DRSELECT),
                tr("IRSELECT", "DRCAPTURE"))
        tap.act("DRCAPTURE",
                self.cregs.STATE.eq(TAPState.DRCAPTURE),
                tr("DREXIT1", "DRSHIFT"))
        tap.act("DRSHIFT",
                self.cregs.STATE.eq(TAPState.DRSHIFT),
                tr("DREXIT1", "DRSHIFT"))
        tap.act("DREXIT1",
                self.cregs.STATE.eq(TAPState.DREXIT1),
                tr("DRUPDATE", "DRPAUSE"))
        tap.act("DRPAUSE",
                self.cregs.STATE.eq(TAPState.DRPAUSE),
                tr("DREXIT2", "DRPAUSE"))
        tap.act("DREXIT2",
                self.cregs.STATE.eq(TAPState.DREXIT2),
                tr("DRUPDATE", "DRSHIFT"))
        tap.act("DRUPDATE",
                self.cregs.STATE.eq(TAPState.DRUPDATE),
                tr("DRSELECT", "IDLE"))
        tap.act("IRSELECT",
                self.cregs.STATE.eq(TAPState.IRSELECT),
                tr("RESET", "IRCAPTURE"))
        tap.act("IRCAPTURE",
                self.cregs.STATE.eq(TAPState.IRCAPTURE),
                tr("IREXIT1", "IRSHIFT"))
        tap.act("IRSHIFT",
                self.cregs.STATE.eq(TAPState.IRSHIFT),
                tr("IREXIT1", "IRSHIFT"))
        tap.act("IREXIT1",
                self.cregs.STATE.eq(TAPState.IREXIT1),
                tr("IRUPDATE", "IRPAUSE"))
        tap.act("IRPAUSE",
                self.cregs.STATE.eq(TAPState.IRPAUSE),
                tr("IREXIT2", "IRPAUSE"))
        tap.act("IREXIT2",
                self.cregs.STATE.eq(TAPState.IREXIT2),
                tr("IRUPDATE", "IRSHIFT"))
        tap.act("IRUPDATE",
                self.cregs.STATE.eq(TAPState.IRUPDATE),
                tr("DRSELECT", "IDLE"))


class ScanData(bitarray):
    def __int__(self):
        return int(self.to01()[::-1], 2)

    def hex(self):
        return hex(int(self))


class DR():
    def write(self, data):
        self.value = self.int2bitarray(self.length, data)

    def __init__(self, name, addr, length):
        self.name = name
        self.addr = addr
        self.length = length
        self.ir = bitarray()
        self.write(0)

    def int2bitarray(self, length, data):
        v = bitarray(length)
        v.setall(0)
        bl = bin(data)[2:]
        for i in range(min(len(bl), len(v))):
            v[-i-1] = int(bl[-i-1])
        return v

    def create_ir(self, length):
        self.ir = self.int2bitarray(length, self.addr)


class TAP():
    def __iadd__(self, dr):
        if isinstance(dr, DR):
            dr.create_ir(self.irlength)
            self.dr[dr.name] = dr
        return self

    def __init__(self, name, irlength):
        self.dr = dict()
        self.name = name
        self.irlength = irlength
        bypass = DR("BYPASS", 0xFFFFFFFF, 1)
        self += bypass
        self.selected_dr = bypass

    def select_dr(self, dr):
        self.selected_dr = self.dr[dr]

    def ir(self):
        return self.selected_dr.ir

    def drsize(self):
        return self.selected_dr.length

    def drvalue(self):
        return self.selected_dr.value

    def write_dr(self, data):
        return self.selected_dr.write(data)


class JTAG(BMIIModule):
    def __init__(self, trst_enable=False):
        self.trst_enable = trst_enable
        self.current_state = TAPState.RESET
        self.chain = []
        BMIIModule.__init__(self, JTAGIOModule())

    def update_state(self, state):
        assert int(self.drv.STATE) == state, "S: {}".format(int(self.drv.STATE))
        self.current_state = state

    def seq(self, path, state):
        for i in path:
            self.drv.TDR = i
        self.update_state(state)

    def shift(self, value):
        value.reverse()
        for i in range(len(value)):
            self.drv.TDR = value[i] << 1 | int(i == len(value) - 1)

    def read_rdr(self):
        value = bitarray()
        while True:
            rdr = int(self.drv.RDR)
            if not (rdr >> 1):
                return value
            value.append(rdr & 1)

    def irscan(self, value):
        self.update_state(TAPState.IDLE)
        self.seq([1, 1, 0, 0], TAPState.IRSHIFT)
        self.shift(value)
        self.update_state(TAPState.IREXIT1)
        self.seq([1, 0, 0, 0], TAPState.IDLE)
        self.read_rdr()

    def drscanreplace(self, size):
        ba = bitarray(size)
        self.update_state(TAPState.IDLE)
        self.seq([1, 0, 0], TAPState.DRSHIFT)
        self.shift(ba)
        self.update_state(TAPState.DREXIT1)
        self.seq([0], TAPState.DRPAUSE)
        value = self.read_rdr()
        self.seq([1, 0], TAPState.DRSHIFT)
        self.shift(value)
        self.update_state(TAPState.DREXIT1)
        self.seq([1, 0, 0, 0], TAPState.IDLE)
        self.read_rdr()
        return value

    def drscan(self, scanvalue):
        self.read_rdr()
        self.update_state(TAPState.IDLE)
        self.seq([1, 0, 0], TAPState.DRSHIFT)
        self.shift(scanvalue)
        self.update_state(TAPState.DREXIT1)
        self.seq([1, 0, 0, 0], TAPState.IDLE)
        return self.read_rdr()

    def reset(self):
        if self.trst_enable:
            self.drv.CTRL.TRST = 1
            self.drv.CTRL.TRST = 0
        else:
            for i in range(7):
                self.drv.TDR = 1
        self.update_state(TAPState.RESET)
        self.seq([0], TAPState.IDLE)

    def bypass_chain(self):
        for t in self.chain:
            t.select_dr("BYPASS")

    def add_tap(self, tap):
        self.chain.append(tap)

    def get_drsize(self):
        drsize = 0
        for t in self.chain:
            drsize += t.drsize()
        return drsize

    def irscanchain(self):
        ir = bitarray()
        for t in self.chain:
            ir.extend(t.ir())
        return self.irscan(ir)

    def drscanchain(self):
        dr = bitarray()
        for t in self.chain:
            dr.extend(t.drvalue())
        return self.drscan(dr)

    def extract_dr(self, tap, data):
        droffset = 0
        drsize = 0
        for t in self.chain:
            if t == tap:
                droffset = drsize
            drsize += t.drsize()
        sd = ScanData(data[droffset:droffset + tap.drsize()])
        sd.reverse()
        return sd

    def get_tap(self, tapname):
        tap = None
        for t in self.chain:
            if t.name == tapname:
                return t
        return None

    def irdrscan(self, tapname, dr, data=None):
        self.bypass_chain()
        tap = self.get_tap(tapname)
        assert tap is not None, "Cannot find TAP in chain: {}".format(tapname)
        tap.select_dr(dr)
        if data is not None:
            tap.write_dr(data)
        self.irscanchain()
        if data is None:
            rb = self.drscanreplace(self.get_drsize())
        else:
            rb = self.drscanchain()
        return self.extract_dr(tap, rb)

    def count_tap(self):
        self.bypass_chain()
        self.irscanchain()
        tapcount = 0
        for i in self.drscan(32 * bitarray("1")):
            if not i:
                tapcount += 1
            else:
                return tapcount
        assert True, "Cannot count TAPs in daisy chain"
