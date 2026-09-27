#include "chemist-progression.h"
#include "battle-workspace.h"
#include "job-state.h"

/* A turn-end explosion is not another player action. Its bounded recipient
 * list belongs to the current native battle allocation. The original periodic
 * renderer performs HP application, numbers, hit poses and KO completion.
 * No additional MP, turn, reaction queue, or outgoing Spotter event is created.
 * This component must be accepted through native playback before release. */
typedef struct {uint8_t *wrapper,*unit;int damage;} Recipient;
typedef struct {
 unsigned magic,self;uint8_t *battle,*carrier;
 unsigned count,next,started;
 Recipient recipients[36];
 uint8_t *saved_periodic,*trigger_owner;
} Explosion;
_Static_assert(sizeof(Explosion)<=512,"Delayed effect pool reservation");
#define MAGIC 0x31465343u
static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static unsigned alive(const uint8_t *u){return u && half(u+0x18) && !(u[0xe8]&64u);}
static void sh(uint8_t *p,unsigned n){p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);}
static unsigned absolute(int n){return (unsigned)(n<0?-n:n);}
static Explosion *slot(void){return ffta_battle_workspace(FFTA_WORKSPACE_DELAYED);}
static void clear(Explosion *p){if(p)for(unsigned i=0;i<sizeof(*p);i++)((uint8_t *)p)[i]=0;}
extern int ffta_integrated_original_exposed_preview(const uint8_t *,const uint8_t *,unsigned,unsigned,unsigned,unsigned);

static int elemental_damage(const uint8_t *caster,const uint8_t *target,unsigned action){
 if(!alive(caster)||!alive(target))return 0;
 /* Native elemental formula retains immunity/absorption and actual defenses.
  * It is evaluated as the reserved delayed command, not the lighter attach
  * hit. Preserve the ordinary query bank and RNG used by the enclosing turn. */
 uint8_t saved[0x94];volatile uint8_t *bank=(volatile uint8_t *)0x0200f390u;
 for(unsigned i=0;i<sizeof(saved);i++)saved[i]=bank[i];
 volatile unsigned *rng=(volatile unsigned *)0x030034b0u;unsigned old=*rng;
 int damage=ffta_integrated_original_exposed_preview(caster,target,action,0,0,2);
 *rng=old;for(unsigned i=0;i<sizeof(saved);i++)bank[i]=saved[i];
 if(damage>999)damage=999;
 if(damage<0){unsigned hp=half(target+0x18),max=half(target+0x1a),missing=max>hp?max-hp:0;if((unsigned)(-damage)>missing)damage=-(int)missing;}
 return damage;
}
int ffta_cp_fuse_damage(const uint8_t *caster,const uint8_t *target){return elemental_damage(caster,target,463);}
void ffta_cp_fuse_prepare(uint8_t *unit,uint8_t *battle){
 Explosion *p=slot();if(!p || p->magic)return;
 if(battle!=(uint8_t *)0x0200f4e8u || !unit)return;
 uint8_t *current=*(uint8_t **)(battle+4);
 if(!current || *(uint8_t **)current!=unit)return;
 uint8_t *s=ffta_job_state(unit);if(!s || !(s[23]&192u))return;
 unsigned x=half(current+8)>>5,y=half(current+12)>>5;
 ffta_cp_position_changed(unit,x,y);
 if(!alive(unit) || !(s[23]&192u))return;
 if((s[23]>>6)==2){s[23]=(uint8_t)((s[23]&63u)|64u);return;}
 if((s[23]>>6)!=1)return;
 uint8_t *wrappers[36],*caster=0;
 unsigned n=((unsigned (*)(void *,uint8_t **))0x08099cddu)(ffta_owned_battle_manager(),wrappers);
 if(n>36)return;
 for(unsigned i=0;i<n;i++){
  uint8_t *u=*(uint8_t **)wrappers[i];
  if(ffta_job_origin(u)==s[24])caster=u;
 }
 /* Consume before playback so copy/lifecycle callbacks cannot duplicate it.
  * A departed, KO or Petrified owner cannot lend a fabricated caster. */
 s[23]&=63u;s[24]=0;
 if(!alive(caster))return;
 clear(p);p->self=(unsigned)p;p->battle=battle;p->carrier=unit;
 int height=((int (*)(unsigned,unsigned))0x0801cc19u)(x,y);
 for(unsigned i=0;i<n;i++){
  uint8_t *w=wrappers[i],*u=*(uint8_t **)w;
  unsigned tx=half(w+8)>>5,ty=half(w+12)>>5;
  if(!alive(u) || tx>=16 || ty>=16 || absolute((int)x-(int)tx)+absolute((int)y-(int)ty)>1)continue;
  int h=((int (*)(unsigned,unsigned))0x0801cc19u)(tx,ty);
  if(absolute(h-height)>2)continue;
  int damage=ffta_cp_fuse_damage(caster,u);if(!damage)continue;
  Recipient *r=&p->recipients[p->count++];r->wrapper=w;r->unit=u;r->damage=damage;
 }
 p->magic=MAGIC;
}
unsigned ffta_cp_fuse_next(uint8_t *battle){
 Explosion *p=slot();
 if(!p || p->magic!=MAGIC || p->self!=(unsigned)p || p->battle!=battle || p->count>36)return 0;
 if(!p->started && !alive(p->carrier)){clear(p);return 0;}
 while(p->next<p->count){
  Recipient *r=&p->recipients[p->next++];
  if(*(uint8_t **)r->wrapper!=r->unit || !alive(r->unit))continue;
  int damage=r->damage;
  if(damage<0){unsigned hp=half(r->unit+0x18),max=half(r->unit+0x1a),missing=max>hp?max-hp:0;if((unsigned)(-damage)>missing)damage=-(int)missing;}
  if(!damage)continue;
  uint8_t *c=(uint8_t *)0x0200f770u;
  for(unsigned i=0;i<0x114;i++)c[i]=0;
  *(uint8_t **)c=r->wrapper;sh(c+0x5e,(unsigned)damage);
  sh(c+0xcc,42);sh(c+0xce,2);sh(c+0xd0,39);sh(c+0xd2,6);
  *(uint8_t **)(battle+0x5c)=c;p->started=1;return 1;
 }
 clear(p);return 0;
}

#define TRAP_MAGIC (MAGIC+1u)
void ffta_cp_trap_slow(uint8_t *caster,uint8_t *target){
 if(!alive(caster)||!alive(target))return;
 uint8_t saved[0x94];volatile uint8_t *bank=(volatile uint8_t *)0x0200f390u;
 for(unsigned i=0;i<sizeof(saved);i++)saved[i]=bank[i];
 uint8_t *c=(uint8_t *)0x0200f3f0u;
 for(unsigned i=0;i<0x34;i++)c[i]=0;
 *(uint8_t **)c=caster;*(uint8_t **)(c+4)=target;*(uint8_t **)(c+8)=target;
 sh(c+12,464);
 const uint8_t *descriptors=*(const uint8_t *const *)0x0812f348u;
 *(const uint8_t **)(c+0x30)=descriptors+104u*4u;c[0x28]=1;
 /* The original Slow descriptor's compatibility, resistance, ordinary
  * accuracy and hit roll run unchanged. Its callback handles Astra and the
  * native Slow/Haste timer relationship. No guaranteed custom status bit. */
 unsigned chance=((unsigned (*)(void))0x08131379u)();
 if(((unsigned (*)(unsigned))0x0812f1ddu)(chance))
  ((void (*)(uint8_t *))0x08132b45u)(c);
 for(unsigned i=0;i<sizeof(saved);i++)bank[i]=saved[i];
}
extern unsigned ffta_cp_original_battle_tick(uint8_t *,unsigned,unsigned);
unsigned ffta_cp_battle_tick(uint8_t *battle,unsigned pressed,unsigned repeat){
 Explosion *p=slot();
 if(battle!=(uint8_t *)0x0200f4e8u || !p)
  return ffta_cp_original_battle_tick(battle,pressed,repeat);
 if(p->magic==TRAP_MAGIC && p->self==(unsigned)p && p->battle==battle){
  uint8_t *c=(uint8_t *)0x0200f770u;
  if(((unsigned (*)(uint8_t *))0x0809f9c1u)(c))return 1;
  uint8_t *w=p->recipients[0].wrapper,*u=p->recipients[0].unit;
  if(*(uint8_t **)w==u){
   if(alive(u))ffta_cp_trap_slow(p->trigger_owner,u);
   else {
    /* Stop a native walking route on the reached tile after lethal entry.
     * The original controller's completed state28 owns its cleanup. */
    uint8_t *walk=*(uint8_t **)(battle+0x44);
    if(walk && *(uint8_t **)walk==w)sh(walk+0xdc,28);
   }
   ((void (*)(uint8_t *))0x08098131u)(w);
  }
  *(uint8_t **)(battle+0x5c)=p->saved_periodic;clear(p);
  return 1;
 }
 /* A placed tile was empty. Test displayed tile centers before the next
  * native controller step, so walking, jumps, knockback and Springboard all
  * use the tile actually reached. Do not interrupt another periodic effect. */
 const uint8_t *bank=ffta_job_state((uint8_t *)0x02000080u);unsigned any=0;
 if(bank)for(unsigned i=0;i<36;i++)any|=bank[i*FFTA_JOB_RECORD_BYTES+23]&248u;
 if(any && half(battle+0xdc)>=5){
  uint8_t *wrappers[36];unsigned n=((unsigned (*)(void *,uint8_t **))0x08099cddu)(ffta_owned_battle_manager(),wrappers);
  if(n<=36)for(unsigned i=0;i<n;i++){
   uint8_t *w=wrappers[i],*u=*(uint8_t **)w;
   unsigned px=half(w+8),py=half(w+12),x=px>>5,y=py>>5;
   if(!alive(u)||x>=16||y>=16||(px&31u)!=16||(py&31u)!=16)continue;
   ffta_cp_position_changed(u,x,y);
   /* Crossing a square in mid-jump is not entering it. The wrapper's
    * vertical coordinate uses sixteenths of the native tile-height unit. */
   if(half(w+10)!=(unsigned)((int (*)(unsigned,unsigned))0x0801cc19u)(x,y)*16u)continue;
   if(p->magic || *(void **)(battle+0x5c))continue;
   unsigned token=ffta_cp_trap_at(u,x,y);if(!token)continue;
   uint8_t *caster=0;
   for(unsigned j=0;j<n;j++){uint8_t *v=*(uint8_t **)wrappers[j];if(ffta_job_origin(v)==token)caster=v;}
   if(!alive(caster))continue;
   uint8_t *s=ffta_job_state(caster);s[23]&=199u;
   int damage=elemental_damage(caster,u,464);
   clear(p);p->magic=TRAP_MAGIC;p->self=(unsigned)p;p->battle=battle;
   p->trigger_owner=caster;p->recipients[0]=(Recipient){w,u,damage};
   p->saved_periodic=*(uint8_t **)(battle+0x5c);
   uint8_t *c=(uint8_t *)0x0200f770u;for(unsigned j=0;j<0x114;j++)c[j]=0;
   *(uint8_t **)c=w;sh(c+0x5e,(unsigned)damage);
   sh(c+0xcc,42);sh(c+0xce,2);sh(c+0xd0,39);sh(c+0xd2,6);
   *(uint8_t **)(battle+0x5c)=c;return 1;
  }
 }
 return ffta_cp_original_battle_tick(battle,pressed,repeat);
}
