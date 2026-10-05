"""Restore pinned missing pure-Perl modules under runs, not Git's Perl."""
import hashlib,json,tarfile,urllib.request
from pathlib import Path
root=Path(__file__).resolve().parent.parent;out=root/'runs/wo2/perl';out.mkdir(parents=True,exist_ok=True)
for name,archive in [('perl-'+n+'.json',n+'.tar.gz') for n in ('locale','makemaker','pod-usage','pod-text','pod-simple','pod-escapes')]:
    lock=json.loads((root/'scripts'/name).read_text());f=out/archive
    if not f.exists():f.write_bytes(urllib.request.urlopen(lock['url'],timeout=60).read())
    assert hashlib.sha256(f.read_bytes()).hexdigest()==lock['sha256'],'Perl module hash mismatch'
    with tarfile.open(f) as t:
        for m in t.getmembers():
            if '/lib/' in m.name and m.isfile():
                p=out/'lib'/m.name.split('/lib/',1)[1];assert p.resolve().is_relative_to(out.resolve())
                p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(t.extractfile(m).read())
    print('Verified '+name)
