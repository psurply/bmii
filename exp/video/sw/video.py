from bmii import *
from migen.genlib.fifo import SyncFIFO


class VideoConfig(Enum):
    CFG1 = 0
    CFG2 = 1


class VideoIOModule(IOModule):
    @property
    def display_logic(self):
        raise NotImplementedError

    @property
    def vram_drive_addr_logic(self):
        raise NotImplementedError

    @property
    def vram_read_logic(self):
        raise NotImplementedError

    def __init__(self, config):
        IOModule.__init__(self, "Video")

        VRAM_DATA_SIZE = 8
        if config == VideoConfig.CFG1:
            VRAM_ADDR_SIZE = 14
        else:
            VRAM_ADDR_SIZE = 16

        # Control Registers
        self.cregs += CtrlReg("ADDRH", CtrlRegDir.WRONLY)
        self.cregs += CtrlReg("ADDRL", CtrlRegDir.WRONLY)
        self.cregs += CtrlReg("DATA", CtrlRegDir.WRONLY)

        # IO definition

        ## VGA Signals
        self.iosignals += IOSignal("VGA_VS", IOSignalDir.OUT)
        self.iosignals += IOSignal("VGA_HS", IOSignalDir.OUT)

        self.iosignals += IOSignal("VGA_RED0", IOSignalDir.OUT)
        self.iosignals += IOSignal("VGA_RED1", IOSignalDir.OUT)

        self.iosignals += IOSignal("VGA_GREEN0", IOSignalDir.OUT)
        self.iosignals += IOSignal("VGA_GREEN1", IOSignalDir.OUT)

        self.iosignals += IOSignal("VGA_BLUE0", IOSignalDir.OUT)
        self.iosignals += IOSignal("VGA_BLUE1", IOSignalDir.OUT)

        # VRAM Signals
        for i in range(VRAM_ADDR_SIZE):
            self.iosignals += IOSignal("VRAM_ADDR{}".format(i), IOSignalDir.OUT)

        for i in range(VRAM_DATA_SIZE):
            self.iosignals += IOSignal("VRAM_DOUT{}".format(i), IOSignalDir.OUT)
            self.iosignals += IOSignal("VRAM_DIN{}".format(i), IOSignalDir.IN)
            self.iosignals += IOSignal("VRAM_DDIR{}".format(i), IOSignalDir.DIRCTL)

        self.iosignals += IOSignal("VRAM_WR", IOSignalDir.OUT)
        self.iosignals += IOSignal("VRAM_CE", IOSignalDir.OUT)

        # Internal signals

        ## Video signals
        self.px = Signal(6)
        self.display_enabled = Signal()
        self.h_display = Signal()
        self.v_display = Signal()
        self.next_h_counter = Signal(10)
        self.h_counter = Signal(10)
        self.v_counter = Signal(10)

        ## VRAM Signals
        self.vram_din = Signal(VRAM_DATA_SIZE)
        self.vram_addr = Signal(VRAM_ADDR_SIZE)

        # Logic

        ## VRAM management

        drive_pxl = Signal()
        drive_vram_d = Signal()
        vram_wr = Signal()
        vram_dout = Signal(VRAM_DATA_SIZE)

        self.comb += self.iosignals.VRAM_WR.eq(vram_wr)
        self.comb += self.iosignals.VRAM_CE.eq(0)
        for i in range(VRAM_ADDR_SIZE):
            self.comb += getattr(self.iosignals, "VRAM_ADDR{}".format(i)).eq(self.vram_addr[i])
        for i in range(VRAM_DATA_SIZE):
            self.comb += getattr(self.iosignals, "VRAM_DOUT{}".format(i)).eq(vram_dout[i])
            self.comb += self.vram_din[i].eq(getattr(self.iosignals, "VRAM_DIN{}".format(i)))
            self.comb += getattr(self.iosignals, "VRAM_DDIR{}".format(i)).eq(drive_vram_d)

        vram_write_fifo = SyncFIFO(VRAM_DATA_SIZE, 4)
        self.comb += vram_write_fifo.we.eq(self.cregs.DATA.wr_pulse)
        self.comb += vram_write_fifo.din.eq(self.cregs.DATA)

        self.vram_cursor = Signal(VRAM_ADDR_SIZE)
        self.sync += \
                If(self.cregs.ADDRL.wr_pulse,
                    self.vram_cursor.eq(self.cregs.ADDRH << 8 | self.cregs.ADDRL)).\
                Elif(~vram_wr,
                    self.vram_cursor.eq(self.vram_cursor + 1))

        fsm_vram = FSM()

        fsm_vram.act("VRAM_WRITE",
                NextValue(drive_pxl, 0),
                If(vram_write_fifo.readable,
                    NextValue(vram_dout, vram_write_fifo.dout),
                    NextValue(drive_vram_d, 1),
                    NextValue(vram_wr, 0),
                    NextValue(self.vram_addr, self.vram_cursor),
                    NextValue(vram_write_fifo.re, 1),
                    NextState("VRAM_WRITE_LATCH")).\
                Else(
                    NextValue(drive_vram_d, 0),
                    NextValue(vram_wr, 1),
                    NextState("VRAM_READ"),
                    *self.vram_drive_addr_logic))

        fsm_vram.act("VRAM_WRITE_LATCH",
                NextValue(drive_pxl, 1),
                NextValue(vram_wr, 1),
                NextValue(vram_write_fifo.re, 0),
                NextState("VRAM_WRITE"))

        fsm_vram.act("VRAM_READ",
                NextValue(drive_pxl, 1),
                NextState("VRAM_WRITE"),
                *self.vram_read_logic)

        self.submodules += vram_write_fifo
        self.submodules += fsm_vram

        ## Video signals generator

        self.clock_domains.cd_pxl = ClockDomain(reset_less=True)
        self.comb += self.cd_pxl.clk.eq(drive_pxl)
        self.clock_domains.cd_line = ClockDomain(reset_less=True)
        self.comb += self.cd_line.clk.eq(self.iosignals.VGA_HS)

        self.comb += self.display_enabled.eq(self.h_display & self.v_display)

        fsm_h = ClockDomainsRenamer("pxl")(FSM())
        fsm_v = ClockDomainsRenamer("line")(FSM())

        def wait(cnt, duration, current_state, next_state):
            return \
                If(cnt == duration - 1,
                    NextValue(cnt, 0),
                    NextState(next_state)).\
                Else(
                    NextValue(cnt, cnt + 1),
                    NextState(current_state))

        fsm_h.act("FRONT_PORCH",
                self.iosignals.VGA_HS.eq(0),
                self.h_display.eq(0),
                wait(self.h_counter, 16, "FRONT_PORCH", "SYNC"))
        fsm_h.act("SYNC",
                self.iosignals.VGA_HS.eq(1),
                self.h_display.eq(0),
                wait(self.h_counter, 96, "SYNC", "BACK_PORCH"))
        fsm_h.act("BACK_PORCH",
                self.iosignals.VGA_HS.eq(0),
                self.h_display.eq(0),
                wait(self.h_counter, 48, "BACK_PORCH", "DISPLAY"))
        fsm_h.act("DISPLAY",
                self.iosignals.VGA_HS.eq(0),
                self.h_display.eq(1),
                wait(self.h_counter, 640, "DISPLAY", "FRONT_PORCH"))

        fsm_v.act("FRONT_PORCH",
                self.iosignals.VGA_VS.eq(0),
                self.v_display.eq(0),
                wait(self.v_counter, 10, "FRONT_PORCH", "SYNC"))
        fsm_v.act("SYNC",
                self.iosignals.VGA_VS.eq(1),
                self.v_display.eq(0),
                wait(self.v_counter, 2, "SYNC", "BACK_PORCH"))
        fsm_v.act("BACK_PORCH",
                self.iosignals.VGA_VS.eq(0),
                self.v_display.eq(0),
                wait(self.v_counter, 33, "BACK_PORCH", "DISPLAY"))
        fsm_v.act("DISPLAY",
                self.iosignals.VGA_VS.eq(0),
                self.v_display.eq(1),
                wait(self.v_counter, 480, "DISPLAY", "FRONT_PORCH"))

        self.submodules += fsm_h
        self.submodules += fsm_v


        ## Pixels generator

        self.comb += self.iosignals.VGA_RED0.eq(self.px[2])
        self.comb += self.iosignals.VGA_GREEN0.eq(self.px[1])
        self.comb += self.iosignals.VGA_BLUE0.eq(self.px[0])

        if config == VideoConfig.CFG1:
            self.comb += self.iosignals.VGA_RED1.eq(self.px[5])
            self.comb += self.iosignals.VGA_GREEN1.eq(self.px[4])
            self.comb += self.iosignals.VGA_BLUE1.eq(self.px[3])

        self.comb += If(self.display_enabled,
                *self.display_logic).Else(self.px.eq(0))


class Video(BMIIModule):
    def __init__(self, config):
        BMIIModule.__init__(self, VideoIOModule(config))

    @classmethod
    def generate(cls, b, config):
        video = cls(config)
        b.add_module(video)

        b.ioctl.sb.pins.IO10 += video.iomodule.iosignals.VRAM_ADDR13
        b.ioctl.sb.pins.IO11 += video.iomodule.iosignals.VRAM_WR
        b.ioctl.sb.pins.IO12 += video.iomodule.iosignals.VRAM_ADDR9
        b.ioctl.sb.pins.IO13 += video.iomodule.iosignals.VRAM_ADDR8
        b.ioctl.sb.pins.IO14 += video.iomodule.iosignals.VRAM_CE
        b.ioctl.sb.pins.IO15 += video.iomodule.iosignals.VRAM_ADDR11
        b.ioctl.sb.pins.IO16 += video.iomodule.iosignals.VRAM_ADDR0
        b.ioctl.sb.pins.IO17 += video.iomodule.iosignals.VRAM_ADDR10
        b.ioctl.sb.pins.IO18 += video.iomodule.iosignals.VRAM_ADDR2
        b.ioctl.sb.pins.IO19 += video.iomodule.iosignals.VRAM_ADDR1
        b.ioctl.sb.pins.IO1A += video.iomodule.iosignals.VRAM_ADDR4
        b.ioctl.sb.pins.IO1B += video.iomodule.iosignals.VRAM_ADDR3
        b.ioctl.sb.pins.IO1C += video.iomodule.iosignals.VRAM_ADDR6
        b.ioctl.sb.pins.IO1D += video.iomodule.iosignals.VRAM_ADDR5
        b.ioctl.sb.pins.IO1E += video.iomodule.iosignals.VRAM_ADDR12
        b.ioctl.sb.pins.IO1F += video.iomodule.iosignals.VRAM_ADDR7

        b.ioctl.sb.pins.IO20 += video.iomodule.iosignals.VRAM_DOUT7
        b.ioctl.sb.pins.IO20 += video.iomodule.iosignals.VRAM_DIN7
        b.ioctl.sb.pins.IO20 += video.iomodule.iosignals.VRAM_DDIR7

        b.ioctl.sb.pins.IO21 += video.iomodule.iosignals.VRAM_DOUT6
        b.ioctl.sb.pins.IO21 += video.iomodule.iosignals.VRAM_DIN6
        b.ioctl.sb.pins.IO21 += video.iomodule.iosignals.VRAM_DDIR6

        b.ioctl.sb.pins.IO22 += video.iomodule.iosignals.VRAM_DOUT5
        b.ioctl.sb.pins.IO22 += video.iomodule.iosignals.VRAM_DIN5
        b.ioctl.sb.pins.IO22 += video.iomodule.iosignals.VRAM_DDIR5

        b.ioctl.sb.pins.IO23 += video.iomodule.iosignals.VRAM_DOUT4
        b.ioctl.sb.pins.IO23 += video.iomodule.iosignals.VRAM_DIN4
        b.ioctl.sb.pins.IO23 += video.iomodule.iosignals.VRAM_DDIR4

        b.ioctl.sb.pins.IO24 += video.iomodule.iosignals.VRAM_DOUT3
        b.ioctl.sb.pins.IO24 += video.iomodule.iosignals.VRAM_DIN3
        b.ioctl.sb.pins.IO24 += video.iomodule.iosignals.VRAM_DDIR3

        b.ioctl.sb.pins.IO25 += video.iomodule.iosignals.VRAM_DOUT0
        b.ioctl.sb.pins.IO25 += video.iomodule.iosignals.VRAM_DIN0
        b.ioctl.sb.pins.IO25 += video.iomodule.iosignals.VRAM_DDIR0

        b.ioctl.sb.pins.IO26 += video.iomodule.iosignals.VRAM_DOUT1
        b.ioctl.sb.pins.IO26 += video.iomodule.iosignals.VRAM_DIN1
        b.ioctl.sb.pins.IO26 += video.iomodule.iosignals.VRAM_DDIR1

        b.ioctl.sb.pins.IO27 += video.iomodule.iosignals.VRAM_DOUT2
        b.ioctl.sb.pins.IO27 += video.iomodule.iosignals.VRAM_DIN2
        b.ioctl.sb.pins.IO27 += video.iomodule.iosignals.VRAM_DDIR2

        b.ioctl.sb.pins.IO29 += video.iomodule.iosignals.VGA_RED0
        b.ioctl.sb.pins.IO2B += video.iomodule.iosignals.VGA_GREEN0
        b.ioctl.sb.pins.IO2D += video.iomodule.iosignals.VGA_BLUE0

        b.ioctl.sb.pins.IO2E += video.iomodule.iosignals.VGA_HS
        b.ioctl.sb.pins.IO2F += video.iomodule.iosignals.VGA_VS

        if config == VideoConfig.CFG1:
            b.ioctl.sb.pins.IO28 += video.iomodule.iosignals.VGA_RED1
            b.ioctl.sb.pins.IO2A += video.iomodule.iosignals.VGA_GREEN1
            b.ioctl.sb.pins.IO2C += video.iomodule.iosignals.VGA_BLUE1
        elif config == VideoConfig.CFG2:
            b.ioctl.sb.pins.IO28 += video.iomodule.iosignals.VRAM_ADDR14
            b.ioctl.sb.pins.IO2A += video.iomodule.iosignals.VRAM_ADDR15
            b.ioctl.sb.pins.IO2C += video.iomodule.iosignals.VRAM_ADDR16

        return video

    @classmethod
    def default(cls, bmii):
        return cls.generate(bmii, VideoConfig.CFG1)

    def write_vram(self, addr, *data):
        self.drv.ADDRH = (addr >> 8) & 0xFF
        self.drv.ADDRL = addr & 0xFF
        for i in data:
            self.drv.DATA = i
