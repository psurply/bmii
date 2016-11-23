from bmii import *
import yaml
import sys
import urwid

from text import *


class SlideVideo(TextVideo):
    def draw_frame(self):
        self.write_framebuffer((1, 0), b"\xb0" * 38)
        self.write_framebuffer((1, 19), b"\xb0" * 38)
        for l in range(1, 19):
            self.write_framebuffer((0, l), b"\xb0")
            self.write_framebuffer((39, l), b"\xb0")
        self.write_framebuffer((0, 0), b"\xb0")
        self.write_framebuffer((0, 19), b"\xb0")
        self.write_framebuffer((39, 0), b"\xb0")
        self.write_framebuffer((39, 19), b"\xb0")

    def draw_title(self, title):
        self.write_framebuffer((1, 0), title, fg=0b000, bg=0b111)

    def draw_footer(self, slide):
        self.write_framebuffer((35, 19),
                "{}/{}".format(self.sd.index(slide) + 1,
                    len(self.sd)))

    def draw_item(self, item, depth=0):
        if isinstance(item, str):
            item = {"text": item}
        if not "fg" in item:
            item["fg"] = 0b111
        if not "bg" in item:
            item["bg"] = 0b000
        if "text" in item:
            self.write_framebuffer(None, item["text"] + "\n", item["fg"], item["bg"])
        if "items" in item:
            for i in item["items"]:
                if depth == 1:
                    self.write_framebuffer(None, b"  \x07 ")
                elif depth == 2:
                    self.write_framebuffer(None, b"    \xfa ")
                else:
                    self.write_framebuffer(None, b"\x10 ")
                self.draw_item(i, depth=depth + 1)

    def draw_body(self, body):
        for item in body:
            self.draw_item(item)

    def display_slide(self, slide):
        self.clear_framebuffer()
        self.draw_frame()

        if "body" in slide:
            self.draw_title(slide["title"])
            self.draw_footer(slide)
            self.write_framebuffer((1,1), "\n")
            self.draw_body(slide["body"])
        else:
            self.write_framebuffer((1, 2), slide["title"], fg=0b000, bg=0b111)
            self.write_framebuffer((1, 4), slide["subtitle"])
            self.write_framebuffer((1, 17), slide["authors"])
            self.write_framebuffer((1, 18), slide["date"])

    def update_display(self):
        self.display_slide(self.sd[self.slide_id])

    def display(self, f):
        def handle_input(key):
            if key in ('q', 'Q'):
                raise urwid.ExitMainLoop()
            elif key in ('right', 'j', ' '):
                if self.slide_id < len(self.sd) - 1:
                    self.slide_id += 1
            elif key in ('left', 'k'):
                if self.slide_id > 0:
                    self.slide_id -= 1
            self.update_display()

        self.load_charset()
        self.sd = list(yaml.load_all(f))
        self.slide_id = 0
        self.update_display()

        txt = urwid.Text(u"Presenting...")
        fill = urwid.Filler(txt, 'bottom')
        urwid.MainLoop(fill, unhandled_input=handle_input).run()


def main():
    b = BMII(shrink=True)
    v = SlideVideo.default(b)

    b.usbctl.drv.set_cpu_speed(CPUSpd.CLK_48M)
    if (len(sys.argv) > 1):
        with open(sys.argv[1], 'r') as f:
            v.display(f)

if __name__ == "__main__":
    main()

