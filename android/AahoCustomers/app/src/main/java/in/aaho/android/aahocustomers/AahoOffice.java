package in.aaho.android.aahocustomers;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.aahocustomers.common.Prefs;
import in.aaho.android.aahocustomers.common.Utils;

public class AahoOffice {

    private int id;

    public AahoOffice(int id) {
        this.id = id;
    }

    public static AahoOffice setAahoOfficeData(JSONObject aahoOfficeObject) throws JSONException {
        if (aahoOfficeObject == null) {
            return null;
        }
        int id = Integer.valueOf(Utils.get(aahoOfficeObject,"id"));
        String t1_phone = Utils.get(aahoOfficeObject,"t1_phone");
        Prefs.set("aaho_office_id", String.valueOf(id));
        Prefs.set("t1_phone_no", String.valueOf(t1_phone));

        AahoOffice aahoOffice = new  AahoOffice(id);

        return aahoOffice;
    }
}
