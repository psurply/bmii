#!/usr/bin/env python2

import footgen

f = footgen.Footgen("CON351779862g", output_format="geda")
f.pins = 60
f.pitch = 0.8
f.width = 2.4
f.padheight = 0.5
f.padwidth = 2
f.so()
f.finish()
