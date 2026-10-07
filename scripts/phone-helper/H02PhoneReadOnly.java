package h02;

import android.app.KeyguardManager;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.hardware.biometrics.BiometricManager;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.File;

/** Read-only public projections. No Cipher, key access, migration, or wallet writes. */
public final class H02PhoneReadOnly {
    static JSONArray query(SQLiteDatabase db, String sql) throws Exception {
        JSONArray rows = new JSONArray();
        try (Cursor c = db.rawQuery(sql, null)) {
            while (c.moveToNext()) {
                JSONObject row = new JSONObject();
                for (int i = 0; i < c.getColumnCount(); i++) {
                    if (c.getType(i) == Cursor.FIELD_TYPE_BLOB) throw new Exception("BLOB_REFUSED");
                    row.put(c.getColumnName(i), c.isNull(i) ? JSONObject.NULL :
                        c.getType(i) == Cursor.FIELD_TYPE_INTEGER ? c.getLong(i) : c.getString(i));
                }
                rows.put(row);
            }
        }
        return rows;
    }
    public static void main(String[] args) {
        try {
            JSONObject out = new JSONObject();
            if (args.length == 1 && args[0].equals("security")) {
                android.os.Looper.prepareMainLooper();
                Class<?> cls = Class.forName("android.app.ActivityThread");
                Object thread = cls.getMethod("systemMain").invoke(null);
                Context ctx = (Context)cls.getMethod("getSystemContext").invoke(thread);
                KeyguardManager kg = ctx.getSystemService(KeyguardManager.class);
                out.put("isDeviceSecure", kg.isDeviceSecure());
                out.put("isDeviceLocked", kg.isDeviceLocked());
                BiometricManager bm = ctx.getSystemService(BiometricManager.class);
                out.put("canAuthenticateStrongOrCredential", bm.canAuthenticate(
                    BiometricManager.Authenticators.BIOMETRIC_STRONG | BiometricManager.Authenticators.DEVICE_CREDENTIAL));
                out.put("canAuthenticateStrong", bm.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG));
                out.put("scope", "shell system-context API; no prompt or credential access");
            } else if (args.length == 1 && args[0].equals("app")) {
                String root = "/data/user/0/com.rjnr.pocketnode/";
                try (SQLiteDatabase db = SQLiteDatabase.openDatabase(root + "databases/pocket_node.db", null, SQLiteDatabase.OPEN_READONLY)) {
                    out.put("roomVersion", db.getVersion());
                    out.put("roomIdentity", query(db, "SELECT identity_hash FROM room_master_table WHERE id=42"));
                    out.put("wallets", query(db, "SELECT walletId,type,derivationPath,parentWalletId,accountIndex,mainnetAddress,testnetAddress FROM wallets ORDER BY accountIndex"));
                    out.put("keyMetadata", query(db, "SELECT walletId,kdfVersion FROM key_material ORDER BY walletId"));
                    out.put("progress", query(db, "SELECT walletId,network,lightStartBlockNumber,localSavedBlockNumber FROM sync_progress ORDER BY walletId,network"));
                    out.put("dao", query(db, "SELECT txHash,\"index\",capacity,status,depositBlockNumber,depositBlockHash,depositEpochHex,network,walletId FROM dao_cells ORDER BY txHash,\"index\""));
                    out.put("balances", query(db, "SELECT walletId,network,address,capacity,blockNumber FROM balance_cache ORDER BY walletId,network"));
                }
                File nativeFile = new File(root + "files/data/testnet/store.db");
                out.put("testnetNativePresent", nativeFile.isFile());
                if (nativeFile.isFile()) {
                    try (SQLiteDatabase db = SQLiteDatabase.openDatabase(nativeFile.getPath(), null, SQLiteDatabase.OPEN_READONLY)) {
                        out.put("nativeUserVersion", db.getVersion());
                        out.put("nativeRegistrations", query(db, "SELECT hex(key) AS keyHex,hex(value) AS valueHex FROM kv WHERE substr(key,1,15)=X'E046494C5445525F53435249505453' ORDER BY key"));
                    }
                }
            } else throw new Exception("BAD_ACTION");
            System.out.println("H02_PHONE_PUBLIC_JSON=" + out.toString());
        } catch (Throwable e) {
            System.out.println("H02_PHONE_READ_ONLY_REFUSED:" + e.getClass().getSimpleName());
            System.exit(2);
        }
    }
}
