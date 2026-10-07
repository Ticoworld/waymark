package h02;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import org.json.JSONObject;
/** Nonsecret convergence projection only; read-only connections, no key access. */
public final class H02PhoneABReadOnly {
    public static void main(String[] args) {
        try {
            JSONObject out=new JSONObject();
            String root="/data/user/0/com.rjnr.pocketnode/";
            try(SQLiteDatabase db=SQLiteDatabase.openDatabase(root+"databases/pocket_node.db",null,SQLiteDatabase.OPEN_READONLY)) {
                try(Cursor c=db.rawQuery("SELECT state,COUNT(*) FROM sub_account_candidates GROUP BY state",null)) {
                    JSONObject counts=new JSONObject();while(c.moveToNext())counts.put(c.getString(0),c.getLong(1));out.put("discoveryStates",counts);
                }
            }
            try(SQLiteDatabase db=SQLiteDatabase.openDatabase(root+"files/data/testnet/store.db",null,SQLiteDatabase.OPEN_READONLY)) {
                try(Cursor c=db.rawQuery("SELECT hex(value) FROM kv WHERE key=X'E04D494E5F46494C54455245445F4E554D424552'",null)) {
                    if(!c.moveToFirst())throw new Exception("MISSING_PROGRESS");out.put("minimumFilteredLittleEndianHex",c.getString(0));
                }
                try(Cursor c=db.rawQuery("SELECT COUNT(*) FROM kv WHERE substr(key,1,15)=X'E04D4154434845445F424C4F434B53'",null)) {
                    c.moveToFirst();out.put("matchedWorkRows",c.getLong(0));
                }
            }
            System.out.println("H02_PHONE_AB_PUBLIC_JSON="+out.toString());
        }catch(Throwable ignored){System.out.println("H02_PHONE_AB_READ_ONLY_REFUSED");System.exit(2);}
    }
}
