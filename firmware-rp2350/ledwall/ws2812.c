/*
 * Copyright (c) 2022-2024, Erich Styger
 *
 * SPDX-License-Identifier: BSD-3-Clause
 * 
 * https://mcuoneclipse.com/2023/04/02/rp2040-with-pio-and-dma-to-address-ws2812b-leds/
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "hardware/pio.h"
#include "hardware/clocks.h"
#include "ws2812.pio.h" /* note: if not found, touch the CMakeLists.txt in this folder and run build again */
#include "ws2812.h"
#include "pico/stdlib.h"
#include "hardware/dma.h"
#include "hardware/irq.h"

/* timing (+/-150ns):
 * 0: 400ns high, followed by 850ns low
 * 1: 850ns low,  followed by 400ns low
 */
static unsigned int WS2812_sm = 0; /* state machine index. \todo should find a free SM */

#define DMA_CHANNEL         (0) /* bit plane content DMA channel */
#define DMA_CHANNEL_MASK    (1u<<DMA_CHANNEL)

static void dma_init(PIO pio, unsigned int sm) {
  dma_claim_mask(DMA_CHANNEL_MASK); /* check that the DMA channel we want is available */
  dma_channel_config channel_config = dma_channel_get_default_config(DMA_CHANNEL); /* get default configuration */
  channel_config_set_dreq(&channel_config, pio_get_dreq(pio, sm, true)); /* configure data request. true: sending data to the PIO state machine */
  channel_config_set_transfer_data_size(&channel_config, DMA_SIZE_32); /* data transfer size is 32 bits */
  channel_config_set_read_increment(&channel_config, true); /* each read of the data will increase the read pointer */
  uint xfer_count = dma_encode_transfer_count(NEOC_NOF_LEDS_IN_LANE*2*NEOC_NOF_COLORS)
  dma_channel_configure(DMA_CHANNEL,
                        &channel_config,
                        &pio->txf[sm], /* write address: write to PIO FIFO */
                        NULL, /* don't provide a read address yet */
                        xfer_count, /* number of transfers */
                        false); /* don't start yet */
  //irq_set_exclusive_handler(DMA_IRQ_0, dma_complete_handler); /* after DMA all data, raise an interrupt */
  dma_channel_set_irq0_enabled(DMA_CHANNEL, true); /* map DMA channel to interrupt */
  irq_set_enabled(DMA_IRQ_0, true); /* enable interrupt */
}

// data is transferred by the DMA in 32-bit chunks; make sure our LED data is fitted to the *end*
// the PIO will blindly spew out all 32-bits of data, so we want to end on LED 0's actual value.
int WS2812_Transfer(uint32_t address) {
  dma_channel_set_read_addr(DMA_CHANNEL, (void*)address, true); /* trigger DMA transfer */
  return 0; /* ok */
}

void WS2812_Init(void) {
  PIO pio = pio0; /* the PIO used */
  WS2812_sm = 0; /* state machine used */

  uint offset = pio_add_program(pio, &ws2812_program);
  ws2812_program_init(pio, WS2812_sm, offset, NEOC_PIN_START, 800000); /* initialize it for 800 kHz */
  dma_init(pio, WS2812_sm);
}
