#include "io.h"
#include "led.h"
#include "fx2regs.h"
#include "fx2sdly.h"
#include "gpif.h"

void io_init(void)
{
    EP2CFG = 0xA2;
    SYNCDELAY;
    EP2CFG = 0xA2;
    SYNCDELAY;
    FIFORESET = 0x80;
    SYNCDELAY;
    FIFORESET = 0x82;
    SYNCDELAY;
    FIFORESET = 0x00;
    SYNCDELAY;
    OUTPKTEND = 0x82;
    SYNCDELAY;
    OUTPKTEND = 0x82;
    SYNCDELAY;
    EP2FIFOCFG = 0x10;   // EP2 is AUTOOUT=1, AUTOIN=0, ZEROLEN=0, WORDWIDE=0

    EP6CFG = 0xE2;
    SYNCDELAY;
    EP6FIFOCFG = 0x0C;
    SYNCDELAY;
    EP6AUTOINLENH = 0x00;
    SYNCDELAY;
    EP6AUTOINLENL = 0x01;
    SYNCDELAY;

    EP1INCFG &= ~bmVALID;
    SYNCDELAY;
    EP1OUTCFG &= ~bmVALID;
    SYNCDELAY;
    EP4CFG &= ~bmVALID;
    SYNCDELAY;
    EP8CFG &= ~bmVALID;
    SYNCDELAY;

    EP2BCL = 0x80;
    SYNCDELAY;
    EP2BCL = 0x80;
    SYNCDELAY;
}

void io_select_reg(BYTE addr)
{
    wait_gpif_done();

    XGPIFSGLDATH = 0;
    XGPIFSGLDATLX = addr;
}

void io_load_rdfifo(BYTE size)
{
    volatile BYTE dummy;

    wait_gpif_done();

    GPIFTCB0 = size;
    SYNCDELAY;
    GPIFTCB1 = 0;
    SYNCDELAY;
    GPIFTCB2 = 0;
    SYNCDELAY;
    GPIFTCB3 = 0;

    EP6AUTOINLENH = 0x00;
    SYNCDELAY;
    EP6AUTOINLENL = size;
    SYNCDELAY;

    dummy = EP6GPIFTRIG;
}

void io_write_data(void)
{
    wait_gpif_done();

    GPIFTCB0 = 1;
    SYNCDELAY;
    GPIFTCB1 = 0;
    SYNCDELAY;
    GPIFTCB2 = 0;
    SYNCDELAY;
    GPIFTCB3 = 0;
    SYNCDELAY;
    EP2GPIFTRIG = 0xFF;
}
