"""Local, user-bound Windows DPAPI storage for image-provider API credentials.

Browser setup uses a loopback-only form. Never logs request bodies or secrets.
Keys are decrypted only for the corresponding provider's API requests.
"""
import argparse, ctypes, json, secrets
from ctypes import wintypes
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT/'.local/image-api-secrets.json'
NAMES = ('GEMINI_API_KEY', 'FAL_KEY', 'BFL_API_KEY', 'IDEOGRAM_API_KEY')

class Blob(ctypes.Structure):
    _fields_ = [('size', wintypes.DWORD), ('data', ctypes.POINTER(ctypes.c_ubyte))]

def crypt(raw, decrypt=False):
    buffer = ctypes.create_string_buffer(raw)
    source = Blob(len(raw), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte)))
    target = Blob()
    library = ctypes.WinDLL('crypt32', use_last_error=True)
    if decrypt:
        ok = library.CryptUnprotectData(ctypes.byref(source), None, None, None, None, 1, ctypes.byref(target))
    else:
        ok = library.CryptProtectData(ctypes.byref(source), 'FFTA image provider credential', None, None, None, 1, ctypes.byref(target))
    if not ok:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        return ctypes.string_at(target.data, target.size)
    finally:
        kernel = ctypes.WinDLL('kernel32')
        kernel.LocalFree.argtypes = [ctypes.c_void_p]
        kernel.LocalFree(target.data)

def read_key(name):
    assert name in NAMES
    data = json.loads(STORE.read_text())
    return crypt(bytes.fromhex(data[name]), True).decode()

def save_key(name, value):
    assert name in NAMES and 15 <= len(value) <= 1024
    data = json.loads(STORE.read_text()) if STORE.exists() else {}
    data[name] = crypt(value.encode()).hex()
    STORE.parent.mkdir(exist_ok=True)
    temp = STORE.with_suffix('.tmp')
    temp.write_text(json.dumps(data, indent=2)+'\n')
    temp.replace(STORE)

def serve(port):
    token = secrets.token_urlsafe(24)
    origin = f'http://127.0.0.1:{port}'
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args): pass
        def do_GET(self):
            if self.path != '/'+token:
                self.send_error(404); return
            options = ''.join(f'<option>{name}</option>' for name in NAMES)
            content = f'''<!doctype html><html><meta charset="utf-8"><title>Local image API setup</title>
            <style>body{{font:18px system-ui;background:#15231d;color:#eef0e8;max-width:650px;margin:60px auto;padding:20px}}input,select,button{{font:inherit;display:block;padding:12px;margin:12px 0;width:100%;box-sizing:border-box}}</style>
            <h1>Save image API access locally</h1><p>The key stays on this computer, encrypted to your Windows account. It will only be sent to its own API provider.</p>
            <form method="post" action="/{token}"><label>Provider credential<select name="provider">{options}</select></label>
            <label>API key<input name="key" type="password" autocomplete="off" required></label><button>Save encrypted key</button></form></html>'''.encode()
            self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8')
            self.send_header('Cache-Control','no-store'); self.send_header('Content-Security-Policy',"default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'")
            self.end_headers(); self.wfile.write(content)
        def do_POST(self):
            if self.path != '/'+token or self.headers.get('Origin') != origin:
                self.send_error(403); return
            size = int(self.headers.get('Content-Length','0'))
            if not 0 < size < 4096:
                self.send_error(400); return
            data = parse_qs(self.rfile.read(size).decode())
            name, key = data.get('provider',[''])[0], data.get('key',[''])[0].strip()
            if name not in NAMES or not 15 <= len(key) <= 1024:
                self.send_error(400); return
            save_key(name, key)
            key = None
            self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8'); self.send_header('Cache-Control','no-store'); self.end_headers()
            self.wfile.write(f'<h1>{name} saved securely on this computer</h1><p>No key value is displayed or logged.</p>'.encode())
    print(json.dumps({'localSetupUrl':origin+'/'+token}), flush=True)
    HTTPServer(('127.0.0.1',port),Handler).serve_forever()

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--serve', type=int)
    args=parser.parse_args()
    if args.serve: serve(args.serve)
