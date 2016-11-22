#ifndef INTR_H
#define INTR_H

#include "fx2ints.h"

void int0_init(void);
void int0_isr(void) __interrupt IE0_ISR;

#define EVENT_QUEUE_EMPTY   0xFF
BYTE event_queue_dequeue();

#endif /* INTR_H */
