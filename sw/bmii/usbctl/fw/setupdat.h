#ifndef SETUPDAT_H
#define SETUPDAT_H

typedef enum {
    GET_STATUS,
    CLEAR_FEATURE,
    // 0x02 is reserved
    SET_FEATURE=0x03,
    // 0x04 is reserved
    SET_ADDRESS=0x05, // this is handled by EZ-USB core unless RENUM=0
    GET_DESCRIPTOR,
    SET_DESCRIPTOR,
    GET_CONFIGURATION,
    SET_CONFIGURATION,
    GET_INTERFACE,
    SET_INTERFACE,
    SYNC_FRAME
} SETUP_DATA;

struct string_dscr {
    BYTE dsc_len;
    BYTE dsc_type;
    BYTE pstr;
};

#define DSCR_DEVICE_TYPE    1
#define DSCR_CONFIG_TYPE    2
#define DSCR_STRING_TYPE    3
#define DSCR_DEVQUAL_TYPE   6

void handle_setupdata(void);

#endif /* SETUPDAT_H */
