#include "usbisr.h"
#include "fw.h"

void sudav_isr() __interrupt
{
    fw_status.do_sud = TRUE;
    clear_sudav();
}

void sof_isr() __interrupt {}
void sutok_isr() __interrupt {}
void suspend_isr() __interrupt {}
void usbreset_isr() __interrupt {}
void hispeed_isr() __interrupt {}
void ep0ack_isr() __interrupt {}
void ep0in_isr() __interrupt {}
void ep0out_isr() __interrupt {}
void ep1in_isr() __interrupt {}
void ep1out_isr() __interrupt {}
void ep2_isr() __interrupt {}
void ep4_isr() __interrupt {}
void ep6_isr() __interrupt {}
void ep8_isr() __interrupt {}
void ibn_isr() __interrupt {}
void ep0ping_isr() __interrupt {}
void ep1ping_isr() __interrupt {}
void ep2ping_isr() __interrupt {}
void ep4ping_isr() __interrupt {}
void ep6ping_isr() __interrupt {}
void ep8ping_isr() __interrupt {}
void errlimit_isr() __interrupt {}
void ep2isoerr_isr() __interrupt {}
void ep4isoerr_isr() __interrupt {}
void ep6isoerr_isr() __interrupt {}
void ep8isoerr_isr() __interrupt {}
void spare_isr() __interrupt {}
