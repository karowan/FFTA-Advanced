"""Local headless mGBA/libretro harness. Never writes the user's saves."""
import ctypes as C
import json, pathlib, sys
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[1]
class Game(C.Structure):
    _fields_=[('path',C.c_char_p),('data',C.c_void_p),('size',C.c_size_t),('meta',C.c_char_p)]
class Descriptor(C.Structure):
    _fields_=[('flags',C.c_uint64),('ptr',C.c_void_p),('offset',C.c_size_t),('start',C.c_size_t),('select',C.c_size_t),('disconnect',C.c_size_t),('length',C.c_size_t),('addrspace',C.c_char_p)]
class MemoryMap(C.Structure):
    _fields_=[('descriptors',C.POINTER(Descriptor)),('count',C.c_uint)]
ENV=C.CFUNCTYPE(C.c_bool,C.c_uint,C.c_void_p)
VIDEO=C.CFUNCTYPE(None,C.c_void_p,C.c_uint,C.c_uint,C.c_size_t)
AUDIO=C.CFUNCTYPE(None,C.c_int16,C.c_int16)
BATCH=C.CFUNCTYPE(C.c_size_t,C.c_void_p,C.c_size_t)
POLL=C.CFUNCTYPE(None)
INPUT=C.CFUNCTYPE(C.c_int16,C.c_uint,C.c_uint,C.c_uint,C.c_uint)
class Emulator:
    def __init__(self,rom):
        self.core=C.CDLL(str(ROOT/'tools/mgba-test-core/mgba_libretro.dll'))
        self.keys=0; self.frame=None; self.pixel=0; self.maps={}
        self.directory=str(ROOT/'build/test').encode(); pathlib.Path(self.directory.decode()).mkdir(parents=True,exist_ok=True)
        @ENV
        def environment(cmd,data):
            if cmd & 0xffff==36:
                mm=C.cast(data,C.POINTER(MemoryMap)).contents
                self.maps={mm.descriptors[i].start:(mm.descriptors[i].ptr,mm.descriptors[i].length) for i in range(mm.count)}
                return True
            if cmd in (9,31): C.cast(data,C.POINTER(C.c_char_p))[0]=self.directory; return True
            if cmd==10: self.pixel=C.cast(data,C.POINTER(C.c_int))[0]; return True
            if cmd==15: return False
            if cmd==17: C.cast(data,C.POINTER(C.c_bool))[0]=False; return True
            if cmd==3: C.cast(data,C.POINTER(C.c_bool))[0]=False; return True
            if cmd==18: C.cast(data,C.POINTER(C.c_bool))[0]=True; return True
            return False
        @VIDEO
        def video(ptr,w,h,pitch):
            if ptr and ptr!=C.c_void_p(-1).value:self.frame=(C.string_at(ptr,pitch*h),w,h,pitch,self.pixel)
        @INPUT
        def inputs(port,device,index,key): return int(bool(self.keys&(1<<key))) if port==0 and key<16 else 0
        self.callbacks=[environment,video,AUDIO(lambda l,r:None),BATCH(lambda p,n:n),POLL(lambda:None),inputs]
        for name,cb in zip(('environment','video_refresh','audio_sample','audio_sample_batch','input_poll','input_state'),self.callbacks):getattr(self.core,'retro_set_'+name)(cb)
        self.core.retro_init()
        self.core.retro_load_game.argtypes=[C.POINTER(Game)];self.core.retro_load_game.restype=C.c_bool
        self.rom=C.create_string_buffer(pathlib.Path(rom).read_bytes());self.game=Game(str(rom).encode(),C.cast(self.rom,C.c_void_p),len(self.rom)-1,None)
        if not self.core.retro_load_game(C.byref(self.game)):
            self.game=None;self.close();raise AssertionError('ROM load failed')
        self.core.retro_serialize_size.restype=C.c_size_t
        for fn in ('retro_serialize','retro_unserialize'):
            getattr(self.core,fn).argtypes=[C.c_void_p,C.c_size_t];getattr(self.core,fn).restype=C.c_bool
        self.core.retro_get_memory_size.argtypes=[C.c_uint];self.core.retro_get_memory_size.restype=C.c_size_t
        self.core.retro_get_memory_data.argtypes=[C.c_uint];self.core.retro_get_memory_data.restype=C.c_void_p
    def run(self,n,keys=0):
        self.keys=keys
        for _ in range(n):self.core.retro_run()
        self.keys=0
    def load(self,p):
        b=pathlib.Path(p).read_bytes();buf=C.create_string_buffer(b);assert self.core.retro_unserialize(buf,len(b))
    def save(self,p):
        n=self.core.retro_serialize_size();b=C.create_string_buffer(n);assert self.core.retro_serialize(b,n);pathlib.Path(p).write_bytes(b.raw)
    def region(self,kind):
        if kind==2:return self.maps[0x02000000]
        return self.core.retro_get_memory_data(kind),self.core.retro_get_memory_size(kind)
    def memory(self,kind=2):return C.string_at(*self.region(kind))
    def set_memory(self,offset,data,kind=2):
        ptr,size=self.region(kind);assert offset>=0 and offset+len(data)<=size
        C.memmove(ptr+offset,data,len(data))
    def screenshot(self,p):
        raw,w,h,pitch,pixel=self.frame
        if pixel==1: im=Image.frombytes('RGB', (w,h),raw,'raw','BGRX',pitch)
        else:
            pixels=[]
            for y in range(h):
                for x in range(w):
                    v=int.from_bytes(raw[y*pitch+x*2:y*pitch+x*2+2],'little')
                    if pixel==2:r,g,b=(v>>11)&31,(v>>5)&63,v&31;g=g*255//63
                    else:r,g,b=(v>>10)&31,(v>>5)&31,v&31;g=g*255//31
                    pixels.append((r*255//31,g,b*255//31))
            im=Image.new('RGB',(w,h));im.putdata(pixels)
        im.resize((w*3,h*3),Image.Resampling.NEAREST).save(p)
    def close(self):
        # Idempotent: release the native core first, then drop every buffer
        # and callback closure so the instance does not depend on cyclic GC
        # to free its ROM copy, frame, memory-map pointers and core handle.
        core=getattr(self,'core',None)
        if core is None:return
        self.core=None
        try:
            if getattr(self,'game',None) is not None:core.retro_unload_game()
        finally:
            try:core.retro_deinit()
            finally:
                self.game=None;self.rom=None;self.frame=None;self.maps={};self.callbacks=[]
                if hasattr(C,'windll'):C.windll.kernel32.FreeLibrary(C.c_void_p(core._handle))
    def __enter__(self):return self
    def __exit__(self,*_):self.close()
    def __del__(self):
        try:self.close()
        except Exception:pass
if __name__=='__main__':
    cfg=json.loads(pathlib.Path(sys.argv[1]).read_text());e=Emulator(ROOT/cfg['rom'])
    if cfg.get('load'):e.load(ROOT/cfg['load'])
    if cfg.get('saveRAM'):
        data=(ROOT/cfg['saveRAM']).read_bytes();e.set_memory(0,data,0)
    for offset,data in cfg.get('writes',[]):e.set_memory(int(offset,0),bytes.fromhex(data))
    for frames,keys in cfg.get('steps',[]):e.run(frames,keys)
    out=ROOT/cfg.get('out','build/test/current');e.save(str(out)+'.state');e.screenshot(str(out)+'.png')
    pathlib.Path(str(out)+'.ram').write_bytes(e.memory());pathlib.Path(str(out)+'.srm').write_bytes(e.memory(0))
    print(json.dumps({'state':str(out)+'.state','screenshot':str(out)+'.png','memoryBytes':len(e.memory()),'pixelFormat':e.pixel,'gameKeys':C.string_at(e.maps[0x03000000][0],8).hex()}));e.close()
