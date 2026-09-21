"""Native party sorting with a paid, away member, then return and cold save.

Reuse the paid-recovery helpers, but run only one acceptance/return. Initial
source eligibility and distinctive extra AP/preferences are declared inputs.
Sorting, travel, collection and saving are actual controller actions.
"""
import pathlib
SCOPE=__doc__
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/test-paid-recovery-cycle.py').read_text(encoding='utf-8')
prefix=source.split("stages=[('prepared',prepare)")[0]
assert prefix!=source
prefix=prefix.replace("'paid-recovery-cycle-'", "'sorted-dispatch-'")
prefix=prefix.replace("'paid-recovery-cycle-latest.json'", "'sorted-dispatch-latest.json'")
exec(compile(prefix,str(ROOT/'scripts/test-paid-recovery-cycle.py'),'exec'))
atexit.unregister(report)
helper_sha=sha(source.encode('utf-8'));failure=None


def extra(r):
    return r[0x1b40:0x1e70],r[0x1e80:0x1e98]


def sort():
    before=e.memory();queue=before[0x21c8:0x28cc]
    tap(8);tap(256,180)
    # Native party menu starts on Marche. Both story-member Select attempts
    # must be rejected, so neither leaves an armed generic swap behind.
    tap(4);tap(128);tap(4)
    check(e.memory()[0x80:0x1940]==before[0x80:0x1940], 'Marche and Montblanc remain fixed')
    check(extra(e.memory())==extra(before), 'Rejected story sort preserves extra data')
    tap(128);tap(4);tap(128);tap(4)
    after=e.memory();capture('sorted-away-Ford')
    expected=bytearray(before[0x80:0x1940])
    expected[528:792],expected[792:1056]=expected[792:1056],expected[528:792]
    check(after[0x80:0x1940]==expected, 'Native sorting moves complete away unit and no other records')
    ap=bytearray(before[0x1b40:0x1e70]);ap[68:102],ap[102:136]=ap[102:136],ap[68:102]
    prefs=bytearray(before[0x1e80:0x1e98]);prefs[2],prefs[3]=prefs[3],prefs[2]
    check(after[0x1b40:0x1e70]==ap, 'Extended AP follows sorted Ford')
    check(after[0x1e80:0x1e98]==prefs, 'Potion preference follows sorted Ford')
    check(half(after,0x3ae)==471 and half(after,0x3c0)&4, 'Away assignment follows actual Ford')
    check(half(after,0x2a6)==0 and not half(after,0x2b8)&4, 'Displaced member inherits no assignment')
    check(after[0x21c8:0x28cc]==queue, 'Sort preserves native dispatch queue')
    tap(1,180)


def collect_sorted():
    before=e.memory();before_gil=gil();original=record()
    check(original is not None, 'Sorted dispatch exists')
    initial_days=(original[1]>>2)|((original[2]&3)<<6)
    check(initial_days==20, 'Sorting consumes no dispatch days')
    previous=20
    for leg in range(1,13):
        travel(8 if leg%2 else 2,'sorted-return-travel-'+str(leg))
        current=record();check(current is not None,'Travel retains sorted dispatch')
        days=(current[1]>>2)|((current[2]&3)<<6)
        check(days<previous,'Native travel advances sorted dispatch');previous=days
        if days==0:break
        tap(1);tap(1)
    check(previous==0,'Full20-day native dispatch duration completed')
    for page in range(10):
        tap(256,240);capture('sorted-return-page-'+str(page))
        if item_count()==1 and half(e.memory(),0x3ae)==0:break
    after=e.memory()
    check(item_count()==1,'Exactly one native reward after sorted return')
    check(half(after,0x3ae)==0 and not half(after,0x3c0)&4,'Returned Ford clears his own assignment')
    check(half(after,0x2a6)==0 and not half(after,0x2b8)&4,'Other member remains unassigned')
    check(extra(after)==extra(before),'Dispatch return preserves both members extra AP and preferences')
    check(after[0x80:0x290]==before[0x80:0x290],'Story members survive sorting and return unchanged')
    check(gil()==before_gil,'Return charges no additional fee')
    world()


def prepare_paid():
    prepare()
    e.set_memory(0x1b40,bytes((i*7+13)%101 for i in range(816)))
    e.set_memory(0x1e80,bytes(i%3 for i in range(24)))
    accept(1)


def save_and_cold():
    global e
    before=e.memory()
    for key,wait in ((8,60),(16,60),(256,60),(256,60),(256,60),(64,20),(256,300)):tap(key,wait)
    sram=e.memory(0);(OUT/'sorted-return.sav').write_bytes(sram)
    values['sramSha1']=sha(sram)
    e.close();e=Emulator(private);e.set_memory(0,sram,0);e.run(3600)
    for key,wait in ((8,300),(256,300),(256,300),(256,300)):tap(key,wait)
    after=e.memory();capture('cold-sorted-return')
    for name,lo,hi in (('all24 roster records',0x80,0x1940),('inventory and extra AP',0x1940,0x1e70),('preferences',0x1e80,0x1e98)):
        check(after[lo:hi]==before[lo:hi],'Cold save retains '+name)
    check(gil()==35000 and item_count()==1,'One fee and reward persist after sorted cold save')
    check(seedpath.read_bytes()==seed,'Private seed unchanged')


try:
    e=Emulator(private)
    if '--resume' in sys.argv:
        prior_path=pathlib.Path(json.loads(latest.read_text())['report'])
        prior=json.loads(prior_path.read_text())
        assert prior['romSha1']==meta['romSha1'] and prior['seedSha1']==sha(seed)
        checks.extend(prior['checks']);completed.extend(prior['completed']);values.update(prior['values'])
        retained.update(report=str(prior_path),reportSha1=sha(prior_path.read_bytes()),completed=list(completed))
        anchor=next(r for r in reversed(prior['observations']) if r['label']==completed[-1])
        observations.append(anchor);folder=pathlib.Path(anchor['directory'])
        for ext,key in (('state','stateSha1'),('ram','ramSha1')):
            assert sha((folder/(anchor['label']+'.'+ext)).read_bytes())==anchor[key]
        e.load(folder/(anchor['label']+'.state'));e.run(1)
    for label,fn in [('paid-before-sort',prepare_paid),('sorted',sort),('returned-after-sort',collect_sorted),('cold',save_and_cold)]:
        if label in completed:continue
        fn();capture(label);completed.append(label);report(False,capture_failure=False)
except BaseException as error:
    failure=repr(error)
    if e is not None:capture('failure')
finally:
    if e is not None:e.close();e=None
result=report(failure is None,capture_failure=False)
result.update(scope=SCOPE,failure=failure,helperSha1=helper_sha)
(OUT/'report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(passed=failure is None,checks=len(checks),failure=failure,report=str(OUT/'report.json'))))
assert failure is None,failure
