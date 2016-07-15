#include "gpifisr.h"
#include "eputils.h"

void gpif_isr(void)     __interrupt (10) {}

void ep2pf_isr()        __interrupt (41) {}
void ep4pf_isr()        __interrupt (42) {}
void ep6pf_isr()        __interrupt (43) {}
void ep8pf_isr()        __interrupt (44) {}
void ep2ef_isr()        __interrupt (45) {}
void ep4ef_isr()        __interrupt (46) {}
void ep6ef_isr()        __interrupt (47) {}
void ep8ef_isr()        __interrupt (48) {}
void ep2ff_isr()        __interrupt (49) {}
void ep4ff_isr()        __interrupt (50) {}
void ep6ff_isr()        __interrupt (51) {}
void ep8ff_isr()        __interrupt (52) {}

void gpifdone_isr()     __interrupt (53)
{
    clear_gpif();
}

void gpifwf_isr()       __interrupt (54) {}
