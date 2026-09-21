#include "mystic-knight.h"

/* Exact floor(product*n/(denominator*d)) without constructing either
 * potentially overflowing product. All callers use positive denominators.
 * A genuinely unrepresentable final result saturates, never wraps. */
uint64_t ffta_damage_ratio(uint64_t product,uint64_t denominator,unsigned n,unsigned d){
 if(!denominator || !d)return 0;
 if(n==d)return product/denominator;
 if(!n)return 0;
 unsigned x=n,y=d;
 while(y){unsigned r=x%y;x=y;y=r;}
 n/=x;d/=x;
 uint64_t q=product/denominator,r=product%denominator,part=0;
 if(r<=UINT64_MAX/n)part=r*n/denominator;
 else {
  /* Binary multiply/divide. Keep the remainder strictly below the divisor
   * and compare before adding so even a UINT64_MAX divisor is supported. */
  uint64_t remainder=0;
  for(unsigned bit=32;bit;){
   --bit;part*=2;
   if(remainder>=denominator-remainder){remainder-=denominator-remainder;part++;}
   else remainder+=remainder;
   if((n>>bit)&1u){
    if(remainder>=denominator-r){remainder-=denominator-r;part++;}
    else remainder+=r;
   }
  }
 }
 /* (q%d)*n+part fits: d and n are unsigned32 and part<n. */
 uint64_t tail=((q%d)*n+part)/d,whole=q/d;
 if(whole>(UINT64_MAX-tail)/n)return UINT64_MAX;
 return whole*n+tail;
}
