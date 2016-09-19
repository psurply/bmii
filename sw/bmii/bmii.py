import argparse
import importlib
import logging
import sys
import time
import unittest

from bmii.ioctl import IOCtl
from bmii.usbctl import USBCtl

from bmii.test import *



class DrvCReg():
    def __init__(self, usbctl, creg):
        object.__setattr__(self, "usbctl", usbctl)
        object.__setattr__(self, "creg", creg)

    def __getattr__(self, field):
        field = getattr(self.creg, field)
        value = self.read(1)
        return (value >> field.offset) & ((1 << field.size) - 1)

    def __setattr__(self, field, value):
        field = getattr(self.creg, field)
        v = self.read(1)
        mask = ~(((1 << field.size) - 1) << field.offset)
        self.write((v & mask) | ((value & ((1 << field.size) - 1)) << field.offset))

    def select(self):
        self.usbctl.drv.select_creg(self.creg)

    def read(self, size):
        self.select()
        return self.usbctl.drv.read(size)

    def write(self, value):
        self.select()
        self.usbctl.drv.write(value)

    def __int__(self):
        return self.read(1)


class Driver():
    def __init__(self, bmii_module):
        object.__setattr__(self, "bmii_module", bmii_module)

    def __getattr__(self, creg_name):
        return DrvCReg(self.bmii_module.usbctl,
                getattr(self.bmii_module.iomodule.cregs, creg_name))

    def __setattr__(self, creg_name, value):
        creg = DrvCReg(self.bmii_module.usbctl,
                getattr(self.bmii_module.iomodule.cregs, creg_name))
        creg.write(value)

    def get_creg(self, creg_name):
        try:
            return self.__getattr__(creg_name)
        except AttributeError:
            logging.error("Cannot find control register %s", creg_name)
            sys.exit(2)


class BMIIModule():
    def __init__(self, iomodule, *testcases):
        self.iomodule = iomodule
        self.usbctl = None
        self.drv = Driver(self)
        self.test_suite = \
                map((lambda x : \
                unittest.defaultTestLoader.loadTestsFromTestCase(x)),
                testcases)

    def run_tests(self):
        logging.info("Simulating %s", self.iomodule.name)
        for ts in self.test_suite:
            unittest.TextTestRunner().run(ts)

    @classmethod
    def default(cls, bmii):
        m = cls()
        bmii.add_module(m)

        return m


class BMIIModules():
    def __init__(self, usbctl):
        self.usbctl = usbctl

    def __iadd__(self, module):
        module.usbctl = self.usbctl
        object.__setattr__(self, module.iomodule.name, module)
        return self

    def run_tests(self):
        for i in dir(self):
            attr = object.__getattribute__(self, i)
            if isinstance(attr, BMIIModule):
                attr.run_tests()

    def get_module(self, module):
        try:
            m = self.__getattribute__(module)
            if not isinstance(m, BMIIModule):
                raise AttributeError
            return m
        except AttributeError:
            logging.error("Cannot find module %s", module)
            sys.exit(2)

class BMII():
    def __init__(self):
        self.usbctl = USBCtl()
        self.ioctl = IOCtl()

        self.modules = BMIIModules(self.usbctl)

        self.modules += BMIIModule(self.ioctl.nb,
                test_nb.NorthBridgeUSBCTLCase,
                test_nb.NorthBridgeIOModuleCase)
        self.modules += BMIIModule(self.ioctl.sb, test_sb.SouthBridgeCase)

        self.parser = argparse.ArgumentParser(description="BMII CLI")
        self.parser.add_argument("-m", action="append",
                help="Add module to BMII", default=[])
        self.parser.set_defaults(action="")
        self.subparser = self.parser.add_subparsers()

        def auto_int(nb):
            return int(nb, 0)

        detect_parser = self.subparser.add_parser(
                name="detect",
                help="Detect plugged BMII")
        detect_parser.set_defaults(action="detect")

        build_parser = self.subparser.add_parser(
                name="build",
                description="Build BMII design/firmware",
                help="build/program BMII design")
        build_parser.add_argument("buildtype",
                choices=["all", "ioctl", "usbctl"])
        build_parser.set_defaults(action="build")

        program_parser = self.subparser.add_parser(
                name="program",
                description="Program BMII",
                help="Program BMII")
        program_parser.set_defaults(action="program")

        simulate_parser = self.subparser.add_parser(
                name="simulate",
                help="simulate IOModule unit tests")
        simulate_parser.add_argument("module", type=str)
        simulate_parser.set_defaults(action="simulate")

        test_parser = self.subparser.add_parser(
                name="test",
                help="test BMII device")
        test_parser.set_defaults(action="test")

        set_parser = self.subparser.add_parser(
                name="set",
                help="write IOModule control register")
        set_parser.add_argument("module", type=str)
        set_parser.add_argument("reg", type=str)
        set_parser.add_argument("value", type=auto_int)
        set_parser.set_defaults(action="set")

        get_parser = self.subparser.add_parser(
                name="get",
                help="read IOModule control register")
        get_parser.add_argument("module", type=str)
        get_parser.add_argument("reg", type=str)
        get_parser.set_defaults(action="get")

        list_parser = self.subparser.add_parser(
                name="list",
                help="list IOModules")
        list_parser.set_defaults(action="list")

        pinout_parser = self.subparser.add_parser(
                name="pinout",
                help="display BMII pinout")
        pinout_parser.set_defaults(action="pinout")

        eval_parser = self.subparser.add_parser(
                name="eval",
                help="evaluate python expression")
        eval_parser.add_argument("cmd", type=str)
        eval_parser.set_defaults(action="eval")

    def add_module(self, module):
        logging.debug("Adding module: %s", module.iomodule.name)
        self.modules += module
        self.ioctl += module.iomodule

    def run_tests(self):
        self.modules.run_tests()

    def build_all(self):
        self.ioctl.build()
        self.usbctl.fw.build()

    def program(self):
        logging.info("[STAGE 1] Loading CPLD programmer firmware")
        logging.info("[STAGE 2] Loading CPLD design")
        self.ioctl.program()
        logging.info("[STAGE 3] Flashing EEPROM")
        self.usbctl.fw.build()
        time.sleep(2)
        self.usbctl.fw.flash()
        logging.info("[STAGE 4] Loading USB firmware")
        self.usbctl.fw.load()

    def list_modules(self):
        def getmaddr(x):
            if isinstance(x, BMIIModule):
                return x.iomodule.addr
            return -1;

        def getraddr(x):
            if isinstance(x, CtrlReg):
                return x.addr
            return -1

        for m in sorted(self.modules.__dict__.values(), key=getmaddr):
            if isinstance(m, BMIIModule):
                print("{}: {}".format(hex(m.iomodule.addr), m.iomodule.name))
                for r in sorted(m.iomodule.cregs.__dict__.values(), key=getraddr):
                    if isinstance(r, CtrlReg):
                        print("\t{}: {} ({})".format(hex(r.addr), r.name,
                                        str(r.direction)))

    def pinout(self):
        return self.ioctl.sb.pinout()

    def test(self):
        logging.debug("Testing device...")
        self.usbctl.drv.attach()

        logging.debug("Testing Northbridge...")
        for i in range(256):
            self.modules.northbridge.drv.SCRATCH = i
            v = int(self.modules.northbridge.drv.SCRATCH) 
            if v != i:
                logging.error("SCRATCH register: wrote %x, read %x", i, v)

        logging.info("Device fully tested")

    def cli(self):
        if len(sys.argv) == 1:
            self.parser.print_help()
            sys.exit(1)

        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG,
                format='[%(levelname)s] %(message)s')

        logging.addLevelName(logging.DEBUG,   "\033[1;34mDEBUG\033[1;0m")
        logging.addLevelName(logging.INFO,    "\033[1;32mINFO\033[1;0m")
        logging.addLevelName(logging.WARNING, "\033[1;33mWARN\033[1;0m")
        logging.addLevelName(logging.ERROR,   "\033[1;31mERROR\033[1;0m")

        args = self.parser.parse_args()

        for m in args.m:
            spec = importlib.util.spec_from_file_location("bmii.modules", m)
            try:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
            except AttributeError:
                raise IOError("Cannot load module {}".format(m))

            for i in mod.bmii_modules:
                i.default(self)

        if args.action == "get":
            drv = self.modules.__getattribute__(args.module).drv
            cr = drv.get_creg(args.reg)
            print(hex(int(cr)))
        elif args.action == "set":
            drv = self.modules.__getattribute__(args.module).drv
            cr = drv.__getattr__(args.reg)
            cr.write(args.value)
        elif args.action == "detect":
            try:
                self.usbctl.drv.attach()
            except IOError as e:
                logging.error("%s", e)
        elif args.action == "build":
            if args.buildtype == "all":
                self.build_all()
            elif args.buildtype == "ioctl":
                self.ioctl.build()
            elif args.buildtype == "usbctl":
                self.usbctl.fw.build()
        elif args.action == "program":
            self.program()
        elif args.action == "test":
            self.test()
        elif args.action == "simulate":
            self.modules.get_module(args.module).run_tests()
        elif args.action == "list":
            self.list_modules()
        elif args.action == "pinout":
            print(self.pinout())
        elif args.action == "eval":
            print(eval(args.cmd))

        self.args = args

    @classmethod
    def default(cls):
        from bmii.modules.fade import Fade

        b = cls()
        fade = Fade()
        b.add_module(fade)

        b.ioctl.sb.pins.LED0 += fade.iomodule.iosignals.NOUT
        b.ioctl.sb.pins.LED1 += fade.iomodule.iosignals.OUT

        return b


if __name__ == "__main__":
    bmii = BMII()
    bmii.run_tests()
