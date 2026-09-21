"""Reconstruct the pre-initial-commit bootstrap source layout.

The initial source commit already contained four later wrapper repairs, while
its cached engine predates them. Express that historical layout as source, not
an embedded binary. The builder must verify the entire compiled engine hash;
current sources are restored before the integrated replacement layers compile.
Never apply this transformation to the working source checkout or final image.
"""
def replace_once(text,old,new):
 assert text.count(old)==1,('Bootstrap source contract differs',old)
 return text.replace(old,new)

def sources(historical):
 result=dict(historical)
 path='src/engine/exposed-effects.s';text=result[path].decode('utf-8').replace('\r\n','\n')
 for name,next_name in (('preview','original_exposed_preview'),('combo','original_exposed_combo')):
  start=f'ffta_exposed_{name}_entry:\n';end=f'.global ffta_{next_name}\n'
  assert text.count(start)==1 and text.count(end)==1
  body=text.split(start,1)[1].split(end,1)[0]
  assert body.startswith('    pop {r3}\n') and f'    bl ffta_exposed_{name}\n' in body
  text=replace_once(text,start+body+end,start+f'    pop {{r3}}\n    b ffta_exposed_{name}\n'+end)
 result[path]=text.encode('utf-8')
 path='src/engine/status-display.s';text=result[path].decode('utf-8').replace('\r\n','\n')
 # These two historical wrappers predate r12 preservation. Preserve all other
 # instructions and correct their stack-relative slots for the omitted word.
 for sequence in ('    mov r7,r12\n    push {r7}\n','    pop {r7}\n    mov r12,r7\n'):
  assert text.count(sequence)==2
  text=text.replace(sequence,'')
 for old,new in (('    ldr r1,[sp,#20]\n','    ldr r1,[sp,#16]\n'),
   ('    str r0,[sp,#4]\n','    str r0,[sp]\n'),('    str r0,[sp,#8]\n','    str r0,[sp,#4]\n')):
  text=replace_once(text,old,new)
 result[path]=text.encode('utf-8')
 path='src/engine/samurai-state.c';text=result[path].decode('utf-8').replace('\r\n','\n')
 # The frozen bootstrap predates A9's direct-action classification. Samurai's
 # real implementation later replaces this provider from current source.
 text=replace_once(text,
  '        action==FFTA_SAM_A6 || action==FFTA_SAM_A7 || action==FFTA_SAM_A8 || action==FFTA_SAM_A9;\n',
  '        action==FFTA_SAM_A6 || action==FFTA_SAM_A7 || action==FFTA_SAM_A8;\n')
 result[path]=text.encode('utf-8')
 return result
