from bmii import *

class SPIIOModule(IOModule):
    def __init__(self, nb_slaves=1, cpol=0, cpha=0):
        IOModule.__init__(self, "spi")

        self.nb_slaves = nb_slaves
        self.cpol = cpol
        self.cpha = cpha
 
        self.cregs += CtrlReg("SS", CtrlRegDir.RDWR)
        self.cregs += CtrlReg("TX", CtrlRegDir.WRONLY)
        self.cregs += CtrlReg("RX", CtrlRegDir.RDONLY)
        self.cregs += CtrlReg("STATUS", CtrlRegDir.RDONLY)

        self.iosignals += IOSignal("SCLK", IOSignalDir.OUT)
        self.iosignals += IOSignal("MOSI", IOSignalDir.OUT)
        self.iosignals += IOSignal("MISO", IOSignalDir.IN)

        for s in range(self.nb_slaves):
            ios = IOSignal("SS{}".format(s), IOSignalDir.OUT)
            self.iosignals += ios
            self.comb += ios.eq(~(self.cregs.SS == s))

        index = Signal(3)
        rx = Signal(8)
        self.comb += self.cregs.RX.eq(rx)

        fsm = FSM()
        self.submodules += fsm

        fsm.act("IDLE",
            self.cregs.STATUS.eq(1),
            self.iosignals.SCLK.eq(self.cpol),
            self.iosignals.MOSI.eq(0),
            NextValue(index, 7),
            If(self.cregs.TX.wr_pulse,
                NextState("DRIVE")).\
            Else(NextState("IDLE"))
        )

        fsm.act("DRIVE",
            self.cregs.STATUS.eq(2),
            self.iosignals.SCLK.eq(1- self.cpol if self.cpha else self.cpol),
            self.iosignals.MOSI.eq(self.cregs.TX >> index),
            NextState("CAPTURE")
        )

        fsm.act("CAPTURE",
            self.cregs.STATUS.eq(3),
            self.iosignals.SCLK.eq(self.cpol if self.cpha else 1 - self.cpol),
            self.iosignals.MOSI.eq(self.cregs.TX >> index),
            NextValue(rx[0], self.iosignals.MISO),
            NextValue(rx[1:8], self.cregs.RX[0:7]),
            NextValue(index, index - 1),
            If(index == 0, NextState("IDLE")).\
            Else(NextState("DRIVE"))
        )


class SPI(BMIIModule):
    def __init__(self, nb_slaves=1, cpol=0, cpha=0):
        BMIIModule.__init__(self, SPIIOModule(nb_slaves, cpol, cpha))

    def select_slave(self, slave):
        if slave >= self.iomodule.nb_slaves:
            raise ValueError("SPI Master module handles only {} slaves".\
                    format(self.iomodule.nb_slaves))
        logging.debug("SPI: selecting slave %d", slave)
        self.drv.SS = slave

    def unselect_slave(self):
        self.drv.SS = 0xFF

    def transceive_byte(self, data):
        self.drv.TX = data
        return int(self.drv.RX)

    def transceive(self, *data):
        return list([self.transceive_byte(x) for x in data])

    @classmethod
    def default(cls, bmii):
        spi = cls(2, cpol=0, cpha=0)
        bmii.add_module(spi)

        bmii.ioctl.sb.pins.IO20 += spi.iomodule.iosignals.SCLK
        bmii.ioctl.sb.pins.IO22 += spi.iomodule.iosignals.SS0
        bmii.ioctl.sb.pins.IO23 += spi.iomodule.iosignals.SS1
        bmii.ioctl.sb.pins.IO24 += spi.iomodule.iosignals.MOSI
        bmii.ioctl.sb.pins.IO25 += spi.iomodule.iosignals.MISO

        return spi


class SPIDev:
    def __init__(self, spi, slave_id):
        self.spi = spi
        self.slave_id = slave_id

    def transceive(self, *data):
        self.spi.select_slave(self.slave_id)
        rx = self.spi.transceive(*data)
        self.spi.unselect_slave()
        return rx

    @classmethod
    def default(cls, bmii, spi, slave_id):
        spidev = cls(spi, slave_id)
        return spidev


bmii_modules = [SPI]
