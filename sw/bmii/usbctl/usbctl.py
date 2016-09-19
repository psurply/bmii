from bmii.usbctl.fw import Firmware
from bmii.usbctl.drv import Driver

class USBCtl():
    def __init__(self):
        self.fw = Firmware()
        self.drv = Driver()
