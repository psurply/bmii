from bmii import *
from bmii.modules.logic_analyzer import *

def main():
    b = BMII()
    la = LogicAnalyser(4)
    b.add_module(la)

    sb = b.modules.southbridge.iomodule

    la.probe("IO1L", 8, sb.cregs.PINSCAN1L)
    la.probe("IO1H", 8, sb.cregs.PINSCAN1H)
    la.probe("IO2L", 8, sb.cregs.PINSCAN2L)
    la.probe("IO2H", 8, sb.cregs.PINSCAN2H)
    la.probe("IOMISC", 8, sb.cregs.PINSCANMISC)

    la.set_trigger(~sb.pins.SW.t.i)

    b.cli()

    la.reset()
    la.capture()
    la.show()

if __name__ == "__main__":
    main()
