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
        self.cursor = 0

    def load_charset(self):
        self.load_sprite_from_png("font.png", self.iomodule.charset_addr)

    def write_framebuffer(self, pos, data, fg=0b111, bg=0b000):
        if pos is not None:
            self.cursor = self.iomodule.framebuffer_addr + \
                ((pos[1] * 40 + pos[0]) << 1)
        else:
            pos = (1, 1)
        self.set_vram_cursor(self.cursor)
        for c in data:
            if c == '\n':
                self.cursor += (40 * 2 - (self.cursor % (40 * 2))) + pos[0] * 2
                self.set_vram_cursor(self.cursor)
            else:
                if isinstance(c, str):
                    c = ord(c)
                self.cursor += 2
                self.write_vram(None, c)
                self.write_vram(None, fg | (bg << 3))

    def clear_framebuffer(self):
        self.set_vram_cursor(self.iomodule.framebuffer_addr)
        self.write_vram(None, *([0] * self.iomodule.framebuffer_size))

if __name__ == "__main__":
    b = BMII(shrink=True)
    v = TextVideo.default(b)

    b.cli()
    b.usbctl.drv.set_cpu_speed(CPUSpd.CLK_48M)
    v.load_charset()
    v.clear_framebuffer()
    v.write_framebuffer((0, 0), b"\x01", fg=0b000, bg=0b111)
    v.write_framebuffer((1, 0), b"\x02", fg=0b001, bg=0b110)
    v.write_framebuffer((2, 0), b"\x03", fg=0b010, bg=0b101)
    v.write_framebuffer((3, 0), b"\x04", fg=0b011, bg=0b100)
    v.write_framebuffer((4, 0), b"\x05", fg=0b100, bg=0b011)
    v.write_framebuffer((5, 0), b"\x06", fg=0b101, bg=0b010)
    v.write_framebuffer((6, 0), b"\x07", fg=0b110, bg=0b001)
    v.write_framebuffer((7, 0), b"\x08", fg=0b111, bg=0b000)
    v.write_framebuffer((8, 0), b"\x09", fg=0b000, bg=0b111)
    v.write_framebuffer((9, 0), b"\x0A", fg=0b001, bg=0b110)
    v.write_framebuffer((10, 0), b"\x0B", fg=0b010, bg=0b101)
    v.write_framebuffer((11, 0), b"\x0C", fg=0b011, bg=0b100)
    v.write_framebuffer((12, 0), b"\x0D", fg=0b100, bg=0b011)
    v.write_framebuffer((13, 0), b"\x0E", fg=0b101, bg=0b010)
    v.write_framebuffer((14, 0), b"\x0F", fg=0b110, bg=0b001)
    v.write_framebuffer((15, 0), b"\x10", fg=0b111, bg=0b000)
    v.write_framebuffer((16, 0), b"\x11", fg=0b000, bg=0b111)
    v.write_framebuffer((17, 0), b"\x12", fg=0b001, bg=0b110)
    v.write_framebuffer((18, 0), b"\x13", fg=0b010, bg=0b101)
    v.write_framebuffer((19, 0), b"\x14", fg=0b011, bg=0b100)
    v.write_framebuffer((20, 0), b"\x15", fg=0b100, bg=0b011)
    v.write_framebuffer((21, 0), b"\x16", fg=0b101, bg=0b010)
    v.write_framebuffer((22, 0), b"\x17", fg=0b110, bg=0b001)
    v.write_framebuffer((23, 0), b"\x18", fg=0b111, bg=0b000)
    v.write_framebuffer((24, 0), b"\x19", fg=0b000, bg=0b111)
    v.write_framebuffer((25, 0), b"\x1A", fg=0b001, bg=0b110)
    v.write_framebuffer((26, 0), b"\x1B", fg=0b010, bg=0b101)
    v.write_framebuffer((27, 0), b"\x1C", fg=0b011, bg=0b100)
    v.write_framebuffer((28, 0), b"\x1D", fg=0b100, bg=0b011)
    v.write_framebuffer((29, 0), b"\x1E", fg=0b101, bg=0b010)
    v.write_framebuffer((30, 0), b"\x1F", fg=0b110, bg=0b001)
    v.write_framebuffer((31, 0), b"\x20", fg=0b111, bg=0b000)
    v.write_framebuffer((32, 0), b"\x21", fg=0b000, bg=0b111)
    v.write_framebuffer((33, 0), b"\x22", fg=0b001, bg=0b110)
    v.write_framebuffer((34, 0), b"\x23", fg=0b010, bg=0b101)
    v.write_framebuffer((35, 0), b"\x24", fg=0b011, bg=0b100)
    v.write_framebuffer((36, 0), b"\x25", fg=0b100, bg=0b011)
    v.write_framebuffer((37, 0), b"\x26", fg=0b101, bg=0b010)
    v.write_framebuffer((38, 0), b"\x27", fg=0b110, bg=0b001)
 
    v.write_framebuffer((1, 2), b"Ash vegal durbatul\x96k,")
    v.write_framebuffer((1, 3), b"ash vegal gimbatul,")
    v.write_framebuffer((1, 4), b"ash vegal thrakatul\x96k")
    v.write_framebuffer((2, 5), b"agh burzum-ishi krimpatul.")
