#include <fx2regs.h>
#include "hardware.h"
#include "delay.h"

//-----------------------------------------------------------------------------

/* JTAG TCK, AS/PS DCLK */

sbit at 0x90+7        TCK;
#define bmTCKOE       bmBIT7
#define SetTCK(x)     do{TCK=(x);}while(0)

/* JTAG TDI, AS ASDI, PS DATA0 */

sbit at 0x90+4        TDI;
#define bmTDIOE       bmBIT4
#define SetTDI(x)     do{TDI=(x);}while(0)

/* JTAG TMS, AS/PS nCONFIG */

sbit at 0x90+5        TMS;
#define bmTMSOE       bmBIT5
#define SetTMS(x)     do{TMS=(x);}while(0)

/* JTAG TDO, AS/PS CONF_DONE */

sbit at 0x90+6        TDO;
#define bmTDOOE       bmBIT6
#define GetTDO(x)     TDO

//-----------------------------------------------------------------------------

#define bmPROGOUTOE (bmTCKOE|bmTDIOE|bmTMSOE)
#define bmPROGINOE  (bmTDOOE)

//-----------------------------------------------------------------------------

void ProgIO_Poll(void)    {}
// These aren't called anywhere in usbjtag.c, but I plan to do so...
void ProgIO_Enable(void)  {}
void ProgIO_Disable(void) {}
void ProgIO_Deinit(void)  {}


void ProgIO_Init(void)
{
  /* The following code depends on your actual circuit design.
     Make required changes _before_ you try the code! */
  CPUCS = CPUCS & ~bmCLKSPD;

  // TDO input, others output
  OEB=(OEB&~bmPROGINOE) | bmPROGOUTOE;

  // Disable external IFCLK
  IFCONFIG = bmIFCLKSRC;

  // Enable JTAGE
  IOA = 0;
  OEA = (1 << 2);
}

void ProgIO_Set_State(unsigned char d)
{
  /* Set state of output pins:
   *
   * d.0 => TCK
   * d.1 => TMS
   * d.2 => nCE (only #ifdef HAVE_AS_MODE)
   * d.3 => nCS (only #ifdef HAVE_AS_MODE)
   * d.4 => TDI
   * d.6 => LED / Output Enable
   */

  SetTCK((d & bmBIT0) ? 1 : 0);
  SetTMS((d & bmBIT1) ? 1 : 0);
  SetTDI((d & bmBIT4) ? 1 : 0);
}

unsigned char ProgIO_Set_Get_State(unsigned char d)
{
  /* Set state of output pins (s.a.)
   * then read state of input pins:
   *
   * TDO => d.0
   * DATAOUT => d.1 (only #ifdef HAVE_AS_MODE)
   */

  ProgIO_Set_State(d);
  return 2|GetTDO(); /* DATAOUT assumed high, no AS mode */
}

//-----------------------------------------------------------------------------

void ProgIO_ShiftOut(unsigned char c)
{
  /* Shift out byte C: 
   *
   * 8x {
   *   Output least significant bit on TDI
   *   Raise TCK
   *   Shift c right
   *   Lower TCK
   * }
   */
 
  (void)c; /* argument passed in DPL */

  _asm
        MOV  A,DPL
        ;; Bit0
        RRC  A
        MOV  _TDI,C
        SETB _TCK
        ;; Bit1
        RRC  A
        CLR  _TCK
        MOV  _TDI,C
        SETB _TCK
        ;; Bit2
        RRC  A
        CLR  _TCK
        MOV  _TDI,C
        SETB _TCK
        ;; Bit3
        RRC  A
        CLR  _TCK
        MOV  _TDI,C
        SETB _TCK
        ;; Bit4
        RRC  A
        CLR  _TCK
        MOV  _TDI,C
        SETB _TCK
        ;; Bit5
        RRC  A
        CLR  _TCK
        MOV  _TDI,C
        SETB _TCK
        ;; Bit6
        RRC  A
        CLR  _TCK
        MOV  _TDI,C
        SETB _TCK
        ;; Bit7
        RRC  A
        CLR  _TCK
        MOV  _TDI,C
        SETB _TCK
        NOP 
        CLR  _TCK
        ret
  _endasm;
}

/*
;; For ShiftInOut, the timing is a little more
;; critical because we have to read _TDO/shift/set _TDI
;; when _TCK is low. But 20% duty cycle at 48/4/5 MHz
;; is just like 50% at 6 Mhz, and that's still acceptable
*/

unsigned char ProgIO_ShiftInOut(unsigned char c)
{
  /* Shift out byte C, shift in from TDO:
   *
   * 8x {
   *   Read carry from TDO
   *   Output least significant bit on TDI
   *   Raise TCK
   *   Shift c right, append carry (TDO) at left
   *   Lower TCK
   * }
   * Return c.
   */

   (void)c; /* argument passed in DPL */

  _asm
        MOV  A,DPL

        ;; Bit0
        MOV  C,_TDO
        RRC  A
        MOV  _TDI,C
        SETB _TCK
        CLR  _TCK
        ;; Bit1
        MOV  C,_TDO
        RRC  A
        MOV  _TDI,C
        SETB _TCK
        CLR  _TCK
        ;; Bit2
        MOV  C,_TDO
        RRC  A
        MOV  _TDI,C
        SETB _TCK
        CLR  _TCK
        ;; Bit3
        MOV  C,_TDO
        RRC  A
        MOV  _TDI,C
        SETB _TCK
        CLR  _TCK
        ;; Bit4
        MOV  C,_TDO
        RRC  A
        MOV  _TDI,C
        SETB _TCK
        CLR  _TCK
        ;; Bit5
        MOV  C,_TDO
        RRC  A
        MOV  _TDI,C
        SETB _TCK
        CLR  _TCK
        ;; Bit6
        MOV  C,_TDO
        RRC  A
        MOV  _TDI,C
        SETB _TCK
        CLR  _TCK
        ;; Bit7
        MOV  C,_TDO
        RRC  A
        MOV  _TDI,C
        SETB _TCK
        CLR  _TCK

        MOV  DPL,A
        ret
  _endasm;

  /* return value in DPL */

  return c;
}



