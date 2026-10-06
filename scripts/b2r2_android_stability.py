"""Bounded pre-Pocket Android stability check; no credentials or wallet state."""
import sys,time,json,datetime,shutil
from pathlib import Path
from r1_qualify import call,shell
out=Path('runs/wo3b2/source/boot-retry1/pre-pocket')
initial=call('logcat','-d','-b','events');anrs=[x for x in initial.splitlines() if 'am_anr' in x or 'am_crash' in x]
pid=shell('pidof','system_server').strip();start=time.monotonic();rows=[]
for i in range(7):
 if i:time.sleep(30)
 settings=shell('am','start','-W','-a','android.settings.SETTINGS');time.sleep(1)
 activities=shell('dumpsys','activity','activities');setting_ok='com.android.settings' in activities and 'Status: ok' in settings
 shell('input','keyevent','KEYCODE_HOME');time.sleep(1)
 home_ok='com.android.launcher3' in shell('dumpsys','activity','activities')
 now=[x for x in call('logcat','-d','-b','events').splitlines() if 'am_anr' in x or 'am_crash' in x]
 row={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed':round(time.monotonic()-start,2),'settings':setting_ok,'home':home_ok,'systemServerUnchanged':pid==shell('pidof','system_server').strip(),'newAnrsOrCrashes':len([x for x in now if x not in anrs]),'freeBytes':shutil.disk_usage(Path.cwd()).free}
 rows.append(row);print(json.dumps(row),flush=True)
 if not setting_ok or not home_ok or not row['systemServerUnchanged'] or row['newAnrsOrCrashes']:break
result={'priorBootAnrs':anrs,'observations':rows,'PASS':len(rows)==7 and all(x['settings'] and x['home'] and x['systemServerUnchanged'] and x['newAnrsOrCrashes']==0 for x in rows)}
with (out/'stability.json').open('x') as f:json.dump(result,f,indent=2)
if not result['PASS']:raise SystemExit(2)
