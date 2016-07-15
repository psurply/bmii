from migen import *

IBus = [
        ("maddr",   3, DIR_M_TO_S),
        ("raddr",   5, DIR_M_TO_S),
        ("wr",      1, DIR_M_TO_S),
        ("req",     1, DIR_M_TO_S),
        ("mosi",    8, DIR_M_TO_S),
        ("miso",    8, DIR_S_TO_M),
]
