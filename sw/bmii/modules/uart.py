from bmii import *
from migen.genlib.fifo import *
from migen.genlib.fsm import *

import math

class BaudRateGenerator(Module):
    def __init__(self, input_freq, baudrate):
        self.clock_domains.cd_clk = ClockDomain()
        self.output = Signal()
        self.comb += self.cd_clk.clk.eq(self.output)

        max_value = int(input_freq / (2 * baudrate) - 1)
        cnt = Signal(math.ceil(math.log2(max_value)))

        self.sync += \
                If(cnt >= max_value,
                    self.output.eq(~self.output),
                    cnt.eq(0)).\
                Else(cnt.eq(cnt + 1))


class ParityType(Enum):
    Even    = 1
    Odd     = 2


class ParityGenerator(Module):
    def __init__(self, parity_type):
        self.input = Signal()
        self.parity = Signal()
        self.en = Signal()

        even = Signal()
        self.sync += \
            If(~self.en,
                even.eq(0)).\
            Elif(self.input,
                even.eq(~even))

        if parity_type == ParityType.Odd:
            self.comb += self.parity.eq(~even)
        else:
            self.comb += self.parity.eq(even)


class UARTUnit(Module):
    def __init__(self, baudrate, data_width, parity_bit, stop_bits, skip_start=False):
        self.data_width = data_width
        self.parity_bit = parity_bit

        self.pg = ParityGenerator(parity_bit)
        self.submodules += ClockDomainsRenamer("brg_clk")(self.pg)

        cnt = Signal(4)

        fsm = FSM()
        self.submodules += ClockDomainsRenamer("brg_clk")(fsm)

        fsm.act("IDLE",
                *self.idle(),
                If(self.start_condition(),
                    *self.enter_start(),
                    NextValue(cnt, 1),
                    NextState("DATA" if skip_start else "START")).\
                Else(NextState("IDLE")))

        fsm.act("START",
                *self.start(),
                NextState("DATA"))

        fsm.act("DATA",
                *self.shift_data(),
                NextValue(cnt, cnt + 1),
                If(cnt >= data_width,
                    NextValue(cnt, 1),
                    *(self.enter_stop() if not parity_bit else []),
                    NextState("PARITY" if parity_bit else "STOP")).\
                Else(NextState("DATA")))

        fsm.act("PARITY",
                *self.parity(),
                NextState("STOP"))

        fsm.act("STOP",
                *self.stop(),
                NextValue(cnt, cnt + 1),
                If(cnt >= stop_bits,
                    NextState("IDLE")).\
                Else(NextState("STOP")))


class TXUnit(UARTUnit):
    def __init__(self, baudrate, data_width, parity_bit, stop_bits, fifo_size=2):
        self.tx = Signal()
        self.thr = Signal(data_width)

        self.fifo = ClockDomainsRenamer({"write": "sys", "read": "brg_clk"})\
                (AsyncFIFO(data_width, fifo_size))
        self.submodules += self.fifo

        super(TXUnit, self).__init__(baudrate, data_width, parity_bit, stop_bits)

        if parity_bit:
            self.comb += self.pg.input.eq(self.tx)

    def idle(self):
        return [self.tx.eq(1)]

    def start_condition(self):
        return self.fifo.readable

    def enter_start(self):
        return [
            NextValue(self.thr, self.fifo.dout),
            NextValue(self.fifo.re, 1),
        ]

    def start(self):
        return [
            self.tx.eq(0),
            NextValue(self.fifo.re, 0),
        ]

    def shift_data(self):
        return [
            self.pg.en.eq(1),
            self.tx.eq(self.thr[0]),
            NextValue(self.thr, self.thr >> 1)
        ]

    def enter_stop(self):
        return []

    def parity(self):
        return [
            self.tx.eq(self.pg.parity)
        ]

    def stop(self):
        return [self.tx.eq(1)]


class RXUnit(UARTUnit):
    def __init__(self, baudrate, data_width, parity_bit, stop_bits,
            fifo_size=4, triple_sampling=False):
        self.rx = Signal()
        self.rhr = Signal(data_width)

        self.fifo = ClockDomainsRenamer({"write": "brg_clk", "read": "sys"})\
            (AsyncFIFO(data_width, fifo_size))
        self.submodules += self.fifo

        self.data = Signal()

        super(RXUnit, self).__init__(baudrate, data_width, parity_bit,
                stop_bits, skip_start=True)

        self.comb += self.fifo.din.eq(self.rhr)

        if triple_sampling:
            self.submodules.sampler = BaudRateGenerator(48000000, baudrate * 4)

            samples = Signal(3)
            self.sync.rx_clk += samples.eq((samples << 1) | self.rx)

            self.comb += self.data.eq(
                    (samples[0] & samples[1]) |
                    (samples[0] & samples[2]) |
                    (samples[1] & samples[2]))
        else:
            self.comb += self.data.eq(self.rx)

        if parity_bit:
            self.comb += self.pg.input.eq(self.data)

    def idle(self):
        return []

    def start_condition(self):
        return ~self.data

    def enter_start(self):
        return [
            NextValue(self.rhr, 0),
        ]

    def start(self):
        return []

    def shift_data(self):
        return [
            self.pg.en.eq(1),
            NextValue(self.rhr, (self.rhr >> 1)
                | (self.data << (self.data_width - 1)))
        ]

    def enter_stop(self):
        return [
            NextValue(self.fifo.we, 1),
        ]

    def parity(self):
        return [
            If(self.pg.parity == self.data,
                *self.enter_stop())
        ]

    def stop(self):
        return [
            NextValue(self.fifo.we, 0)
        ]


class UARTIOModule(IOModule):
    def __init__(self, baudrate, data_width, parity_bit, stop_bits):
        IOModule.__init__(self, "uart")

        self.iosignals += IOSignal("TX", IOSignalDir.OUT)
        self.iosignals += IOSignal("RX", IOSignalDir.IN)

        self.cregs += CtrlReg("THR", CtrlRegDir.RDWR)
        self.cregs += CtrlReg("RHR", CtrlRegDir.RDONLY)
        self.cregs += CtrlReg("STATUS", CtrlRegDir.RDONLY)

        # Baudrate Generator
        self.submodules.brg = BaudRateGenerator(48000000, baudrate)

        # TX
        tx = TXUnit(baudrate, data_width, parity_bit, stop_bits)
        self.submodules.tx = tx

        self.comb += tx.fifo.we.eq(self.cregs.THR.wr_pulse)
        self.comb += tx.fifo.din.eq(self.cregs.THR)
        self.comb += self.cregs.STATUS[1].eq(tx.fifo.writable)
        self.comb += self.iosignals.TX.eq(tx.tx)

        # RX
        rx = RXUnit(baudrate, data_width, parity_bit, stop_bits, triple_sampling=True)
        self.submodules.rx = rx

        self.comb += rx.rx.eq(self.iosignals.RX)
        self.comb += self.cregs.RHR.eq(rx.fifo.dout)
        self.comb += self.cregs.STATUS[0].eq(rx.fifo.readable)
        self.comb += rx.fifo.re.eq(self.cregs.RHR.rd_pulse)


class UART(BMIIModule):
    def __init__(self, baudrate=115200, data_width=8, parity_bit=None, stop_bits=1):
        BMIIModule.__init__(self,
                UARTIOModule(baudrate, data_width, parity_bit, stop_bits))

    @classmethod
    def default(cls, bmii):
        uart = cls()
        bmii.add_module(uart)

        bmii.ioctl.sb.pins.IO10 += uart.iomodule.iosignals.TX
        bmii.ioctl.sb.pins.IO11 += uart.iomodule.iosignals.RX

        return uart

    def transmit_char(self, data):
        while not int(self.drv.STATUS) >> 1:
            pass
        self.drv.THR = data

    def transmit(self, s):
        for i in s:
            self.transmit_char(i)

    def echo(self):
        if int(self.drv.STATUS) & 1:
            self.transmit_char(int(self.drv.RHR))


bmii_modules = [UART]


if __name__ == "__main__":
    bmii = BMII().default()
    uart = UART.default(bmii)

    bmii.usbctl.drv.set_cpu_speed(CPUSpd.CLK_48M)
    while True:
        uart.echo()
