from migen import *
from migen.genlib.io import CRG
import logging
import os
import subprocess
import sys

from bmii.ioctl.iomodule import *
from bmii.ioctl.platform import BMIIPlatform
from bmii.ioctl.north_bridge import NorthBridge
from bmii.ioctl.south_bridge import SouthBridge


class IOModules():
    def __init__(self, bridges):
        self.modules_nb = 0
        self.bridges = bridges

    def __iadd__(self, iomodule):
        iomodule.set_addr(self.modules_nb)
        object.__setattr__(self, iomodule.name, iomodule)
        for bridge in self.bridges:
            bridge.connect(iomodule)
        self.modules_nb += 1
        return self


class IOCtl(Module):
    def __init__(self, shrink=False):
        self.nb = NorthBridge("northbridge")
        self.sb = SouthBridge("southbridge", shadowed=shrink)

        self.iomodules = IOModules([self.nb])
        self.iomodules += self.nb
        self.iomodules += self.sb

        self.submodules.nb = self.nb
        self.submodules.sb = self.sb

    def __iadd__(self, iomodule):
        self.iomodules += iomodule
        self.submodules.__setattr__(iomodule.name, iomodule)
        return self

    def build(self):
        logging.debug("Building IO controller design...")
        plat = BMIIPlatform()
        self.nb.connect_platform(plat)
        self.sb.connect_platform(plat)

        dummy = Signal()
        self.comb += dummy.eq(plat.request("clk0")
                    | plat.request("clk1")
                    | plat.request("clk3"))

        self.submodules.crg = CRG(plat.request("clk2"),
                ~plat.request("reset0") | ~plat.request("reset1"))

        plat.build(self)
        logging.info("IO controller design built")
        return plat

    def detect(self):
        logging.debug("Scanning IO controller...")
        with subprocess.Popen(["jtagconfig", "--enum"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE) as proc:
            proc.wait()
            msg = proc.stdout.read().split(b"\n") + proc.stderr.read().split(b"\n")
            msg = filter(lambda x: len(x) > 0, msg)
            msg = [str(x)[2:-1] for x in msg]

            if proc.returncode != 0:
                logging.error("%s", msg[0])
                raise IOError(msg[0])
            else:
                info = msg[0].strip().split(" ")
                logging.info("Probe: %s", " ".join(info[1:]))
                if msg[1].strip().split(" ")[0] == "Unable":
                    logging.error("%s", msg[1])
                    raise IOError(msg[1])
                else:
                    info = msg[1].strip().split(" ")
                    logging.info("Model: %s", info[3])
                    logging.info("IDCODE: %s", info[0])

    def program(self):
        try:
            self.detect()
            logging.debug("Programming IO controller... ")

            if not os.path.exists(os.path.join("build", "top.pof")):
                logging.warn("Cannot find IO Controller design file")
                logging.warn("Trying to build it")
                self.build()
            subprocess.run(["quartus_pgm", "-m", "jtag",
                   "-o", "p;build/top.pof"])
            logging.info("IO Controller configured")
        except:
            logging.error("Cannot configure IO controller")
            sys.exit(2)
