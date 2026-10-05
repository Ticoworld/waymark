"""Emulator-only transport. No command launches Pocket. No implicit adb target.

Export and restore leave Pocket DISABLED. Resume is a separate explicit command.
Do not run these commands against a recovered wallet until PM authorizes WO-3.
"""
import argparse
import json
import os
import re
import shlex
import subprocess
import uuid
import csv
import base64
import hashlib
from pathlib import Path
import h02_package as policy

ROOT=Path(__file__).resolve().parent.parent
APP='com.rjnr.pocketnode'
AVD='H02_P0_API36_X64'
REMOTE_ROOT='/data/user/0/'+APP
HELPER=ROOT/'runs/wo2/helper/helper.jar'

class Device:
    def __init__(self,serial,apk_hash):
        policy.require(re.fullmatch(r'emulator-\d+',serial) is not None,'physical-device-refused')
        self.serial=serial;self.apk_hash=apk_hash
        self.adb=str(Path(os.environ['LOCALAPPDATA'])/'Android/Sdk/platform-tools/adb.exe')
        policy.require(self.call('emu','avd','name').decode().splitlines()[0]==AVD,'wrong-avd')
        policy.require(self.shell('getprop','ro.kernel.qemu').strip()==b'1','non-emulator')
        policy.require(self.shell('getprop','ro.build.version.sdk').strip()==b'36' and self.shell('getprop','ro.product.cpu.abi').strip()==b'x86_64','emulator-profile-mismatch')
        info=self.shell('dumpsys','package',APP).decode()
        policy.require(re.search(r'versionName=1\.8\.5(?:\s|$)',info) and re.search(r'versionCode=27\b',info) and 'DEBUGGABLE' in info,'wrong-pocket-build')
        paths=self.shell('pm','path',APP).decode().strip().splitlines()
        policy.require(len(paths)==1 and paths[0].startswith('package:/data/app/'),'apk-path')
        policy.require(self.shell('sha256sum',paths[0][8:]).decode().split()[0]==apk_hash,'apk-digest')

    def call(self,*args,data=None):
        r=subprocess.run([self.adb,'-s',self.serial,*args],input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=300)
        policy.require(r.returncode==0,'adb-operation-refused')
        return r.stdout

    def shell(self,*args): return self.call('shell','-T',shlex.join(args))

    def sandbox(self,*args,data=None):
        # shell v2 preserves remote exit status. File bytes use base64 below:
        # Windows adb shell can truncate binary stdin at Ctrl-Z even with -T.
        return self.call('shell','-T',shlex.join(['run-as',APP,*args]),data=data)

    def stopped(self):
        names=self.shell('ps','-A','-o','NAME').decode().splitlines()
        policy.require(not any(n==APP or n.startswith(APP+':') for n in names),'pocket-running')

    def freeze(self):
        self.shell('am','force-stop','--user','0',APP)
        self.shell('pm','disable-user','--user','0',APP)
        disabled=self.shell('pm','list','packages','-d','--user','0',APP).decode().splitlines()
        policy.require('package:'+APP in disabled,'disable-not-confirmed');self.stopped()

    def put(self,remote,data):
        # Destination is constructed by this module; never read from an archive path.
        policy.require(remote.startswith(REMOTE_ROOT+'/files/h02-') and re.fullmatch(r'[/a-zA-Z0-9_.-]+',remote),'unsafe-remote-path')
        self.sandbox('sh','-c','umask 077; set -C; base64 -d > '+shlex.quote(remote),data=base64.b64encode(data)+b'\n')
        policy.require(self.sandbox('sha256sum',remote).decode().split()[0]==hashlib.sha256(data).hexdigest(),'remote-write-digest')

    def get(self,path):
        policy.require(re.fullmatch(re.escape(REMOTE_ROOT)+r'/files/h02-(?:export|inspect)-[a-f0-9]{16}/(?:app.json|native.sqlite)',path) is not None,'unapproved-export-member')
        return base64.b64decode(b''.join(self.sandbox('base64',path).split()),validate=True)

    def deploy(self):
        policy.require(HELPER.is_file(),'helper-not-built')
        self.sandbox('mkdir','-p',REMOTE_ROOT+'/files')
        # Unique path prevents overwriting a helper still in use.
        self.jar=REMOTE_ROOT+'/files/h02-helper-'+uuid.uuid4().hex[:16]+'.jar'
        self.put(self.jar,HELPER.read_bytes());self.sandbox('chmod','400',self.jar)

    def helper(self,action,directory,*args):
        self.stopped()
        r=self.sandbox('env','CLASSPATH='+self.jar,'/system/bin/app_process','/system/bin','h02.H02State',action,REMOTE_ROOT,directory,*args)
        policy.require(r.strip()==b'H02_HELPER_OK','helper-refused');self.stopped()

    def inspect(self):
        directory=REMOTE_ROOT+'/files/h02-inspect-'+uuid.uuid4().hex[:16]
        self.helper('inspect',directory)
        raw=self.get(directory+'/app.json')
        app=json.loads(raw,object_pairs_hook=policy.unique_object)
        policy.validate_app(app,destination=True)
        return raw,app

def run_dir(path):
    path=Path(path).resolve()
    policy.require(path.is_relative_to((ROOT/'runs').resolve()),'output-outside-runs')
    policy.require(not path.exists(),'output-exists');path.mkdir(parents=True)
    if os.name=='nt':
        user=subprocess.run(['whoami','/user','/fo','csv','/nh'],capture_output=True,text=True,check=True)
        sid=next(csv.reader(user.stdout.splitlines()))[1]
        policy.require(re.fullmatch(r'S-[0-9-]+',sid) is not None,'owner-sid')
        acl=subprocess.run(['icacls',str(path),'/inheritance:r','/grant:r','*'+sid+':(OI)(CI)F','*S-1-5-18:(OI)(CI)F','*S-1-5-32-544:(OI)(CI)F'],capture_output=True)
        policy.require(acl.returncode==0,'private-directory-acl')
    else:path.chmod(0o700)
    return path

def export(a):
    # Version/device check precedes any stateful device operation.
    d=Device(a.serial,a.apk_sha256);out=run_dir(a.out)
    d.freeze();d.deploy()
    remote=REMOTE_ROOT+'/files/h02-export-'+uuid.uuid4().hex[:16]
    d.helper('export',remote)
    for name in ('app.json','native.sqlite'):
        (out/name).write_bytes(d.get(remote+'/'+name))
    digest=policy.seal(out,a.apk_sha256,a.genesis,a.boundary,a.boundary_hash,policy.read_json(Path(a.coverage)))
    print('EXPORT_POLICY_PASS; Pocket remains disabled')
    print('Trusted manifest SHA-256: '+digest)

def stage(a):
    # All package rejection gates run before stopping/modifying a destination.
    policy.validate(Path(a.package),a.trust,a.apk_sha256,a.genesis)
    d=Device(a.serial,a.apk_sha256);d.freeze();d.deploy()
    raw,destination=d.inspect()
    plan=policy.restore_plan(Path(a.package),a.trust,a.apk_sha256,a.genesis,destination)
    token=uuid.uuid4().hex[:16];remote=REMOTE_ROOT+'/files/h02-stage-'+token
    d.sandbox('mkdir','-m','700',remote)
    b=policy.encode(plan);d.put(remote+'/plan.json',b);d.put(remote+'/destination.json',raw)
    d.put(remote+'/native.sqlite',(Path(a.package)/'native.sqlite').read_bytes())
    d.helper('stage',remote,__import__('hashlib').sha256(b).hexdigest())
    print('RESTORE_STAGED; Pocket remains disabled; no activation or launch')
    print('Stage token: '+token)

def activate(a):
    policy.require(re.fullmatch('[0-9a-f]{16}',a.token) is not None,'invalid-stage-token')
    d=Device(a.serial,a.apk_sha256);d.freeze();d.deploy()
    remote=REMOTE_ROOT+'/files/h02-stage-'+a.token
    d.helper(a.action,remote)
    print('RESTORE_'+a.action.upper()+'_OK; Pocket remains disabled; no recovery claim')

def enable(a):
    d=Device(a.serial,a.apk_sha256);d.stopped()
    # Check succeeds only when no incomplete cross-file activation exists.
    d.sandbox('test','!','-e',REMOTE_ROOT+'/files/h02-restore-journal.json')
    d.shell('pm','enable','--user','0',APP)
    print('Pocket enabled, not launched')

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    for name in ('export','stage','commit','rollback','enable'):
        q=sub.add_parser(name);q.add_argument('--serial',required=True);q.add_argument('--apk-sha256',required=True)
        if name in ('export','stage'):q.add_argument('--genesis',required=True)
        if name=='export':
            q.add_argument('--out',required=True);q.add_argument('--boundary',required=True,type=int);q.add_argument('--boundary-hash',required=True);q.add_argument('--coverage',required=True)
        if name=='stage':q.add_argument('--package',required=True);q.add_argument('--trust',required=True)
        if name in ('commit','rollback'):q.add_argument('--token',required=True)
    a=p.parse_args()
    {'export':export,'stage':stage,'commit':activate,'rollback':activate,'enable':enable}[a.action](a)

if __name__=='__main__':
    try:main()
    except (policy.Refused,ValueError,KeyError,TypeError,OSError,subprocess.SubprocessError):
        print('H02_OPERATION_REFUSED; if already frozen, Pocket remains disabled');raise SystemExit(2)
