from migen import *

class LevelToPulse(Module):
    def __init__(self, level, pulse):
        self.level = level
        self.pulse = pulse

        fsm = FSM()
        self.submodules += fsm

        fsm.act("IDLE",
            self.pulse.eq(0),
            If(self.level, NextState("PULSE"))\
            .Else(NextState("IDLE"))
        )
        fsm.act("PULSE",
            self.pulse.eq(1),
            NextState("LOCKED")
        )
        fsm.act("LOCKED",
            self.pulse.eq(0),
            If(self.level, NextState("LOCKED"))\
            .Else(NextState("IDLE"))
        )

class NLevelToPulse(Module):
    def __init__(self, level, pulse):
        self.level = level
        self.pulse = pulse

        fsm = FSM()
        self.submodules += fsm

        fsm.act("IDLE",
            self.pulse.eq(0),
            If(self.level, NextState("LOCKED"))\
            .Else(NextState("IDLE"))
        )
        fsm.act("PULSE",
            self.pulse.eq(1),
            NextState("IDLE")
        )
        fsm.act("LOCKED",
            self.pulse.eq(0),
            If(self.level, NextState("LOCKED"))\
            .Else(NextState("PULSE"))
        )
