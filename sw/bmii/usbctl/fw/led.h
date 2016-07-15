#ifndef LED_H
#define LED_H

#include "fx2regs.h"

#define LED_OFFSET 5

static inline void led_init(void)
{
    IOD = 0;
    OED = (1 << LED_OFFSET);
}

static inline void led_blink(void)
{
    PD5 ^= 1;
}

static inline void led_set(BYTE value)
{
    PD5 = value;
}


#endif /* LED_H */
