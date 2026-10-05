"""Private fixture custody. Decrypt one Pocket PNBK using one supplied PIN;
verify derived public identities before saving. No credential CLI arguments.
Only public identities/fixed errors are emitted. Never retries or guesses PINs.
"""
import argparse, hashlib, hmac, json, re, struct, unicodedata
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2.low_level import hash_secret_raw, Type
from h02_package import script_from_address, CODE_HASH

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'private/pocket-disposable-fixture.json'
ORDER=0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

def pub(k):
    return ec.derive_private_key(int.from_bytes(k,'big'),ec.SECP256K1()).public_key().public_bytes(Encoding.X962,PublicFormat.CompressedPoint)

def derive(words,path):
    words=unicodedata.normalize('NFKD',words)
    seed=hashlib.pbkdf2_hmac('sha512',words.encode(),b'mnemonic',2048)
    h=hmac.new(b'Bitcoin seed',seed,'sha512').digest();k,c=h[:32],h[32:]
    if not re.fullmatch(r"m(?:/[0-9]+'?){5}",path):raise ValueError()
    for part in path.split('/')[1:]:
        i=int(part.rstrip("'"))+(0x80000000 if part.endswith("'") else 0)
        data=(b'\0'+k if i>=0x80000000 else pub(k))+struct.pack('>I',i)
        h=hmac.new(c,data,'sha512').digest();delta=int.from_bytes(h[:32],'big')
        n=(delta+int.from_bytes(k,'big'))%ORDER
        if delta>=ORDER or n==0:raise ValueError()
        k,c=n.to_bytes(32,'big'),h[32:]
    return k

def validate_words(words):
    dictionary=(ROOT/'scripts/bip39-english.txt').read_text().split()
    pieces=words.split()
    if len(pieces) not in (12,15,18,21,24):raise ValueError()
    bits=''.join(format(dictionary.index(w),'011b') for w in pieces)
    ent=len(bits)*32//33
    raw=int(bits[:ent],2).to_bytes(ent//8,'big')
    if bits[ent:]!=''.join(format(b,'08b') for b in hashlib.sha256(raw).digest())[:len(bits)-ent]:raise ValueError()

def identity(k,w):
    public=pub(k);args=hashlib.blake2b(public,digest_size=32,person=b'ckb-default-hash').digest()[:20]
    packed=struct.pack('<IIII',73,16,48,49)+bytes.fromhex(CODE_HASH)+b'\x01'+struct.pack('<I',20)+args
    for net,field in [('MAINNET','mainnetAddress'),('TESTNET','testnetAddress')]:
        if script_from_address(w[field],net)!=packed.hex():raise ValueError()
    return {'fixture':'pocket-disposable-d2','walletId':w['walletId'],'path':w['derivationPath'],
      'publicKey':'0x'+public.hex(),'mainnetAddress':w['mainnetAddress'],'testnetAddress':w['testnetAddress'],
      'lockScript':{'code_hash':'0x'+CODE_HASH,'hash_type':'type','args':'0x'+args.hex()},
      'packedScript':'0x'+packed.hex(),'scriptHash':'0x'+hashlib.blake2b(packed,digest_size=32,person=b'ckb-default-hash').hexdigest(),'result':'MATCH'}

def address(k,hrp):
    args=hashlib.blake2b(pub(k),digest_size=32,person=b'ckb-default-hash').digest()[:20]
    raw=b'\0'+bytes.fromhex(CODE_HASH)+b'\x01'+args
    bits=''.join(format(b,'08b') for b in raw);bits+='0'*((-len(bits))%5)
    values=[int(bits[i:i+5],2) for i in range(0,len(bits),5)]
    mod=1
    for v in [ord(x)>>5 for x in hrp]+[0]+[ord(x)&31 for x in hrp]+values+[0]*6:
        top=mod>>25;mod=((mod&0x1ffffff)<<5)^v
        for i,g in enumerate([0x3b6a57b2,0x26508e6d,0x1ea119fa,0x3d4233dd,0x2a1462b3]):
            if (top>>i)&1:mod^=g
    mod^=0x2bc830a3
    return hrp+'1'+''.join('qpzry9x8gf2tvdw0s3jn54khce6mua7l'[v] for v in values+[(mod>>(5*(5-i)))&31 for i in range(6)])

def prospective():
    data=json.loads(FIXTURE.read_text(encoding='utf-8'));verify(data)
    w={'walletId':'PROPOSED_ACCOUNT_1_NOT_CREATED','derivationPath':"m/44'/309'/1'/0/0"}
    k=derive(data['wallets'][0]['mnemonic'],w['derivationPath'])
    w.update(mainnetAddress=address(k,'ckb'),testnetAddress=address(k,'ckt'))
    public=identity(k,w);public['result']='DERIVED_ONLY_NOT_A_PHONE_ACCOUNT'
    (ROOT/'runs/wo3-setup/proposed-account1-public.json').write_text(json.dumps(public,indent=2));print(json.dumps(public,indent=2))

def verify(data):
    result=[]
    for item in data['wallets']:
        w=item['public'];words=item.get('mnemonic')
        if words:
            validate_words(words);k=derive(words,w['derivationPath'])
            if item.get('privateKey') and k.hex()!=item['privateKey'].removeprefix('0x').lower():raise ValueError()
        else:k=bytes.fromhex(item['privateKey'].removeprefix('0x'))
        result.append(identity(k,w))
    return result

def decrypt_backup(b,pin):
    if len(b)<49 or b[:4]!=b'PNBK':raise ValueError()
    salt,iv=b[5:21],b[21:33]
    if b[4]==2:key=hash_secret_raw(pin.encode(),salt,3,65536,4,32,Type.ID,19)
    elif b[4]==1:key=hashlib.pbkdf2_hmac('sha256',pin.encode(),salt,600000,32)
    else:raise ValueError()
    return json.loads(AESGCM(key).decrypt(iv,b[33:],None))

def recover(gui):
    if FIXTURE.exists():raise ValueError()
    phone=json.loads((ROOT/'runs/wo3-setup/phone-public.json').read_text())
    if len(phone['wallets'])!=1:raise ValueError()  # review each wallet independently
    if gui:
        import tkinter as tk
        from tkinter import simpledialog
        window=tk.Tk();window.withdraw()
        pin=simpledialog.askstring('H02 disposable Pocket fixture',
          'Enter the Pocket app PIN once (not the phone unlock code).\nStored recovery words stay under H02-P0/private/.\nThe PIN is not saved. Cancel makes no changes.',show='*',parent=window)
        window.destroy()
    else:
        from getpass import getpass
        pin=getpass('Pocket app PIN (one attempt; not saved): ')
    if not pin:raise ValueError()
    w=phone['wallets'][0]
    b=(ROOT/'private/phone-acquisition/files/key_backups'/str(w['walletId']+'.enc')).read_bytes()
    material=decrypt_backup(b,pin)
    pin=None
    item={'public':w,'mnemonic':material.get('mnemonic'),'privateKey':material['privateKey']}
    data={'format':1,'fixture':'pocket-disposable-d2','sourceSerial':'R5CW6127VPR',
          'sourceVersion':'1.8.3','passphrase':'','wallets':[item]}
    public=verify(data)
    # Mnemonic is sufficient: do not duplicate its derived private key on disk.
    if item['mnemonic']:del item['privateKey']
    with FIXTURE.open('x',encoding='utf-8') as f:json.dump(data,f,indent=2);f.write('\n')
    (ROOT/'runs/wo3-setup/fixture-public-verified.json').write_text(json.dumps(public,indent=2))
    print(json.dumps(public,indent=2))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['recover','verify','prospective']);p.add_argument('--gui',action='store_true');a=p.parse_args()
    if a.action=='recover':recover(a.gui)
    elif a.action=='prospective':prospective()
    else:print(json.dumps(verify(json.loads(FIXTURE.read_text(encoding='utf-8'))),indent=2))

if __name__=='__main__':
    try:main()
    except Exception:
        print('FIXTURE_REFUSED_OR_NO_MATCH; no credential or exception details emitted');raise SystemExit(2)
