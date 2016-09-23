from bmii import *
from bmii.modules.spi import SPI
from bmii.modules.spidev import SerialFlash


def main():
    b = BMII.default()
    spi = SPI.default(b)
    sf = SerialFlash.default(b, spi, 0)

    b.cli()
    sf.read_id()
    sf.read_status()
    sf.dump_to_file("dump.bin")

if __name__ == "__main__":
    main()
