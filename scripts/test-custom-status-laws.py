"""Actual native custom applications survive cleanup into late law queries.

No supplied success masks or calls to the receipt writer. This is transport
acceptance; predictive law warnings and real Judge playback are separate.
"""
import collections,itertools,json,pathlib,struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-geomancer-arts.py'
ns={'__file__':str(source),'__name__':'custom_law_fixture'}
exec(compile(source.read_text().split('\nfor action,seed in itertools.product')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,STACK,regs,reset,execute,call,half,state,job,equip,wrappers=(ns[k] for k in
 ('m','S','meta','OUT','A','T','STACK','regs','reset','execute','call','half','state','job','equip','wrappers'))
checks=collections.Counter();samples=[];case=None;LAW=0x0203e000

def check(k,a,b):
 checks[k]+=1;assert a==b,(k,case,a,b)

def effect(action):
 if action==355:return call('ffta_wound_record_remaining',call('ffta_owned_wound',T))
 if action==373:return call('ffta_viking_challenger',T)
 if action==379:return call('ffta_geo_wisp',T)
 return call('ffta_dancer_debuff',T,int(action==405))

def existing(action):
 if action==355:call('ffta_wound_record_replace',call('ffta_owned_wound',T),60)
 elif action==373:call('ffta_viking_grant_challenge',T,A)
 elif action==379:m.put(state(T)+17,b'\x40')
 else:m.put(state(T)+3,bytes((2<<(3 if action==405 else 0),)))

def query(action,mask,damage,kind=16,value=0,residue=0,move=0):
 m.put(LAW,bytes(4)+bytes((kind,value))+bytes(10))
 m.put(STACK+residue,struct.pack('<4I',move,damage&65535,mask,LAW))
 receipt=call('ffta_battle_workspace',0x2620)
 before=m.read(A,264)+m.read(T,264)+m.read(state(A),22)+m.read(state(T),22)+m.read(receipt,64)+m.read(0x030034b0,4)
 result=m.call(0x081343c8,A,T,action,0,stack=STACK+residue)
 check('pure-late-query',m.read(A,264)+m.read(T,264)+m.read(state(A),22)+m.read(state(T),22)+m.read(receipt,64)+m.read(0x030034b0,4),before)
 return result

for action,condition,seed in itertools.product((355,373,379,404,405),
 ('normal','refresh','inoculated','immune','lethal','petrify','MP'),range(4)):
 case=(action,condition,seed);reset(action,seed)
 race,jid,weapon={355:(1,116,383),373:(2,119,1),379:(3,121,1),404:(4,124,416),405:(4,124,416)}[action]
 job(A,race,jid);job(T,1,2);m.put(A+0x2a,struct.pack('<5H',weapon,0,0,0,0));m.put(T+0x29,b'\x80')
 m.put(T+0x3a,bytes(2));m.put(state(T),bytes(22));m.put(call('ffta_owned_wound',T),bytes(2))
 if condition=='refresh':existing(action)
 if condition=='inoculated':call('ffta_inoculated_grant',T,0)
 if condition=='immune':
  bank=m.word(m.word(0x080cd538)+4)
  index=next(i for i in range(1,144) if half(bank+8*i+4)==11 and m.read(bank+8*i+6,1)==b'\x03')
  m.put(T+0x3b,bytes((index,)));m.put(T+0x40+index,b'\xff')
  check('real-equipped-Immunity',m.call(0x080cd50c,T,stack=STACK),11)
 if condition=='MP':
  bank=m.word(m.word(0x080cd538)+4)
  index=next(i for i in range(1,144) if half(bank+8*i+4)==13 and m.read(bank+8*i+6,1)==b'\x02')
  m.put(T+0x3a,bytes((index,)));m.put(T+0x40+index,b'\xff')
  check('real-equipped-Damage-to-MP',m.call(0x080cd4d4,T,stack=STACK),13)
 if condition=='lethal':m.put(T+0x18,b'\x01\x00')
 if condition=='petrify':m.put(T+0xe8,b'\x40')
 before=half(T+0x18);execute(action);lost=before-half(T+0x18)
 rows=[]
 for i in range(14):
  o=regs[0]+i*0x2c4
  if m.word(o)!=wrappers[A] or half(o+16)!=action:continue
  for j in range(m.read(o+0x2c0,1)[0]):
   row=o+0x20+j*0x2c;w=m.word(row)
   if w and m.word(w)==T:rows.append(row)
 applied=bool(effect(action)) if condition!='refresh' else (lost>0 if action!=373 else any(half(r+12)&128 and not half(r+12)&64 for r in rows))
 if condition in ('inoculated','immune','petrify') or (condition in ('MP','lethal') and action!=373):check('prevention-no-application',applied,False)
 # Clear the live effect BEFORE law reporting, as a later remedy may do.
 m.put(state(T),bytes(22));m.put(call('ffta_owned_wound',T),bytes(2))
 for row in rows:
  for residue in (0,4):
   check('actual-application-reaches-law-after-clear',query(action,row+0x14,half(row+0x1e),residue=residue),int(applied))
  check('no-Poison-alias',query(action,row+0x14,half(row+0x1e),kind=15,value=9),0)
  check('movement-gate',query(action,row+0x14,0,move=1),0)
  copied=LAW+0x100;m.put(copied,m.read(row+0x14,8))
  check('foreign-copied-mask-rejected',query(action,copied,half(row+0x1e)),0)
 samples.append(dict(action=action,condition=condition,seed=seed,rows=len(rows),loss=lost,applied=applied))
 if rows:
  m.put(regs[0],bytes(14*0x2c4));check('retired-result-rejected',query(action,rows[0]+0x14,1),0)
for action in (355,373,379,404,405):
 check('nonvacuous-application-'+str(action),any(s['action']==action and s['condition']=='normal' and s['applied'] and s['rows'] for s in samples),True)
 check('nonvacuous-refresh-'+str(action),any(s['action']==action and s['condition']=='refresh' and s['applied'] and s['rows'] for s in samples),True)
check('nonvacuous-miss',any(s['condition']=='normal' and not s['applied'] and s['rows'] for s in samples),True)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),samples=samples,
 limits=['Predictive custom status warnings, other law kinds and actual Judge playback require separate acceptance.'])
(OUT/'custom-status-laws.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
