"""Use actual UI-produced preferences in unequal-stock native executor cases."""
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[3]
source=ROOT/'scripts/jobs/chemist/test-auto-potion-native.py'
exec(compile(source.read_text(encoding='utf-8').split('positive=0')[0],str(source),'exec'))
prior=max(p for p in OUT.glob('potion-menu-*') if (p/'preference-report.json').exists())
ui=json.loads((prior/'preference-report.json').read_text(encoding='utf-8'))
check('UI-evidence-matches-game',ui['romSha1'],meta['romSha1'])
positive=empty=0
for race,preference,boost,stock_pair,seed in itertools.product((3,5),(0,1),(False,True),((0,5),(5,0),(2,5),(5,2)),range(8)):
 sample=next(x for x in ui['outcomes'] if x['race']==race)
 name=f'{race}-reloaded.ram' if preference else f'{race}-Potion-confirmed.ram'
 ui_value=(prior/name).read_bytes()[0x1e80+sample['slot']]
 check('UI-produced-selection',ui_value,preference)
 events=[]
 ordinary=execute(n,seed,ui_value,boost,False,5,150,0,race,stock_pair=stock_pair)
 actual=execute(m,seed,ui_value,boost,True,5,150,0,race,stock_pair=stock_pair)
 trigger=0<ordinary<150
 eligible=trigger and stock_pair[preference]>0
 expected=min(300,ordinary+(25 if preference==0 else 50)*(3 if boost else 2)//2) if eligible else ordinary
 check('exact-selected-medicine-recovery',actual,expected)
 stock=list(stock_pair);stock[preference]-=int(eligible)
 check('other-medicine-never-substituted',m.read(0x02001940+362,2),bytes(stock))
 state=m.call(S['ffta_job_state'],TARGET)
 check('empty-choice-does-not-lock',m.read(state+8,1)[0]&8,8 if eligible else 0)
 positive+=int(eligible);empty+=int(trigger and not stock_pair[preference])
check('positive-healing-controls',positive>0,True)
check('positive-empty-chosen-stock-controls',empty>0,True)
report=dict(passed=True,romSha1=meta['romSha1'],uiEvidence=str(prior),total=sum(counts.values()),checks=dict(counts),positive=positive,empty=empty,scope='UI-produced saved preference transferred to owned native executor target; not whole campaign playback')
(OUT/'auto-potion-selected-stock.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
