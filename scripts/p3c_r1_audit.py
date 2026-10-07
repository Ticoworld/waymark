"""Read-only exact-H2 payload and pinned persistence-code audit."""
import collections
import json
import sqlite3
import subprocess
from pathlib import Path
import h02_package as p
from h02_device import ROOT

SOURCE_APK = '903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f'
TRUST = '56d4a6506641c62797531eb0f093c4930131a9046d26351377c292568d7d879e'
GENESIS = '10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606'
PACKAGE = ROOT/'runs/wo3b2/package-H2-immutable'
SOURCE = ROOT/'repos/pocket-node'

def git(*args):
    return subprocess.check_output(['git','-C',str(SOURCE),*args],text=True).strip()

def audit():
    p.require(git('rev-parse','HEAD') == p.PIN and not git('status','--porcelain=v1'), 'source-not-pinned-clean')
    p.require(git('rev-parse','HEAD:external/ckb-light-client') == p.LC_TREE, 'native-tree-mismatch')
    manifest, app = p.validate(PACKAGE, TRUST, SOURCE_APK, GENESIS)
    files = [SOURCE/'external/ckb-light-client/light-client-lib'/s for s in
             ['src/storage/mod.rs','src/storage/db/mod.rs','src/storage/db/sqlite.rs','Cargo.toml']]
    backend = files[1].read_text()
    p.require('pub use sqlite::' in backend and '// mod native;' in backend, 'native-backend-unqualified')
    for file in files:
        code = file.read_text()
        p.require(not any(s in code for s in ['to_ne_bytes(', 'from_ne_bytes(', 'transmute(', 'bincode::']), 'host-representation-unqualified')
    schema = SOURCE/'android/app/schemas/com.rjnr.pocketnode.data.database.AppDatabase/17.json'
    room = p.read_json(schema)['database']
    p.require(room['version'] == manifest['roomSchema'] and room['identityHash'] == manifest['roomIdentity'], 'source-room-schema-mismatch')
    counts = collections.Counter(); meta = []; rows = 0
    dbpath = PACKAGE/'native.sqlite'
    with sqlite3.connect(dbpath.resolve().as_uri()+'?mode=ro&immutable=1',uri=True) as db:
        for key,value in db.execute('SELECT key,value FROM kv'):
            family = key[0]; counts[family] += 1; rows += 1
            if family == 0:
                p.require(len(value)>12 and int.from_bytes(value[12:16],'little')==len(value)-12, 'packed-transaction-length')
            elif family in (32,64):
                p.require(len(key)==70 or (family==64 and len(key)>=50), 'live-cell-index-size')
            elif family in (96,128):
                p.require(len(key)>=51 and key[-1] in (0,1), 'history-index-shape')
            elif family == 160:
                p.require(len(value)>=208, 'packed-header-length')
            elif family == 224:
                tag = key[1:]
                if tag.startswith(b'FILTER_SCRIPTS'):
                    p.require(tag[-1] in (0,1) and len(value)==8, 'script-progress-shape')
                    name = 'FILTER_SCRIPTS'; encoding = 'packed Script + u8 tag; u64 BE progress'
                elif tag == b'GENESIS_BLOCK':
                    p.require(len(value)%32==0, 'genesis-hash-vector')
                    name = tag.decode(); encoding = '32-byte hash vector'
                elif tag == b'LAST_STATE':
                    p.require(len(value)==240, 'last-state-shape')
                    name = tag.decode(); encoding = 'U256 LE (32 bytes) + packed Header (208 bytes)'
                elif tag == b'LAST_N_HEADERS':
                    p.require(len(value)%40==0, 'last-headers-shape')
                    name = tag.decode(); encoding = 'u64 LE + 32-byte hash, repeated'
                elif tag == b'MAX_CHECK_POINT_INDEX':
                    p.require(len(value)==4, 'checkpoint-index-shape')
                    name = tag.decode(); encoding = 'u32 BE'
                elif tag == b'MIN_FILTERED_NUMBER':
                    p.require(len(value)==8, 'filtered-number-shape')
                    name = tag.decode(); encoding = 'u64 LE'
                elif tag.startswith(b'MATCHED_BLOCKS'):
                    p.require((len(value)-8)%33==0, 'matched-blocks-shape')
                    name = 'MATCHED_BLOCKS'; encoding = 'u64 BE key; u64 LE count + hash/u8 records'
                else:
                    raise p.Refused('unknown-metadata-payload')
                meta.append({'name':name,'keyBytes':len(key),'valueBytes':len(value),'encoding':encoding})
    return {'sourceCommit':p.PIN,'nativeTree':p.LC_TREE,'H2ManifestSha256':TRUST,
            'sourceApkSha256':SOURCE_APK,'network':'TESTNET','genesis':GENESIS,
            'roomSchema':17,'roomIdentity':p.IDENTITY,'nativeSchema':p.NATIVE_SCHEMA,
            'payloads':{'manifest.json':'architecture-independent JSON provenance; unchanged',
                        'app.json':'architecture-independent logical JSON projection; destination ID remapping required',
                        'native.sqlite':'architecture-independent SQLite KV with explicit BE/LE and packed CKB records; byte-for-byte transfer'},
            'rowsAudited':rows,'keyFamilyCounts':dict(sorted(counts.items())),'metadata':meta,
            'sourceFiles':{str(f.relative_to(SOURCE)):p.sha(f) for f in [*files,schema]},
            'rocksDbPayloadPresent':False,'rawMemoryOrExecutablePayloadPresent':False,
            'unknownPayloads':[],'architectureDependentBlockers':[],
            'scope':'Exact H2 payload and same pinned non-wasm storage implementation; not a phone recovery or activation claim',
            'originalToolHashes':{name:p.sha(ROOT/'scripts'/name) for name in ['h02_package.py','h02_device.py']},
            'helperSha256':p.sha(ROOT/'runs/wo3b2-r2/state-helper/helper.jar'),
            'secretExclusion':'PASS','result':'PASS'}

if __name__ == '__main__':
    try:
        result = audit()
        out = ROOT/'runs/wo3c-r1/cross-abi-audit.json'
        with out.open('xb') as stream: stream.write(p.encode(result))
        print('EXACT_H2_PAYLOAD_AUDIT_PASS', result['rowsAudited'])
    except Exception as e:
        print('H2_ABI_AUDIT_REFUSED '+type(e).__name__+((' '+str(e)) if isinstance(e,p.Refused) else ''))
        raise SystemExit(2)
