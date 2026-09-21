/* Private ARM leaves copied into bounded, temporary IWRAM stack storage.
 * No persistent cache: authenticate and publish the current native frame.
 * The build rejects relocations, external calls and excessive stack use. */
#include "art-frame-fast.h"
typedef uint32_t Word __attribute__((may_alias));

unsigned ffta_art_frame_owners_leaf(const FFTA_ArtOwnerFrame *f) {
 const uint8_t *iw=f->iwram;
 unsigned bank,other,front,ui,main,shown,offset,i,requested=0;
 const uint16_t *source,*hardware;
 const FFTA_ArtOwnerEntry *entries;
 union {uint32_t words[32];uint8_t bytes[128];} tags;
 uint16_t banks[10];
 if(iw[0x28]>1 || iw[0x2f58]>1)return 0;
 bank=iw[0x28]^1;other=iw[0x2f58]^1;
 if(f->owners->ready[bank]!=0x4152544fu)return 0;
 front=*(const Word *)(iw+0x2c50+bank*4);
 ui=*(const Word *)(iw+0x2f60+other*4);
 main=*(const Word *)(iw+0x20+bank*4);
 if(front>48 || ui>32 || main>128 ||
    *(const Word *)(iw+0x3168+other*4)>16)return 0;
 if(front+main>=128)ui=0;
 else if(ui>128-main-front)ui=128-main-front;
 offset=front+ui;shown=main;
 if(shown>128-offset)shown=128-offset;
 source=(const uint16_t *)(iw+0x30+bank*1024);
 hardware=f->hardware+offset*4;entries=f->owners->entries[bank];
 for(i=0;i<32;++i)tags.words[i]=0xffffffffu;
 for(i=0;i<10;++i)banks[i]=0;
 /* Fused validation/classification writes only local scratch. A mismatch
  * anywhere, including the last object, leaves BOTH outputs untouched. */
 for(i=0;i<shown;++i,source+=4,hardware+=4,++entries) {
  unsigned a=source[0],b=source[1],c=source[2],owner=entries->owner;
  if((hardware[0]^a)|(hardware[1]^b)|(hardware[2]^c))return 0;
  if(owner>=10 || !(f->enabled&(1u<<owner)))continue;
  if((entries->attributes[0]^a)|(entries->attributes[1]^b)|
     (entries->attributes[2]^c))continue;
  tags.bytes[offset+i]=owner;requested|=1u<<owner;
  banks[owner]|=1u<<(c>>12);
 }
 if(!((uintptr_t)f->tags&3))
  for(i=0;i<32;++i)((Word *)f->tags)[i]=tags.words[i];
 else for(i=0;i<128;++i)f->tags[i]=tags.bytes[i];
 if(f->banks)for(i=0;i<10;++i)f->banks[i]=banks[i];
 return requested;
}

void ffta_art_frame_publish_leaf(FFTA_ArtPaletteFrame *f,uint16_t *backup,
                                 unsigned count) {
 unsigned i,j;
 /* Caller already proved the complete plan; copies require word alignment.
  * Snapshot each allocated native bank before replacing its current colors. */
 for(i=0;i<f->custom_count;++i)if(f->plan->requested&(1u<<i)) {
  unsigned slot=f->plan->bank[i];
  Word *dest=(Word *)(f->palette+slot*16);
  Word *saved=(Word *)(backup+slot*16);
  const Word *custom=(const Word *)(f->custom+i*16);
  for(j=0;j<8;++j){saved[j]=dest[j];dest[j]=custom[j];}
 }
 for(i=0;i<count;++i) {
  unsigned owner;
  if(i+4<=count && !((uintptr_t)(f->owner+i)&3) &&
     *(const Word *)(f->owner+i)==0xffffffffu){i+=3;continue;}
  owner=f->owner[i];
  if(owner==255 || (f->oam[i*4]&0x300)==0x200)continue;
  f->oam[i*4+2]=(f->oam[i*4+2]&0xfff)|(f->plan->bank[owner]<<12);
 }
}

unsigned ffta_art_frame_native_owners_leaf(const FFTA_ArtOwnerFrame *f) {
 const uint8_t *iw=f->iwram;
 unsigned bank,other,front,ui,main,shown,offset,i,requested=0;
 const uint16_t *source;
 const FFTA_ArtOwnerEntry *entries;
 if(iw[0x28]>1 || iw[0x2f58]>1)return 0;
 bank=iw[0x28]^1;other=iw[0x2f58]^1;
 if(f->owners->ready[bank]!=0x4152544fu)return 0;
 front=*(const Word *)(iw+0x2c50+bank*4);
 ui=*(const Word *)(iw+0x2f60+other*4);
 main=*(const Word *)(iw+0x20+bank*4);
 if(front>48 || ui>32 || main>128 ||
    *(const Word *)(iw+0x3168+other*4)>16)return 0;
 if(front+main>=128)ui=0;
 else if(ui>128-main-front)ui=128-main-front;
 offset=front+ui;shown=main;
 if(shown>128-offset)shown=128-offset;
 source=(const uint16_t *)(iw+0x30+bank*1024);
 entries=f->owners->entries[bank];
 /* Native12BC has already established source==hardware for this main span.
  * No operation here can refuse after counter validation, so publish directly
  * instead of staging a second128-byte tag array. Stale owner records are still
  * rejected against all three CURRENT source attributes before any owner tag. */
 if(!((uintptr_t)f->tags&3))for(i=0;i<32;++i)((Word *)f->tags)[i]=0xffffffffu;
 else for(i=0;i<128;++i)f->tags[i]=255;
 if(f->banks)for(i=0;i<10;++i)f->banks[i]=0;
 for(i=0;i<shown;++i,source+=4,++entries) {
  unsigned owner=entries->owner;
  if(owner>=10 || !(f->enabled&(1u<<owner)))continue;
  if((entries->attributes[0]^source[0])|(entries->attributes[1]^source[1])|
     (entries->attributes[2]^source[2]))continue;
  f->tags[offset+i]=owner;requested|=1u<<owner;
  if(f->banks)f->banks[owner]|=1u<<(source[2]>>12);
 }
 return requested;
}

unsigned ffta_art_frame_fused_owners_leaf(const FFTA_ArtFusedOwnerFrame *input) {
 const FFTA_ArtOwnerFrame *f=&input->owner;
 const uint8_t *iw=f->iwram;
 unsigned bank,other,front,ui,main,tail,shown,offset,extent,i;
 unsigned requested=0,occupied=0,eight=0,valid=1;
 const FFTA_ArtOwnerEntry *entries;
 FFTA_ArtOamDemands *d=input->demands;
 if(iw[0x28]>1 || iw[0x2f58]>1)return 0;
 bank=iw[0x28]^1;other=iw[0x2f58]^1;
 if(f->owners->ready[bank]!=0x4152544fu)return 0;
 front=*(const Word *)(iw+0x2c50+bank*4);
 ui=*(const Word *)(iw+0x2f60+other*4);
 main=*(const Word *)(iw+0x20+bank*4);
 tail=*(const Word *)(iw+0x3168+other*4);
 if(front>48 || ui>32 || main>128 || tail>16)return 0;
 if(front+main>=128)ui=0;
 else if(ui>128-main-front)ui=128-main-front;
 offset=front+ui;shown=main;
 if(shown>128-offset)shown=128-offset;
 extent=offset+shown+tail;if(extent>128)extent=128;
 entries=f->owners->entries[bank];
 if(!((uintptr_t)f->tags&3))for(i=0;i<32;++i)((Word *)f->tags)[i]=0xffffffffu;
 else for(i=0;i<128;++i)f->tags[i]=255;
 if(f->banks)for(i=0;i<10;++i)f->banks[i]=0;
 for(i=0;i<extent;++i) {
#ifdef FFTA_ART_FUSED_WORD_READS
  /* The native-only caller proves word-aligned8-byte OAM and owner records.
   * Read both attribute halves together; attr3 and the reserved owner byte
   * remain excluded from ownership, exactly as in the field-wise bridge. */
  const Word *object=(const Word *)(f->hardware+i*4);
  unsigned ab=object[0],a=ab&65535,c=object[1]&65535,owner=255;
#else
  unsigned a=f->hardware[i*4],b=f->hardware[i*4+1],c=f->hardware[i*4+2],owner=255;
#endif
  if(i>=offset && i<offset+shown) {
#ifdef FFTA_ART_FUSED_WORD_READS
   const Word *entry=(const Word *)(entries+i-offset);
   unsigned recorded=entry[1],candidate=(recorded>>16)&255;
   if(candidate<10 && (f->enabled&(1u<<candidate)) &&
      entry[0]==ab && (recorded&65535)==c) {
#else
   const FFTA_ArtOwnerEntry *entry=entries+i-offset;
   unsigned candidate=entry->owner;
   if(candidate<10 && (f->enabled&(1u<<candidate)) &&
      !((entry->attributes[0]^a)|(entry->attributes[1]^b)|(entry->attributes[2]^c))) {
#endif
    owner=candidate;f->tags[i]=owner;requested|=1u<<owner;
    if(f->banks)f->banks[owner]|=1u<<(c>>12);
   }
  }
  if((a&0x300)==0x200)continue;
  if((a>>14)==3){valid=0;continue;}
  if(owner!=255) {
#ifdef FFTA_ART_FUSED_WORD_READS
   if((a&0xe100) || (ab>>30)!=2)valid=0;
#else
   if((a&0xe100) || (b>>14)!=2)valid=0;
#endif
  } else if(a&0x2000)d->indices[eight++]=(uint8_t)i;
  else occupied|=1u<<(c>>12);
 }
 /* An invalid native object makes later planning refuse before hardware
  * writes. Ownership output itself remains identical to the general bridge.
  * No retained demand or pixel data crosses a composition invocation. */
 d->occupied=occupied;d->requested=requested;d->count=valid?eight:129;
 *input->extent=extent;
 return requested;
}
