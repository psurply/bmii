#ifndef IO_H
#define IO_H

#include "fx2types.h"

void io_init(void);
void io_select_reg(BYTE addr);
void io_load_rdfifo(BYTE addr);
void io_write_data(void);

#endif /* IO_H */
