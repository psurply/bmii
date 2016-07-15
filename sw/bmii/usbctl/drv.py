from enum import IntEnum
import usb


class bmRequestType(IntEnum):
    VENDOR_WR   = 0x40


class bRequest(IntEnum):
    SELECT_CREG = 0xF0
    LOAD_RDFIFO = 0xF1


class Driver():
    def __init__(self):
        self.dev = None

    def attach(self):
        if self.dev != None:
            return

        self.dev = usb.core.find(idVendor=0xffff, idProduct=0xebfe)
        if self.dev == None:
            raise IOError('Device not found')

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
