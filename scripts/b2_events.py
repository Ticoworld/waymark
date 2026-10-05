"""Public experiment timing markers. Arguments must never contain credentials."""
import argparse,datetime,json,re,time
from h02_device import ROOT

def mark(role,event):
    if role not in ('source','control','candidate') or not re.fullmatch('[a-z][a-z0-9_-]+',event):raise ValueError()
    path=ROOT/'runs/wo3b2'/role/'events.jsonl';path.parent.mkdir(parents=True,exist_ok=True)
    row={'role':role,'event':event,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'monotonic':time.monotonic()}
    with path.open('a') as f:f.write(json.dumps(row)+'\n')
    print(json.dumps(row));return row

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('role');p.add_argument('event');a=p.parse_args();mark(a.role,a.event)
