#ifndef GPIF_H
#define GPIF_H

#include "fx2regs.h"
#include "led.h"

static void wait_gpif_done(void)
{
    while (!(GPIFTRIG & 0x80))
        continue;
}

static void gpif_enable(void)
{
    led_set(1);
    IFCONFIG = 0x62;
}

static void gpif_disable(void)
{
    IFCONFIG = 0x60;
}

void GpifInit(void);

#endif /* GPIF_H */
