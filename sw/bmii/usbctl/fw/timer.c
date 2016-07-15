#include "led.h"
#include "fx2ints.h"
#include "timer.h"

void timer_init(void)
{
    T2CON = 0;
    TCLK = 0;
    RCLK = 0;
    CP_RL2 = 0;

    ET2 = 1;
    TL2 = 0;
    TH2 = 0;
    RCAP2L = 0;
    RCAP2H = 0;
    TR2 = 1;
}

void timer2_ovf_isr(void) __interrupt TF2_ISR
{
    static WORD cnt = 0;

    if (++cnt > 8) {
        cnt = 0;
        led_set(0);
    }

    TF2 = 0;
    EXF2 = 0;
}
