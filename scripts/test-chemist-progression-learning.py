"""Native prerequisite, AP, equipment, combo and staged shop consumers."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
exec(compile((ROOT/'scripts/test-chemist-progression-effects.py').read_text().split('\ntry:\n')[0],'<authenticated ARM setup>','exec'))
out=Path(meta['path']).parent/'learning';out.mkdir(exist_ok=True)
design=json.loads((ROOT/'notes/chemist-progression-abilities.json').read_text())
equipment=json.loads((ROOT/'notes/chemist-progression-equipment.json').read_text())
def lesson_row(race,index):return m.word(m.word(0x080257e8)+4*race)+8*index
def actions(job,race):
 return [i for n in range(call('ffta_job_lesson_count',job)) if m.read(lesson_row(race,i:=call('ffta_job_lesson_at',job,n))+6,1)==b'\x01']
try:
 for job in design['jobs']:
  case=('prerequisites',job['id']);reset();u=TARGET
  m.put(u+5,bytes((job['id'],job['race'],job['id'])));m.put(u+0x40,bytes(144))
  for equipped_only in (True,False):
   m.put(u+0x40,bytes(144))
   for prerequisite,needed in job['prerequisites']:
    indices=actions(prerequisite,job['race']);check('enough-original-action-lessons',len(indices)>=needed,True)
    for index in indices[:needed]:call('ffta_ap_set_value',u,index,128 if equipped_only else 127)
   check('unlock-requires-earned-mastery',call('ffta_new_job_eligible',u,job['id']),int(not equipped_only))
  for prerequisite,needed in job['prerequisites']:
   index=actions(prerequisite,job['race'])[needed-1]
   call('ffta_ap_set_value',u,index,0);check('each-prerequisite-required',call('ffta_new_job_eligible',u,job['id']),0)
   call('ffta_ap_set_value',u,index,127)
  for n,lesson in enumerate(job['lessons']):
   index=call('ffta_job_lesson_at',job['id'],n);r=lesson_row(job['race'],index)
   check('native-lesson-ID',int.from_bytes(m.read(r+4,2),'little'),lesson[3])
   check('native-help-installed',int.from_bytes(m.read(r+2,2),'little')>0,True)
   call('ffta_ap_set_value',u,index,0);call('ffta_ability_grant',u,index)
   check('equipment-grants-without-AP',call('ffta_ap_value',u,index),128)
   call('ffta_ap_write_and_equipment_check',u,index,128+lesson[4]//10)
   call('ffta_ability_revoke',u,index)
   check('mastery-survives-unequip',call('ffta_ap_value',u,index),lesson[4]//10)
  check('all-ten-mastered',call('ffta_job_mastered',u,job['id']),1)
  check('seven-actions',call('ffta_job_action_count',u,job['id'],0),7)
  for item in equipment['items']:
   if item['job']!=job['id']:continue
   check('teaching-weapon-equip',m.call(0x080cb5a8,job['id'],item['id'],stack=STACK),1)
  m.put(u+0x3c,bytes((133 if job['id']==126 else 125,)))
  for weapon,want in ((461,job['id']==126),(466,job['id']==127),(462,True),(1,False)):
   m.put(u+0x2a,struct.pack('<5H',weapon,0,0,0,0))
   check('combo-weapon-admission',bool(call('ffta_combo_permitted',u)),want)
 case='stage gated stock';reset();dest=m.call(0x08022840,4096,stack=STACK)
 for stage in range(3):
  for flag in (774,780):m.call(0x080c9574,flag,0,stack=STACK)
  if stage>=1:m.call(0x080c9574,774,1,stack=STACK)
  if stage>=2:m.call(0x080c9574,780,1,stack=STACK)
  count=call('ffta_shop_buy_list',dest,2,0,2)
  ids=[int.from_bytes(m.read(dest+4*i,2),'little') for i in range(count)]
  for item in equipment['items']:
   check('Cyril-stage-teaching-stock',item['id'] in ids,stage>={'S1':0,'S2':1,'S3':2}[item['stage']])
 report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks))
except BaseException as error:
 report=dict(passed=False,romSha1=meta['romSha1'],case=case,error=repr(error),checks=dict(checks));raise
finally:(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
