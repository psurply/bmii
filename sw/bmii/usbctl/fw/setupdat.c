#include "eputils.h"
#include "io.h"
#include "led.h"
#include "fx2macros.h"
#include "fx2regs.h"
#include "setupdat.h"

extern __code WORD dev_dscr;
extern __code WORD dev_qual_dscr;
extern __code WORD highspd_dscr;
extern __code WORD dev_strings;

WORD pDevConfig = (WORD)&highspd_dscr;

#define GF_DEVICE 0
#define GF_ENDPOINT 2
static void handle_clear_feature(void)
{
    switch (SETUPDAT[0]) {
        case GF_DEVICE:
        case GF_ENDPOINT:
            break;
        default:
            stall_ep0();
    }
}

static void get_str_dscr(void)
{
    struct string_dscr *pStr = (struct string_dscr*) &dev_strings;

    BYTE idx = SETUPDAT[2];
    BYTE i;

    for (i = 1; pStr && i < idx; ++i) {
        pStr = (struct string_dscr *) ((BYTE *) pStr + pStr->dsc_len);
        if (pStr->dsc_type != DSCR_STRING_TYPE)
            pStr = NULL;
    }

    if (pStr) {
        SUDPTRH = MSB((WORD) pStr);
        SUDPTRL = LSB((WORD) pStr);
    } else
        stall_ep0();
}

static void handle_get_descriptor(void)
{
   switch (SETUPDAT[3]) {
        case DSCR_DEVICE_TYPE:
            SUDPTRH = MSB((WORD) &dev_dscr);
            SUDPTRL = LSB((WORD) &dev_dscr);
            break;
        case DSCR_CONFIG_TYPE:
            SUDPTRH = MSB(pDevConfig);
            SUDPTRL = LSB(pDevConfig);
            break;
        case DSCR_STRING_TYPE:
            get_str_dscr();
            break;
        case DSCR_DEVQUAL_TYPE:
            SUDPTRH = MSB((WORD) &dev_qual_dscr);
            SUDPTRL = LSB((WORD) &dev_qual_dscr);
            break;
        default:
            stall_ep0();
    }
}


static int handle_vendor_command(void)
{
    enum vendor_cmd {
        SELECT_CREG = 0xF0,
        LOAD_RDFIFO = 0xF1,
    };

    switch (SETUPDAT[1]) {
        case SELECT_CREG:
            io_select_reg(SETUPDAT[2]);
            return 0;
        case LOAD_RDFIFO:
            io_load_rdfifo(SETUPDAT[2]);
            return 0;
        default:
            return 1;
    }
}

void handle_setupdata(void)
{
    switch (SETUPDAT[1]) {
        case GET_STATUS:
            break;
        case CLEAR_FEATURE:
            handle_clear_feature();
            break;
        case SET_FEATURE:
            break;
        case GET_DESCRIPTOR:
            handle_get_descriptor();
            break;
        case GET_CONFIGURATION:
            EP0BUF[0] = 1;
            EP0BCH = 0;
            EP0BCL = 1;
            break;
        case SET_CONFIGURATION:
        case SET_INTERFACE:
        case GET_INTERFACE:
            break;
        default:
            if (handle_vendor_command())
                stall_ep0();
    }

    EP0CS |= bmHSNAK;
}
