#ifndef EPUTILS_H
#define EPUTILS_H

#include "fx2regs.h"

static inline void stall_ep0(void)
{
    EP0CS |= bmEPSTALL;
}

#endif /* EPUTILS_H */
