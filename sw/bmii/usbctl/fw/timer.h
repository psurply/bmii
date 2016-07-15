#ifndef TIMER_H
#define TIMER_H

void timer_init(void);

void timer2_ovf_isr(void) __interrupt TF2_ISR;

#endif /* TIMER_H */
