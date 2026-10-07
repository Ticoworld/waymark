"""Ephemeral UI observation: retain known resource IDs only, never text/input."""
import argparse
import datetime
import re
import xml.etree.ElementTree as ET
import h02_package as p
from h02_device import ROOT, APP
from p3c_r1_probe import adb


def state():
    # /dev/tty streams the dump; no hierarchy file is created on host or phone.
    raw = adb('exec-out','uiautomator','dump','/dev/tty')
    start = raw.find('<?xml')
    end = raw.find('</hierarchy>',start)
    p.require(start>=0 and end>=start,'ui-stream-unavailable')
    root = ET.fromstring(raw[start:end+len('</hierarchy>')])
    tags=set(); labels=set(); packages=set()
    allowed={'Send','Receive','Sync','Activity','Testnet','Wallet','Use PIN',
             'Unlock Pocket Node','Authenticate to access your wallet','OK'}
    for node in root.iter('node'):
        packages.add(node.attrib.get('package',''))
        if node.attrib.get('package')==APP:
            rid=node.attrib.get('resource-id','')
            if re.fullmatch(r'(home|auth|pin)-[a-z0-9-]+',rid):tags.add(rid)
            if node.attrib.get('text') in allowed:labels.add(node.attrib['text'])
    return {'publicTags':sorted(tags),'knownStaticLabels':sorted(labels),'packages':sorted(packages),
            'homeVisible':'home-balance-row' in tags or {'Send','Receive','Testnet'}.issubset(labels),
            'authScreenVisible':'auth-use-pin' in tags or 'Use PIN' in labels,
            'credentialRetained':False,'rawHierarchyRetained':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('label',choices=['unlocked','unlocked-confirmed','after-relaunch','after-restart-unlocked'])
    args=parser.parse_args()
    out=ROOT/'runs/wo3c-r1a'/('ui-'+args.label+'.json')
    try:
        p.require(not out.exists(),'ui-result-exists')
        result=state()
        result['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        with out.open('xb') as stream:stream.write(p.encode(result))
        print(p.encode(result).decode())
    except Exception as e:
        print('R1A_UI_REFUSED '+type(e).__name__+((' '+str(e)) if isinstance(e,p.Refused) else ''))
        raise SystemExit(2)
