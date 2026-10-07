package h02;

import java.security.KeyStore;
import javax.crypto.SecretKeyFactory;
import android.security.keystore.KeyInfo;
import org.json.JSONObject;

/** Only public Keystore existence/protection metadata; never encrypts/decrypts. */
public final class H02PhoneSecurity {
    public static void main(String[] args) {
        try {
            if(java.security.Security.getProvider("AndroidKeyStore")==null)
                Class.forName("android.security.keystore2.AndroidKeyStoreProvider").getMethod("install").invoke(null);
            KeyStore store=KeyStore.getInstance("AndroidKeyStore");store.load(null);
            JSONObject out=new JSONObject();
            for(String alias:new String[]{"pocket_node_key_material","pocket_node_key_material_v2"}) {
                JSONObject row=new JSONObject();
                boolean present=store.containsAlias(alias);row.put("present",present);
                if(present) {
                    java.util.Date created=store.getCreationDate(alias);
                    row.put("createdAt",created==null?JSONObject.NULL:created.getTime());
                    try {
                        javax.crypto.SecretKey key=(javax.crypto.SecretKey)store.getKey(alias,null);
                        KeyInfo info=(KeyInfo)SecretKeyFactory.getInstance(key.getAlgorithm(),"AndroidKeyStore").getKeySpec(key,KeyInfo.class);
                        row.put("userAuthenticationRequired",info.isUserAuthenticationRequired());
                        row.put("authenticationValiditySeconds",info.getUserAuthenticationValidityDurationSeconds());
                        row.put("authenticationType",info.getUserAuthenticationType());
                        row.put("securityLevel",info.getSecurityLevel());
                        row.put("invalidatedByBiometricEnrollment",info.isInvalidatedByBiometricEnrollment());
                        key=null;
                    } catch(Throwable ignored) {row.put("protectionMetadata","UNKNOWN_API_REFUSED");}
                }
                out.put(alias,row);
            }
            out.put("keyExported",false);out.put("cipherOperation",false);
            System.out.println("H02_PHONE_SECURITY_JSON="+out.toString());
        } catch(Throwable ignored) {System.out.println("H02_PHONE_SECURITY_REFUSED");System.exit(2);}
    }
}
