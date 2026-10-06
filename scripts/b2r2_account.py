"""Supported account-1 creation and CUSTOM coverage. Public UI only, no DB writes."""
import argparse,time
from h02_device import Device
from r2_public_tap import APK,tap
from p3b1_ui import nodes,center
from b2_events import mark
EXPECTED='ckt1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqfd5qj9wprzkr3yy8v8409la029vl2j44g8qpweu'
def create(role):
    d=Device('emulator-5580',APK)
    tap(public_text='Settings');tap(public_text='Manage Wallets')
    icons=[n for n in nodes(d) if n.attrib.get('content-desc')=='Settings']
    if len(icons)!=1:raise ValueError('AMBIGUOUS_PARENT')
    x,y=center(icons[0]);d.shell('input','tap',str(x),str(y));time.sleep(1)
    tap(public_text='Add account')
    fields=[n for n in nodes(d) if n.attrib.get('class')=='android.widget.EditText']
    if len(fields)!=1:raise ValueError('ACCOUNT_NAME_FIELD')
    x,y=center(fields[0]);d.shell('input','tap',str(x),str(y));d.shell('input','text','B2%sAccount%s1');d.shell('input','keyevent','4')
    tap(public_text='Create');tap(public_text='Continue anyway');time.sleep(4)
    if not any(n.attrib.get('text')==EXPECTED for n in nodes(d)):raise ValueError('ACCOUNT_PUBLIC_IDENTITY')
    mark(role,'account1_created_and_identity_verified')
    d.shell('input','keyevent','4');d.shell('input','keyevent','4');time.sleep(1)
    tap(public_text='Wallet')
    # Manual account creation changes the selected preference before Gateway's
    # account-switch lifecycle runs. Explicit supported switching refreshes it.
    from p3b1_ui import tap as normal_tap
    normal_tap(d,'Switch');tap(public_text='ckt1qzda0c...7rmyth');time.sleep(2)
    normal_tap(d,'Switch');tap(public_text='B2 Account 1');time.sleep(2)
    from b2r2_coverage import set_floor
    set_floor(1)
    mark(role,'account1_custom_registration_requested')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('role',choices=['control','candidate']);a=p.parse_args()
    try:create(a.role)
    except Exception as e:print('ACCOUNT_AUTOMATION_REFUSED '+type(e).__name__);raise SystemExit(2)
