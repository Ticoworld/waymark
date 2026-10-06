"""Append host free-space metadata; never inspect fixture contents."""
import argparse,datetime,json,shutil
from h02_device import ROOT
def sample(role,event):
    if role not in ('source','control','candidate'):raise ValueError()
    total,used,free=shutil.disk_usage(ROOT)
    row={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'event':event,'total':total,'free':free}
    with (ROOT/'runs/wo3b2'/role/'disk-samples.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
    if free<1.5*2**30:raise RuntimeError('LIVE_STORAGE_RESERVE')
    print(json.dumps(row));return row
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('role');p.add_argument('event');a=p.parse_args();sample(a.role,a.event)
