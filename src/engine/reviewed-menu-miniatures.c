#include <stdint.h>

/* Private menu-only transport. This padding is inside the existing reserved
 * palette pages, above the compiled Live object and below the party-heap root.
 * The builder authenticates both boundaries. It never changes a save record. */
typedef struct { uint16_t tile; uint8_t owner, unused; } Entry;
typedef struct { uint32_t magic, failures; Entry entries[64]; } State;
static State *const state=(State *)0x0203ed00u;
_Static_assert(sizeof(State)==264,"bounded miniature upload map");
#define MAGIC 0x4d494e49u
extern const uint32_t ffta_reviewed_menu_container;
extern const uint8_t ffta_reviewed_menu_groups[10];

void ffta_reviewed_menu_reset(void) {
    state->magic=MAGIC;state->failures=0;
    for(unsigned i=0;i<64;++i)state->entries[i].owner=255;
}

void ffta_reviewed_menu_upload(unsigned index,unsigned destination,unsigned container) {
    if(state->magic!=MAGIC)ffta_reviewed_menu_reset();
    if(container!=ffta_reviewed_menu_container || destination<0x06010000u ||
       destination>0x06017d80u || (destination&31u)) {++state->failures;return;}
    unsigned tile=(destination-0x06010000u)/32u,free=64;
    /* All three authenticated miniature upload paths copy exactly20 tiles.
     * Original figures must retire an earlier generated owner at that range. */
    for(unsigned i=0;i<64;++i) {
        Entry *e=&state->entries[i];
        if(e->owner<3 && tile<e->tile+20u && e->tile<tile+20u)e->owner=255;
        if(e->owner==255 && free==64)free=i;
    }
    if(index<54 || index>=64)return;
    if(free==64) {++state->failures;return;}
    state->entries[free].tile=(uint16_t)tile;
    state->entries[free].owner=ffta_reviewed_menu_groups[index-54];
}

unsigned ffta_reviewed_menu_bank(unsigned layout,unsigned tile,unsigned native) {
    if(state->magic!=MAGIC || layout!=0x0894eae4u || native>=6)return native;
    for(unsigned i=0;i<64;++i)if(state->entries[i].owner<3 && state->entries[i].tile==tile)
        return (native<3?9u:13u)+state->entries[i].owner;
    return native;
}

void ffta_reviewed_menu_draw(const uint8_t *descriptor,const void *layout) {
    unsigned tile=descriptor[22]|((unsigned)descriptor[23]<<8);
    unsigned bank=ffta_reviewed_menu_bank((unsigned)layout,tile,descriptor[18]);
    typedef void (*Draw)(const void *,unsigned,unsigned,unsigned,unsigned,unsigned,
                        unsigned,unsigned,unsigned,unsigned,unsigned);
    ((Draw)0x08001f35u)(layout,descriptor[16],descriptor[17],descriptor[20],
        0,0,0,0,tile,descriptor[19],bank);
}
