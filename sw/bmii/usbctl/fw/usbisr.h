#ifndef USBJT_H
#define USBJT_H

#include "fx2regs.h"
#include "fx2ints.h"

static inline void use_usb_ints(void)
{
    EUSB=1;
    INTSETUP|=bmAV2EN;
}

static inline void clear_usbint(void)
{
    EXIF &= ~0x10;
}

static inline void enable_sudav()
{
    USBIE |= bmSUDAV;
}

static inline void clear_sudav(void)
{
    clear_usbint();
    USBIRQ = bmSUDAV;
}

void usb_isr(void)      __interrupt USBINT_ISR;

void sudav_isr()        __interrupt (13);
void sof_isr()          __interrupt (14);
void sutok_isr()        __interrupt (15);
void suspend_isr()      __interrupt (16);
void usbreset_isr()     __interrupt (17);
void hispeed_isr()      __interrupt (18);
void ep0ack_isr()       __interrupt (19);
void ep0in_isr()        __interrupt (20);
void ep0out_isr()       __interrupt (21);
void ep1in_isr()        __interrupt (22);
void ep1out_isr()       __interrupt (23);
void ep2_isr()          __interrupt (24);
void ep4_isr()          __interrupt (25);
void ep6_isr()          __interrupt (26);
void ep8_isr()          __interrupt (27);
void ibn_isr()          __interrupt (28);
void ep0ping_isr()      __interrupt (29);
void ep1ping_isr()      __interrupt (30);
void ep2ping_isr()      __interrupt (31);
void ep4ping_isr()      __interrupt (32);
void ep6ping_isr()      __interrupt (33);
void ep8ping_isr()      __interrupt (34);
void errlimit_isr()     __interrupt (35);
void ep2isoerr_isr()    __interrupt (36);
void ep4isoerr_isr()    __interrupt (37);
void ep6isoerr_isr()    __interrupt (38);
void ep8isoerr_isr()    __interrupt (39);
void spare_isr()        __interrupt (40);

#endif /* USBJT_H */
