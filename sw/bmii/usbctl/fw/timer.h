#ifndef TIMER_H
#define TIMER_H

#include "fx2ints.h"
#include "fx2regs.h"

void timer_init(void);

void timer2_ovf_isr(void) __interrupt TF2_ISR;

enum spd {
    CLK_12M = 0,
    CLK_24M,
    CLK_48M
};

static inline void set_cpu_freq(enum cpu_spd spd)
{
    const BYTE current_spd = spd;
    CPUCS = (CPUCS & ~bmCLKSPD) | ((current_spd & 3) << 3);
}

#endif /* TIMER_H */
