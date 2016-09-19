from bmii.usbctl.fw import BMIIFirmware, UBFirmware
from bmii.usbctl.drv import Driver

class USBCtl():
    def __init__(self):
        self.fw = BMIIFirmware()
        self.ubfw = UBFirmware()
        self.drv = Driver()
