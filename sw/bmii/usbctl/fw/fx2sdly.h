#ifndef FX2SDLY_H
#define FX2SDLY_H

#define NOP __asm nop __endasm
#define SYNCDELAY NOP; NOP; NOP; NOP

#endif /* FX2SDLY_H */
