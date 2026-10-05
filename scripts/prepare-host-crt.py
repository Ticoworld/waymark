"""Unpack hash-pinned MSVC runtime/header prerequisites into runs only.
Uses the existing Windows SDK and Rust-bundled linker; no system installation.
"""
import hashlib,json,subprocess,zipfile
from pathlib import Path
root=Path(__file__).resolve().parent.parent
out=root/'runs/wo2/msvc';out.mkdir(parents=True,exist_ok=True)
for name,archive in [('msvc-crt.json','crt.vsix'),('msvc-crt-store.json','crt-store.vsix'),('msvc-crt-headers.json','crt-headers.vsix')]:
    p=json.loads((root/'scripts'/name).read_text())['payload'];f=out/archive
    if not f.exists() or hashlib.sha256(f.read_bytes()).hexdigest()!=p['sha256'].lower():
        subprocess.run(['curl.exe','-fL','--retry','3','--connect-timeout','15','--max-time','240','-C','-','-o',str(f),p['url']],check=True)
    assert hashlib.sha256(f.read_bytes()).hexdigest()==p['sha256'].lower(),'download hash mismatch'
    with zipfile.ZipFile(f) as z:
        for n in z.namelist():
            if n.startswith('Contents/') and not n.endswith('/'):
                d=out/Path(n).relative_to('Contents');assert d.resolve().is_relative_to(out.resolve())
                d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes(z.read(n))
    print('Verified and extracted '+name)
