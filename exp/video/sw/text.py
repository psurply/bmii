from bmii import *

from video import *


class TextVideoIOModule(VideoIOModule):
    framebuffer_addr = 0x0
    framebuffer_size = 1600
    framebuffer_width = 40
    charset_addr = 0x700
    char_width = 8
    char_height = 12

    @property
    def display_logic(self):
        text = Signal(3)
        self.comb += \
            If((self.current_char_line >> self.h_counter[1:4]) & 1,
                text.eq(self.current_char_color[0:3])).\
            Else(text.eq(self.current_char_color[3:6]))

        return [self.px.eq(text)]

    @property
    def vram_drive_addr_logic(self):
        v_offset = Signal(5)
        v_char_index = Signal(14)
        self.sync.line += \
            If(~self.v_display,
                v_offset.eq(0),
                v_char_index.eq(0)).\
            Elif((v_offset[1:5] == self.char_height - 1) & v_offset[0],
                v_offset.eq(0),
                v_char_index.eq(v_char_index + self.framebuffer_width)).\
            Else(v_offset.eq(v_offset + 1))

        h_char_index = Signal(7)
        self.comb += \
            If(self.next_h_counter[4:10] == self.framebuffer_width - 1,
                h_char_index.eq(0)).\
            Else(h_char_index.eq(self.next_h_counter[4:10] + 1))

        return [
            If(self.next_h_counter[0:4] == 11,
                NextValue(self.vram_addr, self.framebuffer_addr +\
                   ((v_char_index + h_char_index) << 1) + 1)).\
            Elif(self.next_h_counter[0:4] == 13,
                NextValue(self.vram_addr, self.framebuffer_addr +\
                   ((v_char_index + h_char_index) << 1))).\
            Elif(self.next_h_counter[0:4] == 0,
                NextValue(self.vram_addr, self.charset_addr +
                    self.current_char[0:4] +
                    ((self.current_char[4:8] << 4) * 12) +
                    ((v_offset[1:5]) << 4)))
        ]

    @property
    def vram_read_logic(self):
        return [
            If(self.next_h_counter[0:4] == 12,
                NextValue(self.next_char_color, self.vram_din)).\
            Elif(self.next_h_counter[0:4] == 14,
                NextValue(self.current_char, self.vram_din)).\
            Elif(self.next_h_counter[0:4] == 1,
                NextValue(self.current_char_color, self.next_char_color),
                NextValue(self.current_char_line, self.vram_din))
        ]


    def __init__(self):
        self.current_char = Signal(8)
        self.current_char_color = Signal(8)
        self.current_char_line = Signal(8)
        self.next_char_color = Signal(8)

        VideoIOModule.__init__(self, VideoConfig.CFG2)


class TextVideo(Video):
    def __init__(self, config):
        BMIIModule.__init__(self, TextVideoIOModule())

    def load_charset(self):
        self.load_sprite_from_png("font.png", self.iomodule.charset_addr)

    def write_framebuffer(self, pos, data, fg=0b111, bg=0b000):
        self.set_vram_cursor(self.iomodule.framebuffer_addr +
                ((pos[1] * 40 + pos[0]) << 1))
        for c in data:
            self.write_vram(None, c)
            self.write_vram(None, fg | (bg << 3))

    def clear_framebuffer(self):
        self.set_vram_cursor(self.iomodule.framebuffer_addr)
        self.write_vram(None, *([0] * self.iomodule.framebuffer_size))

    def draw_frame(self):
        self.write_framebuffer((1, 0), b"\xc4" * 38)
        self.write_framebuffer((1, 19), b"\xc4" * 38)
        for l in range(1, 19):
            self.write_framebuffer((0, l), b"\xb3")
            self.write_framebuffer((39, l), b"\xb3")
        self.write_framebuffer((0, 0), b"\xda")
        self.write_framebuffer((0, 19), b"\xc0")
        self.write_framebuffer((39, 0), b"\xbf")
        self.write_framebuffer((39, 19), b"\xd9")


if __name__ == "__main__":
    b = BMII(shrink=True)
    v = TextVideo.default(b)

    b.cli()
    b.usbctl.drv.set_cpu_speed(CPUSpd.CLK_48M)
    v.load_charset()
    v.clear_framebuffer()
    v.draw_frame()
    v.write_framebuffer((1, 0), b"Test")
    v.write_framebuffer((2, 8), b"\x01 Hello World!")
