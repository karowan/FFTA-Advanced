"""Fixed native LR/TBN/payment actions and explicitly owned status lifecycles."""
import pathlib
_script=pathlib.Path(__file__).with_name('test-desperation.py')
exec(compile(_script.read_text().split('# Native support lookup')[0],str(_script),'exec'))
def state(unit):
 p=m.call(allS['ffta_job_state'],unit,stack=STACK)
 assert p and 0x0203f410<=p<0x0203f728,hex(p)
 return p
def support(race,lesson):
 m.put(UNIT+0x3b,bytes((lesson,)))
 m.put((0x02001b40+lesson-144) if race==1 else UNIT+0x40+lesson,b'\xff')
for race,action,blood,selfmode,seed in itertools.product((1,2),(360,364),(False,True),(False,True),range(8)):
 reset(m,action,117 if race==1 else 119,race,seed,friend=action==364)
 actorstate=state(UNIT);targetstate=state(TARGET)
 m.put(actorstate,bytes(4));m.put(targetstate,bytes(4))
 if blood:
  support(race,168 if race==1 else 87)
  check('mastered_bloodcasting',m.call(0x080cd50c,UNIT,stack=STACK),131)
 if selfmode:m.put(UNIT+0x2a,bytes(10))
 m.call(0x080a433c,regs[0],wrappers[UNIT],4 if selfmode else 5,14,stack=regs[13])
 expected_cost=(50 if action==364 else 0)+(2*(10 if action==364 else 8) if blood else 0)
 check('combined_HP_payment',half(m,UNIT+0x18),500-expected_cost)
 check('native_MP_payment',half(m,UNIT+0x1c),99 if blood else 99-(10 if action==364 else 8))
 check('closed_roots',m.read(0x0203ff44,8),bytes(8))
 if action==360:
  check('last_resort_after_hit_or_miss',m.read(actorstate,1),b'\x06')
  check('self_mode_no_injury',half(m,UNIT+0x18),500-expected_cost)
 else:
  target=UNIT if selfmode else TARGET
  check('explicit_caster_link',m.read(state(target)+1,2),bytes((m.call(allS['ffta_job_origin'],UNIT,stack=STACK),1)))
 outcomes.append(dict(race=race,action=action,blood=blood,selfmode=selfmode,seed=seed,actorHP=half(m,UNIT+0x18),targetHP=half(m,TARGET+0x18)))
# Native public eligibility must reject insufficient aggregate HP before MP is
# converted. Private calls preserve live state and RNG, including failure.
for race,action,hp in itertools.product((1,2),(23,356,359,361,363,364),(1,20,21,50,51,70,71,128,129,500)):
 reset(m,action,117 if race==1 else 119,race)
 support(race,168 if race==1 else 87);m.put(UNIT+0x18,struct.pack('<H',hp))
 native_mp=m.call(S['ffta_drk_original_mp_cost'],UNIT,action,stack=STACK)
 native_cost={356:50,363:100,364:50}.get(action,0)
 cost=native_cost+native_mp*2
 check('aggregate_cost_oracle',m.call(S['ffta_drk_hp_cost'],UNIT,action,stack=STACK),cost)
 check('zero_MP_replacement',m.call(0x0812ed98,UNIT,action,stack=STACK),0)
 before=m.read(0x02000000,0x40000);rng=m.word(0x030034b0)
 usable=m.call(S['ffta_drk_usable'],UNIT,action,0,stack=STACK)
 if hp<=cost:check('no_lethal_commit',usable,0)
 check('cost_query_preserves_live',m.read(0x02000000,0x40000),before)
 check('cost_query_preserves_rng',m.word(0x030034b0),rng)
# Explicit lifecycle entrypoints exercise canonical peer ownership, intact
# linked benefit/drawback and application-turn exclusion without battle input.
for event in (1,2,3,4,5,6,7):
 reset(m);a=state(UNIT);t=state(TARGET);m.put(a,bytes(4));m.put(t,bytes(4))
 m.call(S['ffta_drk_grant_last_resort'],UNIT,1,stack=STACK)
 # Make ally before granting the barrier.
 m.put(TARGET+0x29,m.read(UNIT+0x29,1))
 check('grant_source_link',m.call(S['ffta_drk_grant_tbn'],TARGET,UNIT,stack=STACK),1)
 m.call(S['ffta_drk_lifecycle_event'],UNIT,event,stack=STACK)
 check('linked_lr_cleanup',m.read(a,1),b'\0' if event in (2,3,4,5,7) else b'\x06')
 check('caster_peer_cleanup',m.read(t+2,1),b'\0' if event in (1,2,3,4,5) else b'\x01')
reset(m);a=state(UNIT);m.put(a,bytes(4));m.call(S['ffta_drk_grant_last_resort'],UNIT,1,stack=STACK)
for expected in (2,1,0):
 m.call(S['ffta_drk_lifecycle_turn_end'],UNIT,stack=STACK)
 check('application_turn_then_two_turns',m.read(a,1),bytes((expected,)))
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),outcomes=outcomes,scope=__doc__,
 limits=['Abyssal Blade absent','Multi-subcast aggregate reservation unimplemented','Full laws/AI and in-game LR/TBN/status displays pending','Reaction queue and floor-to-zero barriers require their separate acceptance'])
(OUT/'batch-native.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='outcomes'},indent=2))
