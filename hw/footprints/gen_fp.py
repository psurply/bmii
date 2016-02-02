#!/usr/bin/env python2

import footgen

f = footgen.Footgen("SSOP56", output_format="geda")
f.pins = 56
f.pitch = 0.635
f.width = 7.4
f.padheight = 0.4
f.padwidth = 2
f.so()
f.silk_crop(11, 20, pin1="circle")
f.finish()
