package in.aaho.android.aahocustomers.drivers;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.aahocustomers.common.Utils;
import in.aaho.android.aahocustomers.docs.Document;
import in.aaho.android.aahocustomers.vehicles.BankAccount;


/**
 * Created by mani on 6/8/16.
 */
public class BrokerDriverDetails {

    public Long id = null;
    public String name;
    public String phone;

    public Document panDoc = null;
    public Document dlDoc = null;

    public BankAccount account;

    public static final String ID_KEY = "id";
    public static final String NAME_KEY = "name";
    public static final String PHONE_KEY = "phone";
    public static final String ACCOUNT_KEY = "account";

    public static final String PAN_DOC_KEY = "pan_doc";
    public static final String DL_DOC_KEY = "dl_doc";

    public BrokerDriverDetails() {

    }

    public JSONObject toJson() throws JSONException {
        JSONObject jsonObject = new JSONObject();
        addDoc(jsonObject, PAN_DOC_KEY, panDoc);
        addDoc(jsonObject, DL_DOC_KEY, dlDoc);
        addString(jsonObject, NAME_KEY, name);
        addString(jsonObject, PHONE_KEY, phone);
        addAccount(jsonObject);
        if (id != null) {
            jsonObject.put(ID_KEY, id);
        }
        return jsonObject;
    }

    private void addAccount(JSONObject jsonObject) throws JSONException {
        if (account != null) {
            jsonObject.put(ACCOUNT_KEY, account.toJson());
        }
    }

    private void addString(JSONObject jsonObject, String key, String value) throws JSONException {
        if (value != null) {
            jsonObject.put(key, value);
        }
    }

    private void addDoc(JSONObject jsonObject, String key, Document document) throws JSONException {
        if (document != null && document.isModified()) {
            jsonObject.put(key, document.toJson());
        }
    }

    public static BrokerDriverDetails fromJson(JSONObject jsonObject) throws JSONException {
        BrokerDriverDetails driver = new BrokerDriverDetails();

        driver.id = jsonObject.getLong(ID_KEY);
        driver.name = Utils.get(jsonObject, NAME_KEY);
        driver.phone = Utils.get(jsonObject, PHONE_KEY);


        if (jsonObject.has(PAN_DOC_KEY) && !jsonObject.isNull(PAN_DOC_KEY)) {
            JSONObject docObj = jsonObject.getJSONObject(PAN_DOC_KEY);
            driver.panDoc = Document.fromJson(docObj, Document.PAN_DOC_TYPE);
        }

        if (jsonObject.has(DL_DOC_KEY) && !jsonObject.isNull(DL_DOC_KEY)) {
            JSONObject docObj = jsonObject.getJSONObject(DL_DOC_KEY);
            driver.dlDoc = Document.fromJson(docObj, Document.DL_DOC_TYPE);
        }

        if (jsonObject.has(ACCOUNT_KEY) && !jsonObject.isNull(ACCOUNT_KEY)) {
            JSONObject accountDetails = jsonObject.getJSONObject(ACCOUNT_KEY);
            driver.account = BankAccount.fromJson(accountDetails);
        }

        return driver;
    }


    public static BrokerDriverDetails copy(BrokerDriverDetails other) {
        if (other == null) {
            return null;
        }
        BrokerDriverDetails details = new BrokerDriverDetails();
        details.id = other.id;
        details.name = other.name;
        details.phone = other.phone;

        details.panDoc = Document.copy(other.panDoc);
        details.dlDoc = Document.copy(other.dlDoc);
        details.account = BankAccount.copy(other.account);
        return details;
    }
}
