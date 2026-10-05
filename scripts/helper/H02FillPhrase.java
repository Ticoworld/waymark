package h02;

import android.os.Bundle;
import android.view.accessibility.AccessibilityNodeInfo;
import com.android.uiautomator.core.*;
import com.android.uiautomator.testrunner.UiAutomatorTestCase;
import org.json.JSONObject;
import java.nio.charset.StandardCharsets;

/** Test-only secret entry. No screenshots, hierarchy dumps, clipboard, app launch,
 * import submission or key-store writes. Runtime qualification is pending WO-3.
 * Inputs travel via an app-private temporary file, never command arguments.
 */
public final class H02FillPhrase extends UiAutomatorTestCase {
    private static final String APP="com.rjnr.pocketnode";
    static final class Field extends UiObject {
        Field(UiSelector selector) {super(selector);}
        boolean replace(String word) {
            AccessibilityNodeInfo node=findAccessibilityNodeInfo(3000);
            for(int i=0;i<4 && node!=null;i++,node=node.getParent()) {
                if(!APP.contentEquals(node.getPackageName())) return false;
                if(node.isEditable()) {
                    Bundle b=new Bundle();b.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE,word);
                    // Deliberately avoid UiObject.setText/sendText logging paths.
                    boolean ok=node.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT,b);
                    node.refresh();
                    return ok && node.getText()!=null && node.getText().toString().contains(word);
                }
            }
            return false;
        }
    }
    public void testFillOnly() {
        try {
            String path=getParams().getString("fixture");
            if(path==null || !path.matches("/data/user/0/com\\.rjnr\\.pocketnode/files/h02-phrase-[a-f0-9]{16}\\.json")) throw new Exception();
            if(!APP.equals(getUiDevice().getCurrentPackageName()))throw new Exception();
            if(!new UiObject(new UiSelector().resourceId("import-submit")).exists() &&
               !new UiObject(new UiSelector().text("Import Wallet")).exists())throw new Exception();
            Process p=new ProcessBuilder("run-as",APP,"cat",path).start();
            byte[] raw=p.getInputStream().readAllBytes();
            if(p.waitFor()!=0 || raw.length>4096)throw new Exception();
            String[] words=new JSONObject(new String(raw,StandardCharsets.UTF_8)).getString("mnemonic").split(" ");
            java.util.Arrays.fill(raw,(byte)0);
            if(words.length!=12)throw new Exception();
            UiScrollable grid=new UiScrollable(new UiSelector().packageName(APP).scrollable(true));
            grid.setMaxSearchSwipes(16);
            for(int i=0;i<12;i++) {
                if(!words[i].matches("[a-z]+"))throw new Exception();
                UiObject field=grid.getChildByText(new UiSelector().className("android.widget.EditText"),"#"+(i+1),true);
                if(!new Field(field.getSelector()).replace(words[i]))throw new Exception();
            }
            java.util.Arrays.fill(words,null);
            Bundle result=new Bundle();result.putString("stream","H02_PHRASE_FIELDS_FILLED; NOT_SUBMITTED\n");
            getAutomationSupport().sendStatus(0,result);
        } catch(Throwable ignored) {
            // Do not attach exceptions: UI/toolkit messages may contain entered text.
            fail("H02_PHRASE_ENTRY_REFUSED; NO_DETAILS");
        }
    }
}
