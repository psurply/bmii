import argparse
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
        for ts in self.test_suite:
            unittest.TextTestRunner().run(ts)


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
        self.subparser = self.parser.add_subparsers()

        def auto_int(nb):
            return int(nb, 0)

        build_parser = self.subparser.add_parser(
                name="build",
                description="Build/Program BMII design",
                help="build/program BMII design")
        build_parser.add_argument("buildtype",
                choices=["all", "ioctl", "usbctl", "eeprom"])
        build_parser.set_defaults(action="build")

        test_parser = self.subparser.add_parser(
                name="test",
                help="run IOModule unit tests")
        test_parser.add_argument("module", type=str)
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

    def add_module(self, module):
        self.modules += module
        self.ioctl += module.iomodule

    def run_tests(self):
        self.modules.run_tests()

    def build_all(self):
        self.ioctl.program()
        time.sleep(2)
        self.usbctl.fw.build()
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

    def cli(self):
        if len(sys.argv) == 1:
            self.parser.print_help()
            sys.exit(1)

        args = self.parser.parse_args()
        if args.action == "get":
            drv = self.modules.__getattribute__(args.module).drv
            cr = drv.__getattr__(args.reg)
            print(hex(int(cr)))
        elif args.action == "set":
            drv = self.modules.__getattribute__(args.module).drv
            cr = drv.__getattr__(args.reg)
            cr.write(args.value)
        elif args.action == "build":
            if args.buildtype == "all":
                self.build_all()
            elif args.buildtype == "ioctl":
                self.ioctl.program()
            elif args.buildtype == "usbctl":
                self.usbctl.fw.build()
                self.usbctl.fw.load()
            elif args.buildtype == "eeprom":
                self.usbctl.fw.build()
                self.usbctl.fw.flash()
        elif args.action == "test":
            self.modules.__getattribute__(args.module).run_tests()
        elif args.action == "list":
            self.list_modules()

        self.args = args


if __name__ == "__main__":
    bmii = BMII()
    bmii.run_tests()
