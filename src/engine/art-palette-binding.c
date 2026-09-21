#include "art-palette-binding.h"
_Static_assert(sizeof(FFTA_ArtBinding) == 252, "binding layout");
_Static_assert(sizeof(FFTA_ArtBindings) == 284*FFTA_ART_HISTORY_SLOTS+12, "bindings layout");

static void copy_colors(FFTA_ArtBindings *state, unsigned owner) {
    unsigned i;
    for (i = 0; i < 16; ++i) state->colors[owner * 16 + i] = state->entry[owner].fade.colors[i];
}

void ffta_art_bindings_reset(FFTA_ArtBindings *state, const uint16_t *base) {
    unsigned i;
    for (i = 0; i < FFTA_ART_HISTORY_SLOTS; ++i) {
        FFTA_ArtBinding *entry = &state->entry[i];
        entry->bank = 255;
        entry->task = 0;
#if FFTA_ART_HISTORY_SLOTS > FFTA_ART_CLASS_COUNT
        static const uint16_t empty[16]={0};
        const uint16_t *initial=i<FFTA_ART_CLASS_COUNT?base+i*16:empty;
#else
        const uint16_t *initial=base+i*16;
#endif
        ffta_art_fade_start(&entry->fade, initial, initial, 0);
        entry->fade.remaining = 0;
        copy_colors(state, i);
    }
    state->started = state->completed = state->unsupported = 0;
}

void ffta_art_binding_observe(FFTA_ArtBindings *state, unsigned owner, unsigned bank,
                              const uint16_t *native, const uint16_t *base) {
    ffta_art_binding_observe_colors(state, owner, bank, native, base + owner * 16);
}

void ffta_art_binding_observe_colors(FFTA_ArtBindings *state, unsigned owner, unsigned bank,
                                     const uint16_t *native, const uint16_t colors[16]) {
    unsigned i;
    FFTA_ArtBinding *entry = &state->entry[owner];
    if (entry->bank == bank) return;
    entry->bank = bank;
    entry->task = 0;
    for (i = 0; i < 16; ++i) entry->native_base[i] = native[bank * 16 + i];
    ffta_art_fade_start(&entry->fade, colors, colors, 0);
    entry->fade.remaining = 0;
    copy_colors(state, owner);
}

static unsigned overlaps(const FFTA_ArtBinding *entry, unsigned first, unsigned last) {
    unsigned index = 256 + entry->bank * 16;
    return entry->bank < 16 && first <= index + 15 && last >= index;
}

void ffta_art_binding_invalidate(FFTA_ArtBindings *state, unsigned first, unsigned last,
                                 uint32_t task, unsigned recognized) {
    unsigned i;
    for (i = 0; i < FFTA_ART_HISTORY_SLOTS; ++i) {
        FFTA_ArtBinding *entry = &state->entry[i];
        if (entry->task == task || overlaps(entry, first, last)) entry->task = 0;
        if (!recognized && overlaps(entry, first, last)) ++state->unsupported;
    }
}

void ffta_art_binding_start(FFTA_ArtBindings *state, unsigned first, unsigned last,
                            unsigned duration, uint32_t task, unsigned kind,
                            const uint16_t *native_target, const uint16_t *base) {
    ffta_art_binding_start_mapped(state, first, last, duration, task, kind,
                                   native_target, base, 0);
}

static unsigned map_table(const FFTA_ArtBinding *entry,const uint16_t *values,
    uint16_t target[16],const uint16_t *base,const uint8_t *mapping,unsigned owner,unsigned lo) {
    unsigned i,uniform=1,original=1;
    for(i=lo;i<16;++i) {
        if(values[i-lo]!=values[0])uniform=0;
        if(values[i-lo]!=entry->native_base[i])original=0;
    }
    if(!uniform && !original)return 0;
    for(i=0;i<16;++i) {
        if(i<lo) {target[i]=entry->fade.colors[i];continue;}
        unsigned source=mapping?mapping[owner]>>4:owner;
        unsigned scale=mapping?mapping[FFTA_ART_HISTORY_SLOTS+owner]:32;
#if FFTA_ART_HISTORY_SLOTS > FFTA_ART_CLASS_COUNT
        if(source>=FFTA_ART_CLASS_COUNT)return 0;
#endif
        target[i]=original?ffta_art_scale_color(base[source*16+i],scale):values[0];
    }
    return 1;
}

void ffta_art_binding_start_mapped(FFTA_ArtBindings *state, unsigned first, unsigned last,
                            unsigned duration, uint32_t task, unsigned kind,
                            const uint16_t *native_target, const uint16_t *base,
                            const uint8_t *mapping) {
    unsigned owner, i;
    for (owner = 0; owner < FFTA_ART_HISTORY_SLOTS; ++owner) {
        FFTA_ArtBinding *entry = &state->entry[owner];
        uint16_t target[16];
        unsigned index = 256 + entry->bank * 16;
        if (!overlaps(entry, first, last)) continue;
        entry->task = 0;
        if (first > index+1 || last < index + 15 || duration > 255 || !task) {
            ++state->unsupported;
            continue;
        }
        if (kind == 3) {
            unsigned lo=first>index?1:0;
            if(!map_table(entry,native_target+index+lo-first,target,base,mapping,owner,lo)) {
                ++state->unsupported;continue;
            }
        } else {
            for (i = 0; i < 16; ++i) target[i] = index+i<first?entry->fade.colors[i]:kind == 1 ? 0 : 0x7fff;
        }
        ffta_art_fade_start(&entry->fade, entry->fade.colors, target, duration);
        entry->task = task;
        ++state->started;
    }
}

void ffta_art_binding_transform(FFTA_ArtBindings *state, unsigned first, unsigned last,
    unsigned duration, uint32_t task, unsigned kind, unsigned red, unsigned green,
    unsigned blue) {
    unsigned owner, i;
    red &= 65535; green &= 65535; blue &= 65535;
    for (owner = 0; owner < FFTA_ART_HISTORY_SLOTS; ++owner) {
        FFTA_ArtBinding *entry = &state->entry[owner];
        unsigned index = 256 + entry->bank * 16;
        uint16_t target[16];
        if (!overlaps(entry, first, last)) continue;
        entry->task = 0;
        if (first > index+1 || last < index + 15 || duration > 255 || !task ||
            kind < 4 || kind > 12) { ++state->unsupported; continue; }
        for (i = 0; i < 16; ++i) {
            if(index+i<first) {target[i]=entry->fade.colors[i];continue;}
            if(kind==11 || kind==12) {
                /* Native14731C/1473E4 raise each source channel to at least3
                 * before computing the target AND constructing interpolation. */
                unsigned c=entry->fade.colors[i],r=c&31,g=(c>>5)&31,b=(c>>10)&31;
                entry->fade.colors[i]=(r<3?3:r)|((g<3?3:g)<<5)|((b<3?3:b)<<10);
            }
            if (kind == 4)
                target[i] = ((unsigned (*)(unsigned))0x081477ddu)(entry->fade.colors[i]);
            else if (kind == 7)
                target[i] = (uint16_t)(red | (green << 5) | (blue << 10));
            else if(kind==8)
                target[i]=((unsigned (*)(unsigned,unsigned,unsigned,unsigned))
                    0x08147831u)(entry->fade.colors[i],red,green,blue);
            else if(kind==9 || kind==10)
                target[i]=((unsigned (*)(unsigned,unsigned))
                    (kind==9?0x081478ddu:0x08147959u))(entry->fade.colors[i],red);
            else if(kind==11 || kind==12)
                target[i]=((unsigned (*)(unsigned,unsigned,unsigned,unsigned))
                    0x08148385u)(entry->fade.colors[i],red,green,blue);
            else
                target[i] = ((unsigned (*)(unsigned,unsigned,unsigned,unsigned))
                    0x081483edu)(entry->fade.colors[i], red, green, blue);
        }
        ffta_art_fade_start(&entry->fade, entry->fade.colors, target, duration);
        if(kind==11 || kind==12)copy_colors(state,owner);
        entry->task = task;
        ++state->started;
    }
}

void ffta_art_binding_table_transform(FFTA_ArtBindings *state,unsigned first,unsigned last,
    unsigned duration,uint32_t task,unsigned kind,const uint16_t *table,
    unsigned red,unsigned green,unsigned blue,const uint16_t *base,const uint8_t *mapping) {
    unsigned owner,i;
    for(owner=0;owner<FFTA_ART_HISTORY_SLOTS;++owner) {
        FFTA_ArtBinding *entry=&state->entry[owner];
        unsigned index=256+entry->bank*16;
        uint16_t target[16];
        if(!overlaps(entry,first,last))continue;
        entry->task=0;
        unsigned lo=first>index?1:0;
        if(first>index+1 || last<index+15 || duration>255 || !task ||
           (kind!=13 && kind!=14) ||
           !map_table(entry,table+index+lo-first,target,base,mapping,owner,lo)) {
            ++state->unsupported;continue;
        }
        for(i=0;i<16;++i) {
            if(i<lo)continue;
            unsigned color=target[i];
            if(kind==13) {
                unsigned r=color&31,g=(color>>5)&31,b=(color>>10)&31;
                color=(r<3?3:r)|((g<3?3:g)<<5)|((b<3?3:b)<<10);
                target[i]=((unsigned (*)(unsigned,unsigned,unsigned,unsigned))
                    0x08148385u)(color,red,green,blue);
            } else target[i]=((unsigned (*)(unsigned,unsigned,unsigned,unsigned))
                    0x08147831u)(color,red,green,blue);
        }
        ffta_art_fade_start(&entry->fade,entry->fade.colors,target,duration);
        entry->task=task;++state->started;
    }
}

void ffta_art_binding_tick(FFTA_ArtBindings *state, uint32_t task, unsigned before,
                           unsigned after, unsigned alive, unsigned flags) {
    ffta_art_binding_tick_range(state,task,before,after,alive,flags,0,511);
}

void ffta_art_binding_rotate(FFTA_ArtBindings *state,unsigned first,unsigned last,
    unsigned right,unsigned steps,unsigned feed,unsigned value) {
    unsigned owner;
    for(owner=0;owner<FFTA_ART_HISTORY_SLOTS;++owner) {
        FFTA_ArtBinding *entry=&state->entry[owner];
        FFTA_ArtFade *f=&entry->fade;
        unsigned index=256+entry->bank*16,lo,hi;
        if(!overlaps(entry,first,last))continue;
        /* Cross-bank transport needs a source identity for every participating
         * color. Do not silently reinterpret unrelated native banks. */
        if(first<index || last>index+15) {++state->unsupported;continue;}
        lo=first-index;hi=last-index;
#ifdef FFTA_ART_FAST_ROTATION
        if(feed) {
            unsigned width=hi-lo+1,amount=steps<width?steps:width,i;
            for(i=0;i<width;++i) {
                unsigned to=right?hi-i:lo+i;
                f->colors[to]=i+amount<width?f->colors[right?to-amount:to+amount]:value;
            }
        } else {
            /* Rotate each color and its interpolation state once, regardless
             * of the native task's step count. No division runtime is needed. */
            unsigned width=hi-lo+1,amount=0,bit,groups,a,b,start;
            for(bit=32;bit;--bit) {
                amount=(amount<<1)|((steps>>(bit-1))&1);
                if(amount>=width)amount-=width;
            }
            if(amount) {
                a=width;b=amount;
                while(a!=b) {if(a>b)a-=b;else b-=a;}
                groups=a;
                for(start=lo;start<lo+groups;++start) {
                    unsigned i=start,c;
                    uint16_t color=f->colors[i],target=f->target[i];
                    int16_t error[3];int8_t delta[3];
                    for(c=0;c<3;++c) {error[c]=f->error[i][c];delta[c]=f->delta[i][c];}
                    for(;;) {
                        unsigned from;
                        if(right)from=i<lo+amount?i+width-amount:i-amount;
                        else from=i+amount>hi?i+amount-width:i+amount;
                        if(from==start)break;
                        f->colors[i]=f->colors[from];f->target[i]=f->target[from];
                        for(c=0;c<3;++c) {f->error[i][c]=f->error[from][c];f->delta[i][c]=f->delta[from][c];}
                        i=from;
                    }
                    f->colors[i]=color;f->target[i]=target;
                    for(c=0;c<3;++c) {f->error[i][c]=error[c];f->delta[i][c]=delta[c];}
                }
            }
        }
#else
        unsigned step;
        for(step=0;step<steps;++step) {
            unsigned edge=right?hi:lo,i=edge,c;
            uint16_t color=f->colors[edge],target=f->target[edge];
            int16_t error[3];int8_t delta[3];
            for(c=0;c<3;++c) {error[c]=f->error[edge][c];delta[c]=f->delta[edge][c];}
            while(i!=(right?lo:hi)) {
                unsigned from=right?i-1:i+1;
                f->colors[i]=f->colors[from];
                if(!feed) {
                    f->target[i]=f->target[from];
                    for(c=0;c<3;++c) {f->error[i][c]=f->error[from][c];f->delta[i][c]=f->delta[from][c];}
                }
                i=from;
            }
            f->colors[i]=feed?value:color;
            if(!feed) {
                f->target[i]=target;
                for(c=0;c<3;++c) {f->error[i][c]=error[c];f->delta[i][c]=delta[c];}
            }
        }
#endif
        copy_colors(state,owner);
    }
}

void ffta_art_binding_tick_range(FFTA_ArtBindings *state,uint32_t task,unsigned before,
    unsigned after,unsigned alive,unsigned flags,unsigned first,unsigned last) {
    unsigned i;
    for (i = 0; i < FFTA_ART_HISTORY_SLOTS; ++i) {
        FFTA_ArtBinding *entry = &state->entry[i];
        unsigned color,mask=0,index=256+entry->bank*16;
        if (entry->task != task) continue;
        for(color=0;color<16;++color)
            if(index+color>=first && index+color<=last)mask|=1u<<color;
        if(!mask) {entry->task=0;continue;}
        if (alive && before == after) continue; /* Native blink cadence skipped. */
        if (entry->fade.remaining != before || (alive && after + 1 != before) || (!alive && before != 1)) {
            ++state->unsupported;
            entry->task = 0;
            continue;
        }
        ffta_art_fade_step_masked(&entry->fade, flags & 16,mask);
        copy_colors(state, i);
        if (!alive) { entry->task = 0; ++state->completed; }
    }
}
