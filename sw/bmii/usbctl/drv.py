from enum import IntEnum
import logging
import usb


class bmRequestType(IntEnum):
    VENDOR_WR   = 0x40


class bRequest(IntEnum):
    SELECT_CREG = 0xF0
    LOAD_RDFIFO = 0xF1


class Driver():
    def __init__(self):
        self.dev = None

    def detect(self):
        dev = usb.core.find(idVendor=0xffff, idProduct=0xebfe)
        if dev is None:
            raise IOError("Device not found")
        else:
            logging.info("Found device (%03d:%03d)", dev.bus, dev.address)
        return dev

    def attach(self):
        if self.dev is not None:
            return

        self.dev = self.detect()

        self.dev.set_configuration()
        cfg = self.dev.get_active_configuration()
        intf = cfg[(0, 0)]

        self.ep_wr = usb.util.find_descriptor(
                intf,
                custom_match = \
                        lambda e: \
                        usb.util.endpoint_direction(e.bEndpointAddress) == \
                        usb.util.ENDPOINT_OUT)

        self.ep_rd = usb.util.find_descriptor(
                intf,
                custom_match = \
                        lambda e: \
                        usb.util.endpoint_direction(e.bEndpointAddress) == \
                        usb.util.ENDPOINT_IN)

        assert self.ep_wr is not None
        assert self.ep_rd is not None

        self.check_idcode()

    def select_creg(self, ctrlreg):
        self.attach()
        value = (ctrlreg.addr << 3) | (ctrlreg.iomodule.addr)
        self.dev.ctrl_transfer(bmRequestType.VENDOR_WR,
                bRequest.SELECT_CREG, value)

    def load_rdfifo(self, size):
        self.attach()
        self.dev.ctrl_transfer(bmRequestType.VENDOR_WR,
                bRequest.LOAD_RDFIFO, size)

    def write(self, data):
        self.attach()
        if isinstance(data, int):
            data = [data]
        self.ep_wr.write(data)

    def read(self, size):
        self.attach()
        self.load_rdfifo(size)
        if size == 1:
            return self.ep_rd.read(size)[0]
        return self.ep_rd.read(size)

    def check_idcode(self):
        self.dev.ctrl_transfer(bmRequestType.VENDOR_WR,
                bRequest.SELECT_CREG, 0)
        idcode = self.read(1)
        logging.info("IDCODE: %X", idcode)
        if (idcode != 0xA5):
            logging.warning("Unknown IDCODE")
