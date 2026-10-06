package h02;

import android.content.ContentValues;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import org.json.*;
import org.w3c.dom.*;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.transform.*;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import java.io.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import android.system.Os;
import android.system.OsConstants;

/** Standalone app_process helper. Never loads Pocket's Application or starts its LC.
 * The host must verify an emulator, force-stop and disable Pocket before invocation.
 * All Room page copies made by stage/rollback stay in the DESTINATION sandbox.
 */
public final class H02State {
    static int accountCount=2;
    static final String ID="091b40f9618fee3fc8032ff01255a9a4";
    static final String[] W={"walletId","type","derivationPath","parentWalletId","accountIndex","mainnetAddress","testnetAddress"};
    static final String[] P={"walletId","network","lightStartBlockNumber","localSavedBlockNumber","updatedAt"};
    static final String[] C={"parentWalletId","derivationPath","accountIndex","scriptArgs","state","createdAt","registeredFromBlock"};
    static final String[] SUFFIX={"sync_mode","custom_block_height","initial_sync_completed","zero_cell_rescan_done","gap_limit_signal","gap_limit_banner_dismissed"};
    static final String ROOM="databases/pocket_node.db", NATIVE="files/data/testnet/store.db", PREF="shared_prefs/ckb_wallet_prefs.xml";
    static final String[] LIVE={ROOM,ROOM+"-wal",ROOM+"-shm",NATIVE,NATIVE+"-wal",NATIVE+"-shm",PREF};
    static void need(boolean ok) throws Exception { if(!ok) throw new Exception("REFUSED"); }
    static File within(File base,String relative) throws Exception {
        File f=new File(base,relative);need(f.getCanonicalPath().startsWith(base.getCanonicalPath()+File.separator));
        need(!Files.isSymbolicLink(f.toPath()));return f;
    }
    static JSONObject json(File f) throws Exception { need(f.length()<8*1024*1024);return new JSONObject(new String(Files.readAllBytes(f.toPath()),"UTF-8")); }
    static void syncDir(File f) throws Exception {need(f.isDirectory());java.io.FileDescriptor d=Os.open(f.getPath(),OsConstants.O_RDONLY,0);try{Os.fsync(d);}finally{Os.close(d);}}
    static void move(File a,File b) throws Exception {Files.move(a.toPath(),b.toPath());syncDir(a.getParentFile());syncDir(b.getParentFile());}
    static void write(File f,byte[] b) throws Exception { need(!f.exists());try(FileOutputStream o=new FileOutputStream(f)){o.write(b);o.getFD().sync();}syncDir(f.getParentFile()); }
    static void writeJSON(File f,JSONObject j) throws Exception {write(f,(j.toString()+"\n").getBytes("UTF-8"));}
    static String hash(File f) throws Exception {
        MessageDigest d=MessageDigest.getInstance("SHA-256");byte[] b=new byte[65536];
        try(InputStream i=new FileInputStream(f)){int n;while((n=i.read(b))!=-1)d.update(b,0,n);}return hex(d.digest());
    }
    static String hex(byte[] b){StringBuilder s=new StringBuilder();for(byte x:b)s.append(String.format("%02x",x&255));return s.toString();}
    static SQLiteDatabase open(File f,boolean read) throws Exception {need(f.isFile());return SQLiteDatabase.openDatabase(f.getPath(),null,read?SQLiteDatabase.OPEN_READONLY:SQLiteDatabase.OPEN_READWRITE);}
    static long scalar(SQLiteDatabase d,String sql) {try(Cursor c=d.rawQuery(sql,null)){if(!c.moveToFirst())throw new IllegalStateException();return c.getLong(0);}}
    static void roomCheck(SQLiteDatabase d) throws Exception {
        need(scalar(d,"PRAGMA user_version")==17);
        try(Cursor c=d.rawQuery("SELECT identity_hash FROM room_master_table WHERE id=42",null)){need(c.moveToFirst()&&ID.equals(c.getString(0)));}
        need(scalar(d,"SELECT count(*) FROM sqlite_master WHERE type='trigger' AND name NOT LIKE 'room_%'")==0);
        try(Cursor c=d.rawQuery("PRAGMA integrity_check",null)){need(c.moveToFirst()&&"ok".equals(c.getString(0))&&!c.moveToNext());}
    }
    static JSONArray rows(SQLiteDatabase d,String table,String[] cols,String where,String order) throws Exception {
        JSONArray a=new JSONArray();String q="SELECT "+String.join(",",cols)+" FROM "+table+where+" ORDER BY "+order;
        try(Cursor c=d.rawQuery(q,null)){while(c.moveToNext()){JSONObject j=new JSONObject();for(int i=0;i<cols.length;i++){
            int t=c.getType(i);need(t!=Cursor.FIELD_TYPE_BLOB&&t!=Cursor.FIELD_TYPE_FLOAT);
            j.put(cols[i].replace("\"", ""),t==Cursor.FIELD_TYPE_NULL?JSONObject.NULL:t==Cursor.FIELD_TYPE_INTEGER?c.getLong(i):c.getString(i));
        }a.put(j);need(a.length()<=500);}}return a;
    }
    static Document xml(File f) throws Exception {
        need(f.isFile()&&f.length()<1024*1024);
        String raw=new String(Files.readAllBytes(f.toPath()),"UTF-8");need(!raw.contains("<!DOCTYPE")&&!raw.contains("<!ENTITY"));
        DocumentBuilderFactory factory=DocumentBuilderFactory.newInstance();factory.setExpandEntityReferences(false);
        return factory.newDocumentBuilder().parse(f);
    }
    static Set<String> prefNames(JSONArray wallets) throws Exception {
        Set<String> a=new HashSet<>(Arrays.asList("selected_network","sync_strategy","active_wallet_id"));
        for(int i=0;i<wallets.length();i++)for(String s:SUFFIX)a.add(wallets.getJSONObject(i).getString("walletId")+"_testnet_"+s);return a;
    }
    static JSONObject exportApp(File root) throws Exception {
        need(!within(root,PREF+".bak").exists());
        JSONObject out=new JSONObject();JSONArray w;
        try(SQLiteDatabase d=open(within(root,ROOM),true)){
            roomCheck(d);out.put("schema",17);out.put("identity",ID);
            w=rows(d,"wallets",W,"","walletId");need(w.length()==accountCount);out.put("wallets",w);
            out.put("progress",rows(d,"sync_progress",P," WHERE network='TESTNET'","walletId"));
            out.put("candidates",rows(d,"sub_account_candidates",C,"","parentWalletId,derivationPath"));
            boolean settled=true;for(String t:new String[]{"pending_broadcasts","pending_dao_withdraws","pending_dao_unlocks"})settled &= scalar(d,"SELECT count(*) FROM "+t)==0;
            settled &= scalar(d,"SELECT count(*) FROM transactions WHERE status!='CONFIRMED' OR isLocal!=0")==0;
            out.put("pendingFree",settled);
            // Only count matched IDs; no ciphertext, IV or key value crosses this boundary.
            out.put("keysPresent",scalar(d,"SELECT count(*) FROM wallets w JOIN key_material k ON w.walletId=k.walletId")==accountCount);
        }
        Set<String> allowed=prefNames(w);JSONObject prefs=new JSONObject();boolean migrated=false;
        NodeList nodes=xml(within(root,PREF)).getDocumentElement().getChildNodes();
        for(int i=0;i<nodes.getLength();i++)if(nodes.item(i) instanceof Element){
            Element e=(Element)nodes.item(i);String k=e.getAttribute("name");
            if(k.equals("sync_progress_migrated_to_room_v7"))migrated=e.getTagName().equals("boolean")&&e.getAttribute("value").equals("true");
            if(!allowed.contains(k))continue;need(!prefs.has(k));String t=e.getTagName();
            if(t.equals("string"))prefs.put(k,e.getTextContent());
            else if(t.equals("boolean")){need(e.getAttribute("value").matches("true|false"));prefs.put(k,Boolean.parseBoolean(e.getAttribute("value")));}
            else if(t.equals("long")||t.equals("int"))prefs.put(k,Long.parseLong(e.getAttribute("value")));
            else need(false);
        }
        // WalletPreferences.getSyncStrategy defaults to ALL_WALLETS when unset.
        // Preserve the effective policy even when the user never opened Settings.
        if(!prefs.has("sync_strategy"))prefs.put("sync_strategy","ALL_WALLETS");
        out.put("prefs",prefs);out.put("migrationReady",migrated);return out;
    }
    static void snapshotNative(File in,File out) throws Exception {
        need(!out.exists());
        try(SQLiteDatabase src=open(in,true)){
            try(Cursor c=src.rawQuery("SELECT type,name FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'",null)){need(c.moveToFirst()&&c.getString(0).equals("table")&&c.getString(1).equals("kv")&&!c.moveToNext());}
            try(SQLiteDatabase dst=SQLiteDatabase.openDatabase(out.getPath(),null,SQLiteDatabase.OPEN_READWRITE|SQLiteDatabase.CREATE_IF_NECESSARY|SQLiteDatabase.NO_LOCALIZED_COLLATORS)){
                try(Cursor mode=dst.rawQuery("PRAGMA journal_mode=DELETE",null)){need(mode.moveToFirst()&&mode.getString(0).equalsIgnoreCase("delete"));}
                dst.execSQL("PRAGMA synchronous=FULL");dst.execSQL("CREATE TABLE kv(key BLOB PRIMARY KEY,value BLOB)");dst.beginTransaction();
                try(Cursor c=src.rawQuery("SELECT key,value FROM kv ORDER BY key",null)){
                    while(c.moveToNext()){
                        need(c.getType(0)==Cursor.FIELD_TYPE_BLOB&&c.getType(1)==Cursor.FIELD_TYPE_BLOB);
                        byte[] k=c.getBlob(0),v=c.getBlob(1);need(k.length>0);
                        need(v.length>0||((k[0]&255)==224&&new String(Arrays.copyOfRange(k,1,k.length),"UTF-8").equals("LAST_N_HEADERS")));
                        int p=k[0]&255;need(p==0||p==32||p==64||p==96||p==128||p==160||p==192||p==208||p==224);
                        ContentValues cv=new ContentValues();cv.put("key",k);cv.put("value",v);dst.insertOrThrow("kv",null,cv);
                    }
                    dst.setTransactionSuccessful();
                } finally {dst.endTransaction();}
            }
        }
    }
    static JSONObject observeRoom(File root) throws Exception {
        JSONObject out=new JSONObject();
        try(SQLiteDatabase d=open(within(root,ROOM),true)){
            roomCheck(d);
            out.put("transactions",rows(d,"transactions",new String[]{"txHash","blockNumber","blockHash","network","status","isLocal","walletId","balanceChange","fee_shannons"}," WHERE network='TESTNET'","txHash,walletId"));
            out.put("balances",rows(d,"balance_cache",new String[]{"walletId","network","address","capacity","blockNumber"}," WHERE network='TESTNET'","walletId"));
            out.put("daoCount",scalar(d,"SELECT count(*) FROM dao_cells WHERE network='TESTNET'"));
            out.put("daoCells",rows(d,"dao_cells",new String[]{"txHash","\"index\"","capacity","status","depositBlockNumber","depositBlockHash","depositEpochHex","withdrawBlockNumber","withdrawBlockHash","withdrawEpochHex","compensation","unlockEpochHex","depositTimestamp","network","lastUpdatedAt","walletId"}," WHERE network='TESTNET'","txHash,\"index\""));
        }
        return out;
    }
    static void copy(File a,File b) throws Exception {need(!b.exists()&&a.isFile());Files.copy(a.toPath(),b.toPath());try(RandomAccessFile r=new RandomAccessFile(b,"rw")){r.getFD().sync();}syncDir(b.getParentFile());}
    static void checkFields(JSONObject j,String[] allowed) throws Exception {
        Set<String> s=new HashSet<>(Arrays.asList(allowed));need(j.length()==s.size());Iterator<String> it=j.keys();while(it.hasNext())need(s.contains(it.next()));
    }
    static String canonical(Object value) throws Exception {
        if(value instanceof JSONObject){JSONObject j=(JSONObject)value;TreeSet<String> ks=new TreeSet<>();Iterator<String> it=j.keys();while(it.hasNext())ks.add(it.next());StringBuilder b=new StringBuilder("{");for(String k:ks)b.append(JSONObject.quote(k)).append(':').append(canonical(j.get(k))).append(',');return b.append('}').toString();}
        if(value instanceof JSONArray){JSONArray a=(JSONArray)value;StringBuilder b=new StringBuilder("[");for(int i=0;i<a.length();i++)b.append(canonical(a.get(i))).append(',');return b.append(']').toString();}
        return value instanceof String?JSONObject.quote((String)value):value.toString();
    }
    static ContentValues values(JSONObject j,String[] cols) throws Exception {
        checkFields(j,cols);ContentValues v=new ContentValues();for(String k:cols){Object x=j.get(k);if(x==JSONObject.NULL)v.putNull(k);else if(x instanceof Number)v.put(k,((Number)x).longValue());else if(x instanceof String)v.put(k,(String)x);else need(false);}return v;
    }
    static String keyDigest(SQLiteDatabase d) throws Exception {
        MessageDigest md=MessageDigest.getInstance("SHA-256");
        try(Cursor c=d.rawQuery("SELECT * FROM key_material ORDER BY walletId",null)){while(c.moveToNext())for(int i=0;i<c.getColumnCount();i++){
            md.update((byte)c.getType(i));byte[] b=c.isNull(i)?new byte[0]:c.getType(i)==Cursor.FIELD_TYPE_BLOB?c.getBlob(i):c.getString(i).getBytes("UTF-8");md.update(java.nio.ByteBuffer.allocate(4).putInt(b.length).array());md.update(b);
        }}return hex(md.digest());
    }
    static JSONObject liveHashes(File root) throws Exception {
        JSONObject out=new JSONObject();for(String path:LIVE){File f=within(root,path);out.put(path,f.exists()?hash(f):JSONObject.NULL);}return out;
    }
    static void stage(File root,File dir,String planDigest) throws Exception {
        need(!within(root,"files/h02-restore-journal.json").exists());
        need(hash(new File(dir,"plan.json")).equals(planDigest));JSONObject p=json(new File(dir,"plan.json"));
        checkFields(p,new String[]{"format","destinationScripts","progress","candidates","prefs","nativeSha256"});
        need(p.getString("format").equals("h02-p0-v1")||p.getString("format").equals("h02-p0-b1-one-account-v1"));
        accountCount=p.getString("format").equals("h02-p0-v1")?2:1;
        need(hash(new File(dir,"native.sqlite")).equals(p.getString("nativeSha256")));
        JSONObject current=exportApp(root),expected=json(new File(dir,"destination.json"));
        need(canonical(current).equals(canonical(expected))&&current.getBoolean("keysPresent")&&current.getBoolean("pendingFree")&&current.getBoolean("migrationReady"));
        JSONArray w=current.getJSONArray("wallets");Set<String> ids=new HashSet<>();for(int i=0;i<w.length();i++)ids.add(w.getJSONObject(i).getString("walletId"));
        need(p.getJSONObject("destinationScripts").length()==accountCount);for(String id:ids)need(p.getJSONObject("destinationScripts").has(id));
        File staged=new File(dir,"staged");need(staged.mkdir());File rd=new File(staged,"room.db");
        for(String suffix:new String[]{"","-wal","-shm"}){File f=within(root,ROOM+suffix);if(f.exists())copy(f,new File(staged,"room.db"+suffix));}
        try(SQLiteDatabase d=open(rd,false)){
            roomCheck(d);String before=keyDigest(d);d.beginTransaction();
            try{
                d.delete("sync_progress","network=?",new String[]{"TESTNET"});d.delete("sub_account_candidates",null,null);
                JSONArray a=p.getJSONArray("progress");need(a.length()==accountCount);Set<String> seen=new HashSet<>();
                for(int i=0;i<a.length();i++){JSONObject r=a.getJSONObject(i);need(ids.contains(r.getString("walletId"))&&seen.add(r.getString("walletId"))&&r.getString("network").equals("TESTNET"));d.insertOrThrow("sync_progress",null,values(r,P));}
                a=p.getJSONArray("candidates");need(a.length()<=500);for(int i=0;i<a.length();i++){JSONObject r=a.getJSONObject(i);need(ids.contains(r.getString("parentWalletId")));d.insertOrThrow("sub_account_candidates",null,values(r,C));}
                for(String t:new String[]{"transactions","balance_cache","header_cache","dao_cells"})d.delete(t,"network=?",new String[]{"TESTNET"});
                String active=p.getJSONObject("prefs").getString("active_wallet_id");need(ids.contains(active));
                ContentValues off=new ContentValues();off.put("isActive",0);d.update("wallets",off,null,null);ContentValues on=new ContentValues();on.put("isActive",1);d.update("wallets",on,"walletId=?",new String[]{active});
                need(before.equals(keyDigest(d)));d.setTransactionSuccessful();
            }finally{d.endTransaction();}
            try(Cursor c=d.rawQuery("PRAGMA wal_checkpoint(TRUNCATE)",null)){need(c.moveToFirst()&&c.getInt(0)==0);}
            try(Cursor c=d.rawQuery("PRAGMA journal_mode=DELETE",null)){need(c.moveToFirst()&&c.getString(0).equalsIgnoreCase("delete"));}
            roomCheck(d);need(before.equals(keyDigest(d)));
        }
        Document doc=xml(within(root,PREF));Element map=doc.getDocumentElement();JSONObject prefs=p.getJSONObject("prefs");Set<String> allowed=prefNames(w);
        // Absence in the approved source projection restores Pocket's default;
        // it must not retain a stale destination sync flag.
        NodeList prior=map.getChildNodes();for(int i=prior.getLength()-1;i>=0;i--)if(prior.item(i) instanceof Element&&allowed.contains(((Element)prior.item(i)).getAttribute("name")))map.removeChild(prior.item(i));
        Iterator<String> it=prefs.keys();while(it.hasNext()){
            String k=it.next();need(allowed.contains(k));NodeList nodes=map.getChildNodes();for(int i=nodes.getLength()-1;i>=0;i--)if(nodes.item(i) instanceof Element&&((Element)nodes.item(i)).getAttribute("name").equals(k))map.removeChild(nodes.item(i));
            Object v=prefs.get(k);String t=v instanceof Boolean?"boolean":v instanceof Number?"long":"string";Element e=doc.createElement(t);e.setAttribute("name",k);if(t.equals("string"))e.setTextContent((String)v);else e.setAttribute("value",v.toString());map.appendChild(e);
        }
        File pf=new File(staged,"prefs.xml");try(FileOutputStream o=new FileOutputStream(pf)){TransformerFactory.newInstance().newTransformer().transform(new DOMSource(doc),new StreamResult(o));o.getFD().sync();}
        copy(new File(dir,"native.sqlite"),new File(staged,"native.sqlite"));
        writeJSON(new File(dir,"STAGED.json"),new JSONObject().put("room",hash(rd)).put("prefs",hash(pf)).put("native",hash(new File(staged,"native.sqlite"))).put("baseline",liveHashes(root)));
    }
    static void commit(File root,File dir,boolean syntheticInterrupt) throws Exception {
        need(dir.getName().matches("h02-stage-[a-f0-9]{16}"));
        File journal=within(root,"files/h02-restore-journal.json");need(!journal.exists());JSONObject receipt=json(new File(dir,"STAGED.json"));File s=new File(dir,"staged");
        need(hash(new File(s,"room.db")).equals(receipt.getString("room"))&&hash(new File(s,"prefs.xml")).equals(receipt.getString("prefs"))&&hash(new File(s,"native.sqlite")).equals(receipt.getString("native")));
        need(canonical(liveHashes(root)).equals(canonical(receipt.getJSONObject("baseline"))));
        File backup=new File(dir,"originals");need(backup.mkdir());JSONArray existed=new JSONArray();for(String f:LIVE)existed.put(within(root,f).exists());
        writeJSON(journal,new JSONObject().put("stage",dir.getName()).put("existed",existed).put("baseline",receipt.getJSONObject("baseline")));
        for(int i=0;i<LIVE.length;i++){File f=within(root,LIVE[i]);if(f.exists())move(f,new File(backup,Integer.toString(i)));if(i==0&&syntheticInterrupt)need(false);}
        move(new File(s,"room.db"),within(root,ROOM));move(new File(s,"native.sqlite"),within(root,NATIVE));move(new File(s,"prefs.xml"),within(root,PREF));
        writeJSON(new File(dir,"COMMITTED.json"),receipt);need(journal.delete());syncDir(journal.getParentFile());
    }
    static void rollback(File root) throws Exception {
        File jf=within(root,"files/h02-restore-journal.json");JSONObject j=json(jf);String stage=j.getString("stage");need(stage.matches("h02-stage-[a-f0-9]{16}"));File dir=within(root,"files/"+stage),backup=new File(dir,"originals");JSONArray existed=j.getJSONArray("existed");need(existed.length()==LIVE.length);
        for(int i=0;i<LIVE.length;i++){File f=within(root,LIVE[i]),b=new File(backup,Integer.toString(i));if(b.exists()){if(f.exists())need(f.delete());copy(b,f);}else if(!existed.getBoolean(i)&&f.exists())need(f.delete());}
        for(String path:LIVE)syncDir(within(root,path).getParentFile());need(canonical(liveHashes(root)).equals(canonical(j.getJSONObject("baseline"))));need(jf.delete());syncDir(jf.getParentFile());
    }
    public static void main(String[] a) {
        try{
            need(a.length>=3);String action=a[0];File root=new File(a[1]).getCanonicalFile(),dir=new File(a[2]).getCanonicalFile();
            if(action.equals("export-b1")||action.equals("inspect-b1")||action.equals("observe-b1")){accountCount=1;action=action.substring(0,action.length()-3);}
            boolean sandbox=root.getPath().equals("/data/user/0/com.rjnr.pocketnode")||root.getPath().equals("/data/data/com.rjnr.pocketnode");
            boolean synthetic=root.getPath().startsWith("/data/local/tmp/h02-synthetic-");need(sandbox||synthetic);
            need(dir.getPath().startsWith(root.getPath()+"/files/h02-"));
            if(action.equals("probe")){
                need(sandbox&&dir.mkdir());File test=new File(dir,"sqlite-probe.db");
                // Generated, non-wallet data: prove framework SQLite works
                // under the actual app UID without loading its Application.
                try(SQLiteDatabase db=SQLiteDatabase.openDatabase(test.getPath(),null,SQLiteDatabase.OPEN_READWRITE|SQLiteDatabase.CREATE_IF_NECESSARY|SQLiteDatabase.NO_LOCALIZED_COLLATORS)){
                    try(Cursor mode=db.rawQuery("PRAGMA journal_mode=WAL",null)){need(mode.moveToFirst()&&mode.getString(0).equalsIgnoreCase("wal"));}
                    db.execSQL("CREATE TABLE h02_probe(value INTEGER NOT NULL)");
                    db.beginTransaction();try{db.execSQL("INSERT INTO h02_probe VALUES(73)");db.setTransactionSuccessful();}finally{db.endTransaction();}
                    need(scalar(db,"SELECT sum(value) FROM h02_probe")==73);
                }
                try(SQLiteDatabase db=open(test,true)){need(scalar(db,"SELECT sum(value) FROM h02_probe")==73);}
            }
            else if(action.equals("export")||action.equals("inspect")||action.equals("observe")){
                need(dir.mkdir());JSONObject app=exportApp(root);need(app.getBoolean("pendingFree")&&app.getBoolean("migrationReady")&&app.getBoolean("keysPresent"));
                writeJSON(new File(dir,"app.json"),app);
                if(action.equals("export")||action.equals("observe"))snapshotNative(within(root,NATIVE),new File(dir,"native.sqlite"));
                if(action.equals("observe"))writeJSON(new File(dir,"public.json"),observeRoom(root));
            }else if(action.equals("stage")){need(a.length==4);stage(root,dir,a[3]);}
            else if(action.equals("commit"))commit(root,dir,false);
            else if(action.equals("commit-interrupt")){need(synthetic);commit(root,dir,true);}
            else if(action.equals("rollback"))rollback(root);
            else need(false);
            System.out.println("H02_HELPER_OK");
        }catch(Throwable e){
            System.err.println("H02_HELPER_REFUSED "+e.getClass().getSimpleName());
            for(StackTraceElement f:e.getStackTrace())if(f.getClassName().equals("h02.H02State"))System.err.println(f.getMethodName()+":"+f.getLineNumber());
            System.exit(2);
        }
    }
}
