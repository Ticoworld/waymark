"""Read-only storage metadata inventory. Never opens file contents or follows reparse points."""
import ctypes,datetime,json,os,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
getsize=ctypes.WinDLL('kernel32',use_last_error=True).GetCompressedFileSizeW
getsize.argtypes=[ctypes.c_wchar_p,ctypes.POINTER(ctypes.c_ulong)];getsize.restype=ctypes.c_ulong
roots=[ROOT.parent,Path(os.environ['LOCALAPPDATA'])/'Android/Sdk',Path.home()/'.android/avd',Path.home()/'.gradle',Path.home()/'.cargo',Path.home()/'.rustup',Path(os.environ['LOCALAPPDATA'])/'Temp',Path('C:/Windows/Temp'),Path('C:/temp'),Path('C:/tmp'),Path('C:/w'),Path('C:/Ubuntu'),Path('C:/mnt'),Path.home()/'Downloads',Path.home()/'.cache']
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'driveBefore':shutil.disk_usage(ROOT)._asdict(),'roots':[],'directories':[],'largeFiles':[],'errors':[],'skippedReparse':[]}
def allocated(p):
 high=ctypes.c_ulong();ctypes.set_last_error(0);lo=getsize(str(p),ctypes.byref(high))
 if lo==0xffffffff and ctypes.get_last_error():raise OSError(ctypes.get_last_error())
 return (high.value<<32)|lo

def walk(p):
 logical=physical=count=0
 try:
  with os.scandir(p) as it:
   for e in it:
    try:
     st=e.stat(follow_symlinks=False)
     if st.st_file_attributes & 0x400:
      result['skippedReparse'].append(e.path);continue
     if e.is_dir(follow_symlinks=False):
      a,b,c=walk(Path(e.path));logical+=a;physical+=b;count+=c
     elif e.is_file(follow_symlinks=False):
      n=allocated(e.path);logical+=st.st_size;physical+=n;count+=1
      if st.st_size>=50*1024**2:result['largeFiles'].append({'path':e.path,'logical':st.st_size,'allocated':n})
    except OSError as exc:result['errors'].append({'path':e.path,'error':type(exc).__name__})
 except OSError as exc:result['errors'].append({'path':str(p),'error':type(exc).__name__})
 result['directories'].append({'path':str(p),'logical':logical,'allocated':physical,'files':count})
 return logical,physical,count
for p in roots:
 if p.exists():
  a,b,c=walk(p);result['roots'].append({'path':str(p),'logical':a,'allocated':b,'files':c})
  print(json.dumps(result['roots'][-1]),flush=True)
 else:result['roots'].append({'path':str(p),'missing':True})
result['driveAfterScan']=shutil.disk_usage(ROOT)._asdict()
out=ROOT/'runs/wo3b2-r1/storage-before.json'
with out.open('x') as f:json.dump(result,f,indent=2)
print('METADATA_SCAN_COMPLETE errors='+str(len(result['errors']))+' skippedReparse='+str(len(result['skippedReparse'])))
