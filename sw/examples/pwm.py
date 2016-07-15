from bmii import *
from bmii.modules import pwm

if __name__ == "__main__":
    b = BMII()
    b.add_module(pwm.PWM())
    b.ioctl.program()
