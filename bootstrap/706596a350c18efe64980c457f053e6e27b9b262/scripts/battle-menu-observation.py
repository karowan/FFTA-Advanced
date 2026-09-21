"""Bounded, deterministic observation of the original native turn menu."""
import json,pathlib
ANCHOR=json.loads((pathlib.Path(__file__).parent/'fixtures/native-turn-menu.json').read_text())

def menu_visible(emulator):
    if emulator.frame is None:return False
    raw,width,height,pitch,pixel=emulator.frame
    if (width,height)!=(ANCHOR['width'],ANCHOR['height']):return False
    def read(x,y):
        if pixel==1:
            offset=y*pitch+x*4
            channels=raw[offset:offset+3]
        else:
            offset=y*pitch+x*2
            value=int.from_bytes(raw[offset:offset+2],'little')
            if pixel==2:
                channels=((value>>11&31)*255//31,(value>>5&63)*255//63,(value&31)*255//31)
            else:
                channels=((value>>10&31)*255//31,(value>>5&31)*255//31,(value&31)*255//31)
        return channels
    for x,y in ANCHOR['points']:
        if min(read(x,y))<ANCHOR['threshold']:return False
    for x,y in ANCHOR['darkPoints']:
        if max(read(x,y))>ANCHOR['darkThreshold']:return False
    return True

def wait_for_menu(emulator,limit=1800,step=10):
    """Observe without button presses; fail when the bounded frame budget ends."""
    if limit<0 or step<=0:raise ValueError('Invalid frame budget')
    elapsed=0
    while not menu_visible(emulator):
        if elapsed>=limit:raise AssertionError('Native Wait/Status menu did not appear within frame budget')
        frames=min(step,limit-elapsed);emulator.run(frames);elapsed+=frames
    return elapsed
