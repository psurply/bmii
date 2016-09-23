from bmii import *
from bmii.modules.logic_analyzer import *
from bmii.modules.spi import *

def main():
    b = BMII()
    spi = SPI.default(b)

    la = LogicAnalyser(16)
    b.add_module(la)

    la.probe("SCLK", 1, spi.iomodule.iosignals.SCLK)
    la.probe("SS0", 1, spi.iomodule.iosignals.SS0)
    la.probe("MOSI", 1, spi.iomodule.iosignals.MOSI)

    la.set_trigger(spi.iomodule.cregs.TX.wr_pulse)

    la.reset()
    spi.select_slave(0)

    b.cli()

    la.capture()
    la.show()

if __name__ == "__main__":
    main()
