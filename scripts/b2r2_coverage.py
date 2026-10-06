"""Set selected account's historical floor through normal Settings UI."""
import argparse,time
from p3b1_ui import device,nodes,center
from r2_public_tap import tap
FLOORS={0:22369937,1:22647000}
def set_floor(index):
    d=device();suffix='myth' if index==0 else 'pweu'
    if not any(n.attrib.get('text')=='ckt1qz...'+suffix for n in nodes(d)):raise ValueError('ACTIVE_PUBLIC_IDENTITY')
    tap(public_text='Settings');tap(public_text='Sync Options');tap(public_text='From a specific date')
    fields=[n for n in nodes(d) if n.attrib.get('class')=='android.widget.EditText']
    if len(fields)!=1:raise ValueError('COVERAGE_FIELD')
    x,y=center(fields[0]);d.shell('input','tap',str(x),str(y));d.shell('input','keycombination','113','29');d.shell('input','text',str(FLOORS[index]))
    if not any(n.attrib.get('text')==str(FLOORS[index]) for n in nodes(d)):raise ValueError('COVERAGE_INPUT')
    d.shell('input','keyevent','4');tap(public_id='sync-sheet-apply');tap(public_text='Wallet');time.sleep(2)
    print('NORMAL_COVERAGE_SET account='+str(index)+' floor='+str(FLOORS[index]))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('index',type=int,choices=[0,1]);a=p.parse_args();set_floor(a.index)
