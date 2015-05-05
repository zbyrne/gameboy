#ifndef MEM_H
#define MEM_H
/* Memory Map
Interrupt Enable Register
-- 0xFFFF
Internal RAM
-- 0xFF80
Empty
-- 0xFF4C
I/O ports
-- 0xFF00
Empty
-- 0xFEA0
Sprite Attrib Memory
-- 0xFE00
Dup of 8k internal RAM
-- 0xE000
8k internal RAM
-- 0xC000
8k switchable RAM
-- 0xA000
8k video RAM
-- 0x8000
16k switchable ROM
-- 0x4000
16k ROM
-- 0x0000

** Lower 32k in cartridge
 */

/* CPU interface */
uint8_t mem_read(uint16_t);
void mem_write(uint16_t, uint8_t);
#endif
