#ifndef GPIFISR_H
#define GPIFISR_H

#include "fx2regs.h"

static inline void use_gpif_ints(void)
{
    EIEX4 = 1;
    INTSETUP |= bmAV4EN | INT4IN;
}

static inline void clear_gpif(void)
{
    EXIF &= ~0x40;
}

static inline void enable_gpifdone(void)
{
    GPIFIE |= 0x01;
}


void gpif_isr(void) __interrupt (10);
void ep2pf_isr() __interrupt;
void ep4pf_isr() __interrupt;
void ep6pf_isr() __interrupt;
void ep8pf_isr() __interrupt;
void ep2ef_isr() __interrupt;
void ep4ef_isr() __interrupt;
void ep6ef_isr() __interrupt;
void ep8ef_isr() __interrupt;
void ep2ff_isr() __interrupt;
void ep4ff_isr() __interrupt;
void ep6ff_isr() __interrupt;
void ep8ff_isr() __interrupt;
void gpifdone_isr() __interrupt;
void gpifwf_isr() __interrupt;

#endif /* GPIFISR_H */
