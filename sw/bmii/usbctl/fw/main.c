#include "delay.h"
#include "eputils.h"
#include "gpif.h"
#include "gpifisr.h"
#include "io.h"
#include "led.h"
#include "fw.h"
#include "fx2ints.h"
#include "fx2regs.h"
#include "setupdat.h"
#include "timer.h"
#include "usbisr.h"

struct fw_status fw_status = {
    .do_sud = FALSE,
};

void resume_isr(void) __interrupt RESUME_ISR
{
    RESI = 0;
}

static inline void set_cpu_freq(void)
{
    enum spd {
        CLK_12M = 0,
        CLK_24M,
        CLK_48M
    };

    const BYTE current_spd = CLK_12M;
    CPUCS = (CPUCS & ~bmCLKSPD) | (current_spd << 3);
}

static void renumerate(void)
{
    if(!(USBCS & bmRENUM))
    {
        USBCS |= bmDISCON | bmRENUM;
        delay(1500);
        USBCS &= ~bmDISCON;
    }
}

static void deassert_jtage(void)
{
    PA5 = 2;
    OEA = (1 << 2);
}

static void init(void)
{
    deassert_jtage();
    set_cpu_freq();

    ERESI = 1;
    EA = 1;

    led_init();
    timer_init();

    use_usb_ints();
    enable_sudav();

    renumerate();

    GpifInit();
    use_gpif_ints();
    enable_gpifdone();

    io_init();
}

void main(void)
{
    init();
    for (;;) {
        if (fw_status.do_sud) {
            gpif_enable();
            handle_setupdata();
            fw_status.do_sud = FALSE;
        }

        if (!(EP2468STAT & bmEP2EMPTY)) {
            gpif_enable();
            wait_gpif_done();
            io_write_data();
        }

        wait_gpif_done();
        gpif_disable();
    }
}
