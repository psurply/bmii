from bmii import *

if __name__ == "__main__":
    b = BMII()

    b.usbctl.drv.attach()
    b.usbctl.drv.select_creg(b.ioctl.sb.cregs.PINMUXMISC)
    b.usbctl.drv.write(3)
    b.usbctl.drv.select_creg(b.ioctl.sb.cregs.PINSCANMISC)
    print(b.usbctl.drv.read(6))
