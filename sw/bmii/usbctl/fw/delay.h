#ifndef DELAY_H
#define DELAY_H

#include "fx2types.h"

static inline void delay(WORD millis)
{
    volatile WORD cnt;
    const WORD loop_count = 706;

    do {
        cnt = loop_count;
        do {
        } while (--cnt);
    } while (--millis);
}

#endif /* DELAY_H */
