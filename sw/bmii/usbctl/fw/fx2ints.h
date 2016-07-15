#ifndef FX2INTS_H
#define FX2INTS_H

typedef enum {
    IE0_ISR=0,
    TF0_ISR,
    IE1_ISR,
    TF1_ISR,
    TI_0_ISR,
    TF2_ISR,
    RESUME_ISR,
    TI_1_ISR,
    USBINT_ISR,
    I2CINT_ISR,
    IE4_ISR,
    IE5_ISR,
    IE6_ISR,
} FX2_ISR;

#endif /* FX2INTS_H */
