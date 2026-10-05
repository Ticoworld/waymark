"""Check actual fixture material is absent from experiment docs/scripts/new outputs.
No secret values or matched snippets are emitted. Does not scan private/ itself.
This is scoped leak detection, not a forensic erasure guarantee.
"""
import json, subprocess
from p3_fixture import ROOT,FIXTURE,derive,verify

def main():
    obj=json.loads(FIXTURE.read_text(encoding='utf-8'));verify(obj)
    needles=[]
    for item in obj['wallets']:
        words=item.get('mnemonic')
        if words:
            for separator in (' ','\n','\r\n',',',', '):needles.append(separator.join(words.split()).encode())
            k=derive(words,item['public']['derivationPath'])
        else:k=bytes.fromhex(item['privateKey'].removeprefix('0x'))
        needles.extend([k,k.hex().encode(),k.hex().upper().encode()])
    files=[]
    # PowerShell redirection can produce UTF-16 logs; check both encodings.
    text_needles=[n for n in needles if all(b<128 for b in n)]
    needles.extend(n.decode('ascii').encode(enc) for n in text_needles for enc in ('utf-16-le','utf-16-be'))
    for root in (ROOT/'docs',ROOT/'scripts',ROOT/'runs/wo3-setup',ROOT/'runs/wo3b1'):
        files.extend(p for p in root.rglob('*') if p.is_file() and not any(s in ('venv','__pycache__') for s in p.parts))
    for path in files:
        raw=path.read_bytes()
        if any(n in raw for n in needles):raise ValueError()
    tracked=subprocess.run(['git','ls-files','-z'],cwd=ROOT,capture_output=True,check=True).stdout.decode().split('\0')
    if any(p.startswith(('private/','runs/','repos/')) for p in tracked):raise ValueError()
    result=subprocess.run(['git','check-ignore',str(FIXTURE)],cwd=ROOT,capture_output=True)
    if result.returncode!=0:raise ValueError()
    print('PRIVATE_BOUNDARY_AUDIT_PASS; '+str(len(files))+' docs/scripts/new-output files checked; no fixture words or derived private key found')

if __name__=='__main__':
    try:main()
    except Exception:
        print('PRIVATE_BOUNDARY_AUDIT_FAILED; no values emitted');raise SystemExit(2)
