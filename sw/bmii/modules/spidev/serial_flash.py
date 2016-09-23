from bmii import *
from bmii.modules.spi import SPIDev
from enum import IntEnum


class SFCommand(IntEnum):
    WriteEnable     = 0x06
    WriteDisable    = 0x04
    ReadId1         = 0x9F
    ReadId2         = 0x9E
    ReadStatusReg   = 0x05
    WriteStatusReg  = 0x01
    ReadDataBytes   = 0x03
    PageProgram     = 0x02
    SectorErase     = 0xD8
    BulkErase       = 0xC7
    DeepPowerDown   = 0xB9
    ReleasePwrDown  = 0xAB


class SerialFlash(SPIDev):
    def __init__(self, spi, slave_id):
        SPIDev.__init__(self, spi, slave_id)

        self.spi.iomodule.cregs += CtrlReg("HOLD", CtrlRegDir.RDWR)
        self.spi.iomodule.iosignals += IOSignal("HOLD", IOSignalDir.OUT)
        self.spi.iomodule.comb += \
                self.spi.iomodule.iosignals.HOLD.eq(~self.spi.iomodule.cregs.HOLD)

    @classmethod
    def default(cls, bmii, spi, slave_id):
        spidev = cls(spi, slave_id)
        bmii.ioctl.sb.pins.IO26 += spi.iomodule.iosignals.HOLD
        return spidev

    def hold(self):
        self.spi.drv.HOLD = 1

    def resume(self):
        self.spi.drv.HOLD = 0

    def read_id(self):
        data = self.transceive(SFCommand.ReadId1, 0, 0, 0)
        logging.info("Manufacturer ID: 0x%x", data[1])
        logging.info("Device ID: 0x%x%x", data[2], data[3])
        return data[1:]

    def read_status(self):
        data = self.transceive(SFCommand.ReadStatusReg, 0)
        logging.info("Status: 0x%x", data[0])
        return data

    def dump(self, start_addr, size):
        logging.debug("Reading %d bytes at 0x%x ...", size, start_addr)
        return bytes(self.transceive(*([SFCommand.ReadDataBytes,
            (start_addr >> 16) & 0xFF,
            (start_addr >> 8) & 0xFF,
            start_addr & 0xFF] + [0] * size))[4:])

    def dump_to_file(self, path, bs=4096, nb=512):
        with open(path, 'wb+') as f:
            logging.debug("Dumping flash into %s", path)
            for b in range(nb):
                f.write(self.dump(b * bs, bs))
