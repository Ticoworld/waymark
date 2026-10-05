"""Explicit emulator-only normal Pocket UI driver; no screenshots or raw XML logs."""
import argparse,json,re,subprocess,time,xml.etree.ElementTree as ET
from pathlib import Path
from h02_device import Device,ROOT,APP
APK='903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f'

def device():return Device('emulator-5580',APK)

def nodes(d):
    path='/data/local/tmp/h02-b1-ui.xml'
    d.shell('sh','-c','umask 077; uiautomator dump '+path+' >/dev/null')
    raw=d.shell('cat',path);d.shell('rm','-f',path)
    return list(ET.fromstring(raw).iter('node'))

def center(n):
    v=list(map(int,re.findall(r'\d+',n.attrib['bounds'])))
    return (v[0]+v[2])//2,(v[1]+v[3])//2

def tap(d,text):
    matches=[n for n in nodes(d) if n.attrib.get('text')==text or n.attrib.get('resource-id')==text or n.attrib.get('content-desc')==text]
    if len(matches)!=1:raise ValueError('AMBIGUOUS_PUBLIC_UI_SELECTOR')
    x,y=center(matches[0]);d.shell('input','tap',str(x),str(y))

def view(d):
    # Defense in depth: never print a phrase word or any editable field contents.
    fixture=json.loads((ROOT/'private/pocket-disposable-fixture.json').read_text())
    words=set(fixture['wallets'][0]['mnemonic'].split())
    for n in nodes(d):
        a=n.attrib;t=a.get('text','');desc=a.get('content-desc','')
        if not (t or desc or a.get('resource-id')):continue
        if a.get('class')=='android.widget.EditText':t='[EDITABLE REDACTED]'
        def redact(s):return re.sub(r'[A-Za-z]+',lambda m:'[REDACTED]' if m[0].lower() in words else m[0],s)
        print(json.dumps({'text':redact(t),'description':redact(desc),'id':a.get('resource-id'),'bounds':a.get('bounds'),'class':a.get('class')}))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['view','tap','launch','back']);p.add_argument('--text');a=p.parse_args();d=device()
    if a.action=='view':view(d)
    elif a.action=='tap':tap(d,a.text)
    elif a.action=='back':d.shell('input','keyevent','4')
    else:d.shell('am','start','-n',APP+'/.MainActivity')

if __name__=='__main__':
    try:main()
    except Exception as e:
        print('B1_UI_REFUSED '+type(e).__name__);raise SystemExit(2)
