#include "fx2ints.h"
#include "gpif.h"
#include "intr.h"
#include "led.h"

#define EVENT_QUEUE_SIZE    32

struct event_queue {
    BYTE begin;
    BYTE end;
    BYTE size;
    BYTE content[EVENT_QUEUE_SIZE];
};

static volatile __bit mutex;
static struct event_queue eq;

static inline void event_queue_lock(void)
{
    for (;;) {
        if (mutex) {
            mutex = 0;
            return;
        }
    }
}

static inline void event_queue_unlock(void)
{
    mutex = 1;
}

static inline void event_queue_init(void)
{
    mutex = 1;
    eq.begin = 0;
    eq.end = 0;
}

static inline void event_queue_enqueue(BYTE value)
{
    event_queue_lock();

    if (eq.size >= EVENT_QUEUE_SIZE) {
        EX0 = 0;
        goto error_full;
    }

    eq.content[eq.end] = value;
    eq.end = (eq.end + 1) % EVENT_QUEUE_SIZE;
    eq.size += 1;

error_full:
    event_queue_unlock();
}

BYTE event_queue_dequeue()
{
    BYTE value;
    event_queue_lock();

    if (eq.size == 0) {
        value = EVENT_QUEUE_EMPTY;
        goto error_empty;

    }

    value = eq.content[eq.begin];
    eq.begin = (eq.begin + 1) % EVENT_QUEUE_SIZE;
    eq.size -= 1;

error_empty:
    event_queue_unlock();
    return value;
}


void int0_init(void)
{
    event_queue_init();

    EX0 = 1;
    PORTACFG |= bmINT0;
}

void int0_isr(void) __interrupt IE0_ISR
{
    BYTE dummy;

    gpif_enable();
    wait_gpif_done();
    dummy = XGPIFSGLDATLX;

    wait_gpif_done();
    event_queue_enqueue(XGPIFSGLDATLNOX);

    IE0 = 0;
}
