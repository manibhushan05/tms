package in.aaho.android.ownr.drivers;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.ownr.common.Utils;
import in.aaho.android.ownr.vehicles.BankAccount;
import in.aaho.android.ownr.docs.Document;


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
    public static final String ACCOUNT_KEY = "account_details";
    public static final String ACCOUNT_ID_KEY = "account_id";

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
            jsonObject.put(ACCOUNT_ID_KEY, account.id);
            /*jsonObject.put(ACCOUNT_KEY, account.toJson());*/
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

    public static BrokerDriverDetails fromJsonObject(JSONObject jsonObject) throws JSONException {
        BrokerDriverDetails driver = new BrokerDriverDetails();

        driver.id = jsonObject.getLong(ID_KEY);
        driver.name = Utils.get(jsonObject, NAME_KEY);
        driver.phone = Utils.get(jsonObject, PHONE_KEY);


        JSONArray jsonArrayDocuments = jsonObject.getJSONArray("docs");
        for (int i = 0; i < jsonArrayDocuments.length(); i++) {
            JSONObject jsonObjectDoc = jsonArrayDocuments.getJSONObject(i);
            if (jsonObjectDoc != null) {
                if (jsonObjectDoc.has(Document.DOCUMENT_CATEGORY_KEY)) {
                    String docCategory = jsonObjectDoc.getString(Document.DOCUMENT_CATEGORY_KEY);
                    if (docCategory.equalsIgnoreCase("PAN")) {
                        driver.panDoc = Document.fromJsonObjectDriver(jsonObject,
                                jsonObjectDoc,Document.PAN_DOC_TYPE,docCategory);
                    } else if (docCategory.equalsIgnoreCase("DL")) {
                        driver.dlDoc = Document.fromJsonObjectDriver(jsonObject,
                                jsonObjectDoc,Document.DL_DOC_TYPE,docCategory);
                    } else {
                        // do nothing
                    }
                }
            }
        }

        if (jsonObject.has(ACCOUNT_KEY) && !jsonObject.isNull(ACCOUNT_KEY)) {
            JSONObject accountDetails = jsonObject.getJSONObject(ACCOUNT_KEY);
            driver.account = BankAccount.fromJson(accountDetails);
        }

        return driver;
    }
}
