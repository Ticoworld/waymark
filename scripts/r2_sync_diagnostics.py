"""Extract only fixed numeric LC protocol observations from logcat in memory.
No raw logs, key logs, UI dumps or credentials are saved or printed.
"""
import argparse,collections,datetime,json,re
from h02_device import Device,ROOT
from r2_observe import APK

PATTERNS={
 'minimum':r'current min filtered block number: (\d+)',
 'filters_received':r'recieved block filters: start number: (\d+), filters count: (\d+), blocks count: (\d+)',
 'duplicate_or_discontinuous':r'start_number of block_filters message (\d+) is not continuous with min_filtered_block_number: (\d+)',
 'registered_start':r'startBlock=(\d+) \(hex=0x[0-9a-f]+\)',
}
def capture(label):
    d=Device('emulator-5580',APK);pid=d.shell('pidof','com.rjnr.pocketnode').decode().strip()
    if not pid.isdigit():raise ValueError()
    raw=d.shell('logcat','-d','--pid='+pid,'-v','threadtime').decode(errors='replace')
    events=[];counts=collections.Counter()
    for line in raw.splitlines():
        if not re.search(r'\b(?:ckb-light-client|SyncCoordinator)\s*:',line):continue
        for label_,pattern in PATTERNS.items():
            m=re.search(pattern,line)
            if m:events.append({'time':line[:18],'event':label_,'numbers':list(map(int,m.groups()))})
        for term in ('timeout','Failed','failed','disconnect','panic','cannot find peers which are proved','BlockFilterHashes'):
            if term in line:counts[term]+=1
    out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pid':int(pid),'counts':dict(counts),'events':events}
    f=ROOT/'runs/wo3b1-r2'/label
    with f.open('x') as stream:json.dump(out,stream,indent=2)
    print(json.dumps({'utc':out['utc'],'pid':pid,'counts':counts,'firstEvents':events[:4],'lastEvents':events[-6:]}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('label');a=p.parse_args();capture(a.label)
