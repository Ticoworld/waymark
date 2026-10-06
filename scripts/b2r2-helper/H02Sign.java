package h02;

import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import dalvik.system.PathClassLoader;
import java.io.File;
import java.security.KeyStore;
import java.util.Arrays;
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import org.json.*;

/** Test-only challenge signing in the recovered emulator app UID. No secret export,
 * no mnemonic access, no key writes and no transaction signing/broadcast. */
public final class H02Sign {
    static String stage="arguments";
    static void need(boolean b) throws Exception {if(!b)throw new Exception();}
    static String hex(byte[] b){StringBuilder s=new StringBuilder();for(byte x:b)s.append(String.format("%02x",x&255));return s.toString();}
    static byte[] decode(byte[] b) throws Exception {
        int start=b.length>=2&&b[0]=='0'&&b[1]=='x'?2:0;
        need(b.length-start==64);byte[] v=new byte[32];
        for(int i=0;i<32;i++){int a=Character.digit((char)b[start+2*i],16),c=Character.digit((char)b[start+2*i+1],16);need(a>=0&&c>=0);v[i]=(byte)(a*16+c);}return v;
    }
    public static void main(String[] args){
        try {
            need(args.length==3&&args[0].startsWith("/data/app/")&&args[1].equals("/data/user/0/com.rjnr.pocketnode")&&args[2].matches("[0-9a-f]{64}"));
            byte[] challenge=decode(args[2].getBytes("US-ASCII"));
            stage="provider";
            if(java.security.Security.getProvider("AndroidKeyStore")==null)
                Class.forName("android.security.keystore2.AndroidKeyStoreProvider").getMethod("install").invoke(null);
            KeyStore ks=KeyStore.getInstance("AndroidKeyStore");ks.load(null);
            need(ks.containsAlias("pocket_node_key_material"));
            stage="apk-signer";
            String libs=new File(args[0]).getParent()+"/lib/x86_64:"+args[0]+"!/lib/x86_64";
            PathClassLoader loader=new PathClassLoader(args[0],libs,H02Sign.class.getClassLoader());
            Class<?> type=Class.forName("com.rjnr.pocketnode.core.crypto.Secp256k1Signer",true,loader);
            Object signer=type.getField("INSTANCE").get(null);
            JSONArray result=new JSONArray();stage="read-only-rows";
            try(SQLiteDatabase db=SQLiteDatabase.openDatabase(args[1]+"/databases/pocket_node.db",null,SQLiteDatabase.OPEN_READONLY);
                Cursor c=db.rawQuery("SELECT w.walletId,w.accountIndex,k.kdfVersion,k.iv,k.encryptedPrivateKey FROM wallets w JOIN key_material k ON w.walletId=k.walletId ORDER BY w.accountIndex",null)){
                need(c.getCount()==2);
                while(c.moveToNext()){
                    need(c.getInt(2)==1);byte[] key=null,plain=null,ciphertext=null,iv=null;
                    try {
                        stage="decrypt-local-v1";iv=c.getBlob(3);ciphertext=c.getBlob(4);
                        Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");
                        cipher.init(Cipher.DECRYPT_MODE,ks.getKey("pocket_node_key_material",null),new GCMParameterSpec(128,iv));
                        plain=cipher.doFinal(ciphertext);key=decode(plain);
                        stage="challenge-sign";
                        byte[] pub=(byte[])type.getMethod("publicKey",byte[].class).invoke(signer,(Object)key);
                        byte[] sig=(byte[])type.getMethod("signRecoverable",byte[].class,byte[].class).invoke(signer,challenge,key);
                        need((Boolean)type.getMethod("verify",byte[].class,byte[].class,byte[].class).invoke(signer,sig,challenge,pub));
                        result.put(new JSONObject().put("walletId",c.getString(0)).put("accountIndex",c.getInt(1)).put("publicKey",hex(pub)).put("signature",hex(sig)));
                    } finally {for(byte[] b:new byte[][]{key,plain,ciphertext,iv})if(b!=null)Arrays.fill(b,(byte)0);}
                }
            }
            System.out.println(new JSONObject().put("challenge",args[2]).put("accounts",result).toString());
        }catch(Throwable e){System.out.println("H02_SIGN_REFUSED stage="+stage);System.exit(2);}
    }
}
