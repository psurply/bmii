from bmii import *

if __name__ == "__main__":
    b = BMII()
    b.usbctl.fw.build()
    b.usbctl.fw.load()
