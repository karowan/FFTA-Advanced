#include "battle-workspace.h"
extern void ffta_manager_register(uint8_t *);
extern void ffta_copy_owner_free(void *);
#define MAGIC 0x31535742u
#define POOL_BYTES 0x2660u
typedef struct { unsigned magic,self;uint8_t *pool,*heap; } Header;
typedef struct { unsigned magic,owner,self; } Pool;
static unsigned valid(const uint8_t *p,unsigned size) {
 uintptr_t v=(uintptr_t)p;
 return !(v&3u) && v>=0x0200000cu && v<=0x0203f000u-size;
}
static unsigned allocated(const uint8_t *p,unsigned size) {
 if(!valid(p,size))return 0;
 const uint16_t *native=(const uint16_t *)(p-12);
 unsigned bytes=4u*native[3];
 /* Native6EC0 absorbs an unsplittable remainder of zero..three words.
  * The owned payload can therefore exceed the requested size by12 bytes. */
 return native[2]==0x616c && bytes>=size+12u && bytes<=size+24u &&
  valid(p,bytes-12u);
}
static Header *header(void) {
 uint8_t *m=ffta_owned_battle_manager();
 if(!allocated(m,FFTA_WORKSPACE_MANAGER_BYTES))return 0;
 Header *h=(Header *)(m+0x430);
 return h->magic==MAGIC && h->self==(unsigned)m ? h:0;
}
static uint8_t *pool(Header *h) {
 if(!h || h->heap!=*(uint8_t **)0x0200f434u || !allocated(h->pool,POOL_BYTES))return 0;
 const Pool *p=(const Pool *)h->pool;
 return p->magic==MAGIC && p->owner==h->self && p->self==(unsigned)p ? h->pool:0;
}
void ffta_battle_workspace_register(uint8_t *manager) {
 if(!allocated(manager,FFTA_WORKSPACE_MANAGER_BYTES))return;
 ffta_manager_register(manager);
 Header *h=(Header *)(manager+0x430);
 h->self=(unsigned)manager;h->pool=0;h->heap=0;h->magic=MAGIC;
}
unsigned ffta_additional_workspace_prepare(void) {
 Header *h=header();if(!h)return 0;
 if(pool(h))return 1;
 /* Only explicit snapshot creation allocates. Pure getters never repair a
  * forged/stale header or claim somebody else's allocation. */
 if(h->pool)return 0;
 uint8_t *heap=*(uint8_t **)0x0200f434u;
 if(!valid(heap,20))return 0;
 uint8_t *p=((uint8_t *(*)(unsigned))0x08022841u)(POOL_BYTES);
 if(!p)return 0;
 for(unsigned i=0;i<POOL_BYTES;i++)p[i]=0;
 Pool *owner=(Pool *)p;owner->owner=h->self;owner->self=(unsigned)p;owner->magic=MAGIC;
 h->heap=heap;h->pool=p;return 1;
}
void *ffta_battle_workspace(unsigned offset) {
 uint8_t *p=pool(header());
 if(!p || (offset!=FFTA_WORKSPACE_GEOMANCER && offset!=FFTA_WORKSPACE_RESULTS && offset!=FFTA_WORKSPACE_EXTRA &&
           offset!=FFTA_WORKSPACE_EXTENSION && offset!=FFTA_WORKSPACE_DOUBLECAST &&
           offset!=FFTA_WORKSPACE_FIGHT_LAWS))return 0;
 return p+offset;
}
void ffta_additional_workspace_retire(void *allocation) {
 extern void ffta_geo_renderer_free(void *);
 ffta_geo_renderer_free(allocation);
 Header *h=header();if(!h)return;
 uint8_t *p=pool(h);
 extern void ffta_myk_doublecast_retire(void);
 if(p && allocation==p) { ffta_myk_doublecast_retire();h->pool=0;h->heap=0;return; }
 uintptr_t a=(uintptr_t)allocation;
 if(!valid(allocation,12))return;
 const uint16_t *native=(const uint16_t *)(a-12);
 unsigned bytes=4u*native[3];
 if(native[2]!=0x616c || bytes<12 || bytes-12>0x0203f000u-a ||
    a>h->self || a+bytes-12<h->self+FFTA_WORKSPACE_MANAGER_BYTES)return;
 /* Clearing the owner's pointer before native free makes recursive free
  * observation inert. A parent-allocation free also contains this manager. */
 ffta_myk_doublecast_retire();
 uint8_t *heap=h->heap;void *manager=(void *)h->self;h->pool=0;h->heap=0;
 if(p)((void (*)(void *,void *))0x08007171u)(heap,p);
 if(allocation!=manager)ffta_copy_owner_free(manager);
}
