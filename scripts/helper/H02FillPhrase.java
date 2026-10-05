package h02;

import android.os.Bundle;
import android.view.accessibility.AccessibilityNodeInfo;
import com.android.uiautomator.core.*;
import com.android.uiautomator.testrunner.UiAutomatorTestCase;
import org.json.JSONObject;
import java.nio.charset.StandardCharsets;

/** Test-only normal UI automation. No screenshots, hierarchy dumps, clipboard,
 * direct key-store writes or production Application loading.
 * Secret inputs travel via an app-private temporary file, never command arguments.
 * Public actions and private input methods are invoked individually by the host.
 */
public final class H02FillPhrase extends UiAutomatorTestCase {
    private static final String APP="com.rjnr.pocketnode";
    public void testPublicTap() {
        String stage="foreground";
        try {
            if(!APP.equals(getUiDevice().getCurrentPackageName()))throw new Exception();
            String id=getParams().getString("publicId");
            String encoded=getParams().getString("publicTextB64");
            String text=encoded==null?null:new String(android.util.Base64.decode(encoded,android.util.Base64.NO_WRAP),StandardCharsets.UTF_8);
            UiSelector selector=new UiSelector().packageName(APP);
            if(id!=null)selector=selector.resourceId(id);
            else if(text!=null)selector=selector.text(text);
            else throw new Exception();
            UiObject target=new UiObject(selector);
            stage="exists";if(!target.waitForExists(20000))throw new Exception();
            stage="enabled";if(!target.isEnabled())throw new Exception();
            stage="click";if(!new Field(selector).activate())throw new Exception();
            Bundle result=new Bundle();result.putString("stream","H02_PUBLIC_TAP_OK\n");
            getAutomationSupport().sendStatus(0,result);
        } catch(Throwable ignored) {fail("H02_PUBLIC_TAP_REFUSED; STAGE="+stage);}
    }
    public void testPublicState() {
        try {
            String[] texts={"Welcome to Pocket Node","Choose Sync Start Point","Create a PIN","Choose a 6-digit PIN","Confirm PIN","Enter PIN","Invalid mnemonic. Please check your words and try again.","Please fill in all 12 words","Settings","Home","Recover Wallet"};
            StringBuilder s=new StringBuilder();
            for(int i=0;i<texts.length;i++)if(new UiObject(new UiSelector().packageName(APP).text(texts[i])).exists())s.append("H02_PUBLIC_STATE_").append(i).append("\n");
            UiObject submit=new UiObject(new UiSelector().packageName(APP).resourceId("import-submit"));
            if(submit.exists())s.append(submit.isEnabled()?"H02_IMPORT_ENABLED\n":"H02_IMPORT_DISABLED\n");
            Bundle result=new Bundle();result.putString("stream",s.toString()+"H02_PUBLIC_STATE_OK\n");getAutomationSupport().sendStatus(0,result);
        } catch(Throwable ignored) {fail("H02_PUBLIC_STATE_REFUSED");}
    }
    public void testEnterPrivatePin() {
        try {
            if(!APP.equals(getUiDevice().getCurrentPackageName()))throw new Exception();
            String path=getParams().getString("fixture");
            if(path==null||!path.matches("/data/user/0/com\\.rjnr\\.pocketnode/files/h02-pin-[a-f0-9]{16}\\.json"))throw new Exception();
            Process p=new ProcessBuilder("run-as",APP,"cat",path).start();
            byte[] raw=p.getInputStream().readAllBytes();if(p.waitFor()!=0||raw.length>1024)throw new Exception();
            String pin=new JSONObject(new String(raw,StandardCharsets.UTF_8)).getString("pin");
            java.util.Arrays.fill(raw,(byte)0);if(!pin.matches("[0-9]{6}"))throw new Exception();
            // Clear a partial entry from a prior refused automation action.
            UiSelector delete=new UiSelector().packageName(APP).description("Delete");
            for(int i=0;i<6;i++) {
                if(!new UiObject(delete).exists()||!new Field(delete).activate())break;
                android.os.SystemClock.sleep(80);
            }
            for(int i=0;i<6;i++) {
                UiSelector selector=new UiSelector().packageName(APP).resourceId("pin-keypad-"+pin.charAt(i));
                UiObject key=new UiObject(selector);
                if(!key.waitForExists(3000)||!new Field(selector).activate())throw new Exception();
                android.os.SystemClock.sleep(120);
            }
            pin=null;
            Bundle result=new Bundle();result.putString("stream","H02_PRIVATE_PIN_ENTERED\n");getAutomationSupport().sendStatus(0,result);
        } catch(Throwable ignored) {fail("H02_PRIVATE_PIN_REFUSED; NO_DETAILS");}
    }
    static final class Field extends UiObject {
        Field(UiSelector selector) {super(selector);}
        boolean activate() {
            AccessibilityNodeInfo node=findAccessibilityNodeInfo(3000);
            for(int i=0;i<5 && node!=null;i++,node=node.getParent()) {
                if(!APP.contentEquals(node.getPackageName()))return false;
                if(node.isClickable())return node.performAction(AccessibilityNodeInfo.ACTION_CLICK);
            }
            return false;
        }
        AccessibilityNodeInfo editable() {
            AccessibilityNodeInfo node=findAccessibilityNodeInfo(3000);
            for(int i=0;i<4 && node!=null;i++,node=node.getParent()) {
                if(!APP.contentEquals(node.getPackageName())) return null;
                if(node.isEditable()) return node;
            }
            return null;
        }
        boolean replace(String word) {
            for(int attempt=0;attempt<3;attempt++) {
                AccessibilityNodeInfo node=editable();
                if(node!=null) {
                    Bundle b=new Bundle();b.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE,word);
                    // Deliberately avoid UiObject.setText/sendText logging paths.
                    boolean ok=node.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT,b);
                    if(ok) for(int wait=0;wait<20;wait++) {
                        android.os.SystemClock.sleep(50);
                        node.refresh();
                        if(node.getText()!=null && node.getText().toString().equals(word))return true;
                        AccessibilityNodeInfo fresh=editable();
                        if(fresh!=null && fresh.getText()!=null && fresh.getText().toString().equals(word))return true;
                    }
                }
                android.os.SystemClock.sleep(100);
            }
            return false;
        }
    }
    public void testFillOnly() {
        String stage="parameters";
        try {
            String path=getParams().getString("fixture");
            if(path==null || !path.matches("/data/user/0/com\\.rjnr\\.pocketnode/files/h02-phrase-[a-f0-9]{16}\\.json")) throw new Exception();
            stage="foreground";
            if(!APP.equals(getUiDevice().getCurrentPackageName()))throw new Exception();
            stage="import-screen";
            if(!new UiObject(new UiSelector().resourceId("import-submit")).exists() &&
               !new UiObject(new UiSelector().text("Import Wallet")).exists())throw new Exception();
            stage="private-input";
            Process p=new ProcessBuilder("run-as",APP,"cat",path).start();
            byte[] raw=p.getInputStream().readAllBytes();
            if(p.waitFor()!=0 || raw.length>4096)throw new Exception();
            String[] words=new JSONObject(new String(raw,StandardCharsets.UTF_8)).getString("mnemonic").split(" ");
            java.util.Arrays.fill(raw,(byte)0);
            if(words.length!=12)throw new Exception();
            UiScrollable grid=new UiScrollable(new UiSelector().packageName(APP).scrollable(true));
            grid.setMaxSearchSwipes(16);
            for(int i=0;i<12;i++) {
                stage="locate-field-"+(i+1);
                if(!words[i].matches("[a-z]+"))throw new Exception();
                UiObject field=grid.getChildByText(new UiSelector().className("android.widget.EditText"),"#"+(i+1),true);
                stage="set-field-"+(i+1);
                if(!new Field(field.getSelector()).replace(words[i]))throw new Exception();
            }
            java.util.Arrays.fill(words,null);
            Bundle result=new Bundle();result.putString("stream","H02_PHRASE_FIELDS_FILLED; NOT_SUBMITTED\n");
            getAutomationSupport().sendStatus(0,result);
        } catch(Throwable ignored) {
            // Do not attach exceptions: UI/toolkit messages may contain entered text.
            fail("H02_PHRASE_ENTRY_REFUSED; STAGE="+stage);
        }
    }
}
