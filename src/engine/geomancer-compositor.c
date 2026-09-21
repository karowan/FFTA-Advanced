#include "geomancer-compositor.h"
#define KEY_UNUSED 0xfffdu
#define KEY_STATIC 0xfffeu
#define KEY_SHARED 0xffffu
static const uint32_t blank[8]={0,0,0,0,0,0,0,0};
#define BLANK_BUCKET 236u

unsigned ffta_geo_cache_index(unsigned i){
 if(i<640)return i;
 if(i<FFTA_GEO_CACHE_TILES)return i+192; /* 06006800..06006bff */
 return ~0u;
}
static int floor8(int v){return v>=0?v/8:-((-v+7)/8);}
static unsigned intensity(unsigned c){
 return 3*(c&31)+6*((c>>5)&31)+((c>>10)&31);
}
static unsigned equal(const uint32_t *a,const uint32_t *b){
 for(unsigned i=0;i<8;i++)if(a[i]!=b[i])return 0;
 return 1;
}
static unsigned bucket_for(const uint32_t *pixels){
  unsigned h=2166136261u;
  for(unsigned i=0;i<8;i++)h=(h^pixels[i])*16777619u;
  /* Low FNV bits alone ignore most pixel columns and cluster terrain edges.
   * Fold all source bits into the bucket; equality remains authoritative. */
  h^=h>>16;h*=0x7feb352du;h^=h>>15;h*=0x846ca68bu;h^=h>>16;
  return h&(FFTA_GEO_HASH_SIZE-1);
}
static unsigned intern(FFTA_GeoFrame *f,const uint32_t *pixels,unsigned bucket){
 if(bucket>=FFTA_GEO_HASH_SIZE)bucket=bucket_for(pixels);
 unsigned slot=bucket;
 for(unsigned probes=0;probes<FFTA_GEO_HASH_SIZE;probes++){
  unsigned entry=f->hash[slot];
  if(!entry){
   unsigned index=f->count;
   if(index==FFTA_GEO_CACHE_TILES){
    for(index=1;index<f->count && f->animation_key[index]!=KEY_UNUSED;index++){}
    if(index==f->count)return ~0u;
   }else f->count++;
   f->animation_key[index]=KEY_UNUSED;
   for(unsigned i=0;i<8;i++)f->graphics[index][i]=pixels[i];
   f->hash[slot]=(uint16_t)(index+1);return index;
  }
  if(equal(f->graphics[entry-1],pixels))return entry-1;
  slot=(slot+1)&(FFTA_GEO_HASH_SIZE-1);
 }
 return ~0u;
}
static unsigned opaque(const uint32_t *pixels){
 /* Parallel zero-nibble detection. Borrow propagation can only follow an
  * actual zero, so this answers existence without64 serial pixel tests. */
 for(unsigned y=0;y<8;y++){
  unsigned v=pixels[y];if((v-0x11111111u)&~v&0x88888888u)return 0;
 }
 return 1;
}
static unsigned row_opaque(const FFTA_GeoFrame *f,unsigned p,unsigned x){
 return f->row_metadata[p][x]==0xffffu?opaque(f->row_source[p][x]):
  f->row_metadata[p][x]>>10;
}
static unsigned flipped_row(unsigned pixels,unsigned key){
 if(key&0x400u){
  pixels=((pixels&0x0f0f0f0fu)<<4)|((pixels>>4)&0x0f0f0f0fu);
  pixels=((pixels&0x00ff00ffu)<<8)|((pixels>>8)&0x00ff00ffu);
  pixels=(pixels<<16)|(pixels>>16);
 }
 return pixels;
}
static unsigned load_row(const FFTA_GeoScene *s,FFTA_GeoFrame *f,int x0,int y,
 const FFTA_GeoSource *sources,unsigned begin,unsigned end){
 for(unsigned plane=0;plane<2;plane++)for(unsigned col=begin;col<end;col++){
  int x=x0+(int)col;unsigned word=0;
  if(x>=0 && x<64 && y>=0 && y<64)word=s->arrangement[plane][y*64+x];
  unsigned tile=word&1023;
  f->palette_bits[plane][col]=(uint16_t)word;
  f->row_source[plane][col]=f->row[plane][col];
  f->row_metadata[plane][col]=0xffffu;
  if(x<0 || x>=64 || y<0 || y>=64){
   f->palette_bits[plane][col]|=0xfffu;
   f->row_source[plane][col]=blank;f->row_metadata[plane][col]=BLANK_BUCKET;
   continue;
  }
  /* Original maps may leave meaningless lower references behind an opaque
   * foreground. Outlines only add opaque pixels, never reveal those cells. */
  if(plane && row_opaque(f,0,col)){
   f->palette_bits[plane][col]|=0xfffu;
   f->row_source[plane][col]=blank;f->row_metadata[plane][col]=BLANK_BUCKET;
   continue;
  }
  if(sources && tile>=s->animated_tiles && tile<s->tile_count){
   const FFTA_GeoSource *source=&sources[((word>>10)&3u)*s->tile_count+tile];
   f->row_source[plane][col]=source->pixels;
   f->row_metadata[plane][col]=(uint16_t)(source->bucket|(source->opaque<<10));
   continue;
  }
  const uint32_t *graphics=0;
  if(tile<s->tile_count)graphics=(tile<s->animated_tiles?s->animated_graphics:s->graphics)+tile*8;
  else for(unsigned i=0;i<s->retained_count;i++)
   if(s->retained_ids[i]==tile){graphics=s->retained_graphics+i*8;break;}
  if(!graphics)return 0;
  if(tile<s->animated_tiles && x>=0 && x<64 && y>=0 && y<64)
   f->animated_used[tile>>5]|=1u<<(tile&31u);
  if(!(word&0xc00u) && x>=0 && x<64 && y>=0 && y<64){
   for(unsigned row=0;row<8;row++)f->row[plane][col][row]=graphics[row];
   continue;
  }
  for(unsigned row=0;row<8;row++){
   unsigned pixels=graphics[(word&0x800u)?7-row:row];
   pixels=flipped_row(pixels,word);
   /* Outside the native canvas is transparent, even if graphic0 is nonzero. */
   f->row[plane][col][row]=(x<0 || x>=64 || y<0 || y>=64)?0:pixels;
  }
 }
 return 1;
}
static void edges(const FFTA_GeoScene *s,FFTA_GeoFrame *f,int x0,int y0,unsigned begin,unsigned end){
 /* Union every shadow before every light core: adjacent fields cannot erase
  * one another's core, regardless of caster or board traversal order. */
 for(unsigned pass=0;pass<2;pass++){
 for(unsigned field=0;field<f->field_count;field++){
  unsigned i=f->fields[field];
  unsigned kind=s->board[i]&3u;if(!kind)continue;
  const FFTA_GeoProjection *p=&s->projection[i];
  if(p->y+16<=y0 || p->y>=y0+8 || p->x+32<=x0 || p->x>=x0+248)continue;
  for(unsigned q=0;q<4;q++){
   unsigned plane=p->plane[q];if(plane>1)continue;
   for(unsigned ly=0;ly<8;ly++){
    int sy=p->y+(int)(q>>1)*8+(int)ly;
    if(sy<y0 || sy>=y0+8 || sy<0 || sy>=512)continue;
    /* Rime is dashed; Refuge is continuous. A shared edge is an idempotent
     * union, so caster/board traversal order cannot change its appearance. */
    if(!(kind&2u) && (ly&2u))continue;
    unsigned start=(q==1 || q==2)?2*ly:14-2*ly;
    for(int n=pass?0:-1;n<(pass?2:3);n++){
     /* Keep the halo on its native quarter, including its palette/plane.
      * This preserves the proven set of graphics cells touched by a field. */
     if((int)start+n<0 || (int)start+n>=16)continue;
     int sx=p->x+(int)(q&1)*16+(int)start+(int)n;
     if(sx<x0 || sx>=x0+248 || sx<0 || sx>=512)continue;
     unsigned col=(unsigned)(sx-x0)>>3,pixel=(unsigned)sx&7u;
     if(col<begin || col>=end)continue;
     unsigned bank=(f->palette_bits[plane][col]>>12)&7u;
     unsigned ink=pass?f->light[bank]:f->dark[bank];
     /* Immutable terrain stays in ROM until an edge actually changes it. */
     if(f->row_source[plane][col]!=f->row[plane][col]){
      for(unsigned r=0;r<8;r++)f->row[plane][col][r]=f->row_source[plane][col][r];
      f->row_source[plane][col]=f->row[plane][col];
     }
     f->row_metadata[plane][col]=0xffffu;
     uint32_t *row=&f->row[plane][col][sy-y0];
     f->palette_bits[plane][col]|=0xfffu; /* Modified pixels have no source key. */
     *row=(*row&~(15u<<(pixel*4)))|(ink<<(pixel*4));
    }
   }
  }
 }
}
}
static unsigned compose_span(const FFTA_GeoScene *s,FFTA_GeoFrame *f,
 const FFTA_GeoSource *sources,int x0,int ty,unsigned begin,unsigned end){
 if(!load_row(s,f,x0,ty,sources,begin,end))return 0;
 edges(s,f,x0*8,ty*8,begin,end);
 for(unsigned x=begin;x<end;x++){
  unsigned hidden=row_opaque(f,0,x);
  unsigned position=((unsigned)ty&31u)*32+((unsigned)(x0+(int)x)&31u);
  for(unsigned p=0;p<2;p++){
   unsigned key=f->palette_bits[p][x]&0xfffu,slot=(key^(key>>8))&255u;
   unsigned index;
   if(p && hidden)index=0;
   else if(key!=0xfffu && f->memo_key[slot]==key)index=f->memo_value[slot];
   else {
    unsigned metadata=f->row_metadata[p][x];
    index=intern(f,f->row_source[p][x],metadata==0xffffu?metadata:metadata&(FFTA_GEO_HASH_SIZE-1));
    if(key!=0xfffu){f->memo_key[slot]=(uint16_t)key;f->memo_value[slot]=(uint16_t)index;}
   }
   if(index==~0u)return 0;
   unsigned animation=KEY_STATIC;
   int tx=x0+(int)x;
   if(!(p && hidden)){
    if(key!=0xfffu){
     if((key&1023u)<s->animated_tiles)animation=key;
    }else if(tx>=0 && tx<64 && ty>=0 && ty<64 &&
      (s->arrangement[p][ty*64+tx]&1023u)<s->animated_tiles)animation=KEY_SHARED;
   }
   unsigned previous=f->animation_key[index];
   f->animation_key[index]=(uint16_t)(previous==KEY_UNUSED?animation:
     previous==animation?previous:KEY_SHARED);
   f->map[p][position]=(uint16_t)(ffta_geo_cache_index(index)|(f->palette_bits[p][x]&0xf000u));
  }
 }
 return 1;
}
unsigned ffta_geo_compose(const FFTA_GeoScene *s,FFTA_GeoFrame *f,const FFTA_GeoSource *sources){
 if(!f)return 0;
 f->ready=0;f->count=0;
 if(!f->graphics || !s || !s->arrangement[0] || !s->arrangement[1] || !s->graphics ||
    !s->palette || !s->projection || !s->board || !s->tile_count ||
    s->animated_tiles>s->tile_count || s->animated_tiles>128 ||
    (s->animated_tiles && !s->animated_graphics) ||
    s->retained_count>8 || (s->retained_count && (!s->retained_ids || !s->retained_graphics)) ||
    s->tile_count>640 || s->camera_x < -256 || s->camera_x>768 ||
    s->camera_y < -256 || s->camera_y>768)return 0;
 for(unsigned p=0;p<2;p++)for(unsigned i=0;i<1024;i++)f->map[p][i]=0;
 for(unsigned i=0;i<FFTA_GEO_HASH_SIZE;i++)f->hash[i]=0;
 for(unsigned i=0;i<FFTA_GEO_CACHE_TILES;i++){
  f->animation_key[i]=KEY_UNUSED;
 }
 for(unsigned i=0;i<256;i++)f->memo_key[i]=0xffffu;
 f->field_count=0;
 for(unsigned i=0;i<4;i++)f->animated_used[i]=0;
 for(unsigned i=0;i<256;i++)if(s->board[i]&3u)f->fields[f->field_count++]=(uint8_t)i;
 for(unsigned b=0;b<8;b++){
  unsigned light=1,dark=1;
  for(unsigned n=2;n<16;n++){
   if(intensity(s->palette[b*16+n])>intensity(s->palette[b*16+light]))light=n;
   if(intensity(s->palette[b*16+n])<intensity(s->palette[b*16+dark]))dark=n;
  }
  f->light[b]=(uint8_t)light;f->dark[b]=(uint8_t)dark;
 }
 intern(f,blank,BLANK_BUCKET);
 f->animation_key[0]=KEY_STATIC; /* Always reserve the transparent ring cell. */
 int x0=floor8(s->camera_x),y0=floor8(s->camera_y);
 for(unsigned y=0;y<21;y++){
  int ty=y0+(int)y;
  if(!compose_span(s,f,sources,x0,ty,0,31))return 0;
 }
 f->origin_x=x0;f->origin_y=y0;
 f->ready=1;return 1;
}
static unsigned logical(unsigned word){
 unsigned i=word&1023u;
 return i<640?i:i-192;
}
unsigned ffta_geo_shift(const FFTA_GeoScene *s,FFTA_GeoFrame *f,const FFTA_GeoSource *sources){
 if(!s || !f || !f->ready || !f->graphics || !f->count ||
    f->count>FFTA_GEO_CACHE_TILES || s->camera_x < -256 || s->camera_x>768 ||
    s->camera_y < -256 || s->camera_y>768)return 0;
 int nx=floor8(s->camera_x),ny=floor8(s->camera_y),ox=f->origin_x,oy=f->origin_y;
 int dx=nx-ox,dy=ny-oy;
 if(dx<=-31 || dx>=31 || dy<=-21 || dy>=21)return 0;
 if(!dx && !dy)return 1;
 f->ready=0;
 /* A transient84-byte bitset identifies retained cache entries. Reuse the
  * existing unused provenance marker for free slots rather than enlarging
  * the native allocation with persistent reference counters. */
 uint32_t used[(FFTA_GEO_CACHE_TILES+31u)/32u]={1};
 for(int y=oy;y<oy+21;y++)for(int x=ox;x<ox+31;x++){
  unsigned retained=x>=nx && x<nx+31 && y>=ny && y<ny+21;
  unsigned pos=((unsigned)y&31u)*32+((unsigned)x&31u);
  for(unsigned p=0;p<2;p++){
   unsigned index=logical(f->map[p][pos]);
   if(index>=f->count || f->animation_key[index]==KEY_UNUSED)return 0;
   if(retained)used[index>>5]|=1u<<(index&31u);
   else f->map[p][pos]=0;
  }
 }
 /* Rehash only retained cache entries. Pixel hashes are recomputed because
  * an accepted animation refresh may have changed them since last compose.
  * Equal animated/static aliases can retain separate slots; exhaustion falls
  * back to the full exact interner and its proven capacity bound. */
 for(unsigned i=0;i<FFTA_GEO_HASH_SIZE;i++)f->hash[i]=0;
 for(unsigned i=0;i<256;i++)f->memo_key[i]=0xffffu;
 for(unsigned i=0;i<f->count;i++){
  if(!(used[i>>5]&(1u<<(i&31u)))){f->animation_key[i]=KEY_UNUSED;continue;}
  unsigned slot=bucket_for(f->graphics[i]);
  while(f->hash[slot])slot=(slot+1)&(FFTA_GEO_HASH_SIZE-1);
  f->hash[slot]=(uint16_t)(i+1);
 }
 for(int y=ny;y<ny+21;y++){
  unsigned begin=0,end=31;
  if(y>=oy && y<oy+21){
   if(dx>0)begin=(unsigned)(31-dx);
   else if(dx<0)end=(unsigned)-dx;
   else continue;
  }
  if(!compose_span(s,f,sources,nx,y,begin,end))return 0;
 }
 f->origin_x=nx;f->origin_y=ny;f->ready=1;return 1;
}
static void animated_pixels(const FFTA_GeoScene *s,unsigned key,uint32_t *out){
 const uint32_t *source=s->animated_graphics+(key&1023u)*8;
 if(!(key&0xc00u)){
  for(unsigned y=0;y<8;y++)out[y]=source[y];
  return;
 }
 for(unsigned y=0;y<8;y++)out[y]=flipped_row(source[(key&0x800u)?7-y:y],key);
}
unsigned ffta_geo_refresh_animation(const FFTA_GeoScene *s,FFTA_GeoFrame *f){
 if(!s || !f || !f->ready || !f->graphics || !s->animated_graphics ||
    !s->animated_tiles || s->animated_tiles>128 || !f->count ||
    f->count>FFTA_GEO_CACHE_TILES)return 0;
 int x0=floor8(s->camera_x),y0=floor8(s->camera_y);
 unsigned shared=0;
 /* Check before writing: a newly transparent foreground can expose a lower
  * tile omitted by the previous frame. That requires complete composition. */
 for(unsigned i=0;i<f->count;i++){
  unsigned key=f->animation_key[i];
  if(key==KEY_SHARED){shared=1;continue;}
  if(key>=KEY_UNUSED)continue;
  if((key&1023u)>=s->animated_tiles)return 0;
  /* Flips cannot change opacity, so avoid constructing transformed pixels. */
  if(opaque(s->animated_graphics+(key&1023u)*8)!=opaque(f->graphics[i]))return 0;
 }
 /* Shared cache entries may also serve static cells or another animated key.
  * Outlined animated tiles likewise cannot be copied verbatim. Compare their
  * complete new pixels with the old cache; fall back only if they differ.
  * Do not assume that two equal old sources stay equal in the next frame. */
 if(shared)for(unsigned i=0;i<256;i++)f->memo_key[i]=KEY_SHARED;
 if(shared)for(unsigned y=0;y<21;y++){
  int ty=y0+(int)y;if(ty<0 || ty>=64)continue;
  for(unsigned x=0;x<31;x++){
   int tx=x0+(int)x;if(tx<0 || tx>=64)continue;
   unsigned pos=((unsigned)ty&31u)*32+((unsigned)(x0+(int)x)&31u);
   for(unsigned p=0;p<2;p++){
    unsigned index=logical(f->map[p][pos]);
    if(f->animation_key[index]!=KEY_SHARED)continue;
    unsigned key=s->arrangement[p][ty*64+tx]&0xfffu;
    if((key&1023u)>=s->animated_tiles)continue;
    unsigned slot=(key^(key>>8))&255u;
    if(f->memo_key[slot]==key && f->memo_value[slot]==index)continue;
    if(p && opaque(f->graphics[logical(f->map[0][pos])]))continue;
    animated_pixels(s,key,f->row[0][0]);
    /* Static aliases never change. For an animated outlined tile, raw pixels
     * equal to the old outlined cache are safe too: reapplying the unchanged
     * edge ink is idempotent. Any difference takes the conservative full path.
     * The front entry is checked before trusting its old opacity for lower. */
    if(!equal(f->graphics[index],f->row[0][0]))return 0;
    f->memo_key[slot]=(uint16_t)key;f->memo_value[slot]=(uint16_t)index;
   }
  }
 }
 /* Every alias/opacity guard passed. Maps and tile ownership stay identical;
  * only unambiguous animated cache entries can now be updated in place. */
 for(unsigned i=0;i<f->count;i++){
  unsigned key=f->animation_key[i];
  if(key<KEY_UNUSED)animated_pixels(s,key,f->graphics[i]);
 }
 return 1;
}
