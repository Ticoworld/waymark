"""Observe public Pocket/auth UI tags only; no raw hierarchy or credential output."""
import json
import re
import xml.etree.ElementTree as ET
from p3c_r1_probe import adb

def state():
    path='/data/local/tmp/h02-r1-public-ui.xml'
    adb('shell','uiautomator','dump',path)
    raw=adb('shell','cat',path)
    root=ET.fromstring(raw[raw.index('<?xml'):])
    tags=set();system_auth=False;home=False;auth=False
    for node in root.iter('node'):
        package=node.attrib.get('package',''); rid=node.attrib.get('resource-id','')
        if package=='com.rjnr.pocketnode':
            # Only known automation tags, never arbitrary text/editable content.
            if re.fullmatch(r'(home|auth|pin)-[a-z0-9-]+',rid):tags.add(rid)
            if rid=='home-balance-row':home=True
            if rid=='auth-use-pin':auth=True
        if package in ('com.android.systemui','com.samsung.android.biometrics.app.setting'):
            if any(s in rid.lower() for s in ['biometric','fingerprint','credential','auth_dialog','prompt']):system_auth=True
    return {'homeVisible':home,'authScreenVisible':auth,'systemAuthUiVisible':system_auth,'publicTags':sorted(tags)}

if __name__=='__main__':
    try:print(json.dumps(state()))
    except Exception:print('PUBLIC_UI_OBSERVATION_REFUSED');raise SystemExit(2)
