"""Normal public navigation for per-account balance/history/DAO reconciliation."""
import argparse,datetime,json,re,time
from h02_device import ROOT
from p3b1_ui import device,nodes,center,tap as normal_tap
from r2_public_tap import tap
from h02_package import require,encode,secret_gate
def nav(d,text):
    matches=[n for n in nodes(d) if n.attrib.get('text')==text and center(n)[1]>2100]
    require(len(matches)==1,'bottom-nav-selector');x,y=center(matches[0]);d.shell('input','tap',str(x),str(y));time.sleep(2)
def capture(label):
    out=ROOT/'runs/wo3b2'/label;require(not out.exists(),'reconcile-output-exists');d=device();observations=[]
    nav(d,'Wallet')
    for i,selector,suffix in [(0,'ckt1qzda0c...7rmyth','myth'),(1,'B2 Account 1','pweu')]:
        normal_tap(d,'Switch');tap(public_text=selector);time.sleep(5)
        texts=[n.attrib.get('text','') for n in nodes(d)]
        require('CKB Testnet' in texts and 'ckt1qz...'+suffix in texts,'active-account-identity')
        balances=[s for s in texts if re.fullmatch(r'[\d,]+\.\d+ CKB',s)]
        nav(d,'Activity');time.sleep(3)
        nav(d,'DAO');time.sleep(6)
        # These are public DAO page labels only. Never run on security screens.
        texts=[n.attrib.get('text','') for n in nodes(d) if n.attrib.get('class')!='android.widget.EditText']
        allowed=[s for s in texts if re.fullmatch(r'(?:[\d,]+\.\d+ CKB|[+~]?[\d,.]+ CKB|Deposited|Locked|Unlockable|Withdrawing|Active|Completed|No deposits yet|Deposit|Withdraw|Unlock|Nervos DAO|.*epochs?.*|.*CKB locked.*)',s,re.I)]
        row={'accountIndex':i,'homeBalances':balances,'daoLabels':allowed};secret_gate(encode(row));observations.append(row)
        nav(d,'Wallet')
    result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Normal per-account Home, Activity and DAO navigation; no transactions','observations':observations}
    out.write_bytes(encode(result));print(json.dumps(result,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('label');a=p.parse_args();capture(a.label)
