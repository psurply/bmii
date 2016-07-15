#ifndef FX2MACROS_H
#define FX2MACROS_H

#define MSB(addr) (BYTE)(((WORD)(addr) >> 8) & 0xff)
#define LSB(addr) (BYTE)((WORD)(addr) & 0xff)
#define MAKEWORD(msb,lsb) (((WORD)msb << 8) | lsb)

#endif /* FX2MACROS_H */
