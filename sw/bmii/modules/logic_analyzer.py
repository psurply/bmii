from enum import IntEnum
from bmii import *
from migen.genlib.fifo import *
import logging
import time
import tempfile

class Probe:
    def __init__(self, name, nbits, signal):
        logging.debug("Probing %s", name)
        self.name = name
        self.signal = signal
        self.nbits = nbits
        self.values = []

    def retrieve_values(self, drv, nb):
        self.values = [int(drv.get_creg(self.name)) for i in range(nb)]


class LogicAnalyserState(IntEnum):
    WAITING     = 0
    CAPTURING   = 1
    DONE        = 2


class LogicAnalyserIOModule(IOModule):
    def __init__(self, memsize):
        IOModule.__init__(self, "logic_analyzer")

        self.cregs += CtrlReg("STATUS", CtrlRegDir.RDONLY)
        self.cregs += CtrlReg("START", CtrlRegDir.WRONLY)

        self.trigger = Signal()
        self.fifo_full = Signal()
        self.memsize = memsize

        fsm = FSM()
        self.submodules += fsm

        fsm.act("WAITING",
                self.cregs.STATUS.eq(LogicAnalyserState.WAITING),
                If(self.trigger, NextState("CAPTURING")).
                Else(NextState("WAITING")))

        fsm.act("CAPTURING",
                self.cregs.STATUS.eq(LogicAnalyserState.CAPTURING),
                If(self.fifo_full, NextState("DONE")).
                Else(NextState("CAPTURING")))

        fsm.act("DONE",
                self.cregs.STATUS.eq(LogicAnalyserState.DONE),
                If(self.cregs.START.wr_pulse, NextState("WAITING")).
                Else(NextState("DONE")))

    def probe(self, probe):
        fifo = SyncFIFO(probe.nbits, self.memsize)

        cr = CtrlReg(probe.name, CtrlRegDir.RDONLY)

        self.comb += cr.eq(fifo.dout)
        self.comb += self.fifo_full.eq(~fifo.writable)
        self.comb += fifo.re.eq(cr.rd_pulse)
        self.comb += fifo.we.eq(self.cregs.STATUS == LogicAnalyserState.CAPTURING)
        self.comb += fifo.din.eq(probe.signal)

        self.cregs += cr
        self.submodules += fifo


class LogicAnalyser(BMIIModule):
    def __init__(self, memsize):
        self.memsize = memsize
        BMIIModule.__init__(self, LogicAnalyserIOModule(memsize))
        self.probes = {}

    def probe(self, name, nbits, signal):
        probe = Probe(name, nbits, signal)
        self.probes[name] =  probe
        self.iomodule.probe(probe)

    def set_trigger(self, signal):
        self.iomodule.comb += self.iomodule.trigger.eq(signal)

    def retrieve_values(self):
        for p in self.probes.values():
            p.retrieve_values(self.drv, self.memsize)

    def reset(self):
        self.retrieve_values()
        self.drv.START = 0

    def capture(self):
        self.reset()

        if int(self.drv.STATUS) == LogicAnalyserState.WAITING:
            logging.info("Waiting for trigger...")
            while int(self.drv.STATUS) == LogicAnalyserState.WAITING:
                pass

        if int(self.drv.STATUS) == LogicAnalyserState.CAPTURING:
            logging.info("Capturing...")

        while int(self.drv.STATUS) != LogicAnalyserState.DONE:
            pass

        self.retrieve_values()
        logging.info("Values captured")

    def to_vcd(self, f):
        f.write("$date {} $end\n".format(time.asctime()))
        f.write("$version {} $end\n".format("0.1"))
        f.write("$timescale {} $end\n".format("1 s"))
        f.write("$scope module bmii $end\n")
        for p in self.probes.values():
            f.write("$var wire {} {} {} $end\n".format(p.nbits,
                p.name, p.name))
        f.write("$upscope $end\n")

        for i in range(self.memsize):
            f.write("#{}\n".format(i + 1))
            for p in self.probes.values():
                f.write("b{} {}\n".format(bin(p.values[i])[2:], p.name))
        f.write("#{}\n".format(self.memsize + 1))

    def show(self):
        f = tempfile.NamedTemporaryFile(delete=False, mode="w+", suffix=".vcd")
        self.to_vcd(f)
        f.close()
        subprocess.run(["gtkwave", f.name], check=True)
