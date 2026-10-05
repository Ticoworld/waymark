"""Bounded public Home-screen watcher. Never run during key/PIN input."""
import argparse,datetime,json,re,time
from h02_device import ROOT
from p3b1_ui import device,nodes

def main():
    p=argparse.ArgumentParser();p.add_argument('--label',required=True);p.add_argument('--seconds',type=int,default=300);p.add_argument('--until-synced',action='store_true');a=p.parse_args()
    out=ROOT/'runs/wo3b1-r2'/a.label;out.parent.mkdir(parents=True,exist_ok=True)
    d=device();start=time.monotonic()
    consecutive=0
    with out.open('x',encoding='utf-8') as f:
        while True:
            ns=nodes(d)
            texts=[n.attrib.get('text','') for n in ns if n.attrib.get('class')!='android.widget.EditText']
            safe=[s for s in texts if re.fullmatch(r'(?:CKB Testnet|Syncing|\u2713 Synced|Synced|Up to date|Catching up from [\d,]+ to [\d,]+|[\d,]+\.[\d]+ CKB|\d+ peers connected|Finish syncing before making transactions)',s)]
            row={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed':round(time.monotonic()-start,2),'publicStatus':safe}
            pid=d.shell('pidof','com.rjnr.pocketnode').decode().strip()
            if pid.isdigit():
                raw=d.shell('logcat','-d','--pid='+pid,'-v','brief','ckb-light-client:D','*:S').decode(errors='replace')
                minimum=re.findall(r'current min filtered block number: (\d+)',raw)
                row['nativeLastLoggedMinimum']=int(minimum[-1]) if minimum else None
                del raw
            line=json.dumps(row);f.write(line+'\n');f.flush();print(line,flush=True)
            peers=any(re.fullmatch(r'[1-9]\d* peers connected',s) for s in safe)
            funded=any(re.fullmatch(r'[\d,]+\.\d+ CKB',s) and float(s[:-4].replace(',',''))>1 for s in safe)
            synced=('\u2713 Synced' in safe or 'Up to date' in safe) and 'CKB Testnet' in safe and peers and funded and 'Finish syncing before making transactions' not in safe
            consecutive=consecutive+1 if synced else 0
            if a.until_synced and consecutive>=2:
                print('UI_SYNC_SETTLED; exact frozen acceptance still required',flush=True);break
            if time.monotonic()-start>=a.seconds:break
            time.sleep(min(30,max(0,a.seconds-(time.monotonic()-start))))

if __name__=='__main__':main()
