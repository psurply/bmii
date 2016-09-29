from bmii import *

from video import *


class BasicVideoIOModule(VideoIOModule):
    sprite_addr = 0x0

    @property
    def display_logic(self):
        bg = Signal(3)
        self.comb += bg.eq(self.h_counter[6:9])

        fg = Signal(3)
        self.comb += fg.eq(self.vram_data)

        return [self.px.eq(bg ^ fg)]

    @property
    def vram_drive_addr_logic(self):
        return [
            NextValue(self.vram_addr, self.sprite_addr +
                self.next_h_counter[0:5] + (self.v_counter[1:5] << 5))
        ]

    @property
    def vram_read_logic(self):
        return [NextValue(self.vram_data, self.vram_din)]

    def __init__(self):
        self.vram_data = Signal(3)
        VideoIOModule.__init__(self, VideoConfig.CFG2)


class BasicVideo(Video):
    sprite = [
        0b00000000000000000000000000,
        0b00000000000000000000000000,
        0b11100000011111100011111111,
        0b11100000111111110011111111,
        0b11100001110000111011100000,
        0b11100001100000011011100000,
        0b11100001110000000011100000,
        0b11100000111111100011111100,
        0b11100000001111110011111100,
        0b11100000000000111011100000,
        0b11100001100000011011100000,
        0b11100001110000111011100000,
        0b11111110111111110011111111,
        0b11111110011111100011111111,
        0b00000000000000000000000000,
        0b00000000000000000000000000,
    ]

    def __init__(self, config):
        BMIIModule.__init__(self, BasicVideoIOModule())

    def write_sprite(self, color):
        d = []
        for l in self.sprite:
            for i in range(31, -1, -1):
                d.append(color if (l >> i & 1) else 0)
        self.write_vram(self.iomodule.sprite_addr, *d)


if __name__ == "__main__":
    b = BMII.default()
    v = BasicVideo.default(b)

    b.cli()
    b.usbctl.drv.set_cpu_speed(CPUSpd.CLK_48M)
    v.write_sprite(0b111)
