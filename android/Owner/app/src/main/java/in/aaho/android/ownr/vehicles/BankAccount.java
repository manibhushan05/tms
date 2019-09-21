package in.aaho.android.ownr.vehicles;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

import in.aaho.android.ownr.common.Utils;

/**
 * Created by shobhit on 26/10/16.
 */

public class BankAccount {
    public static final List<BankAccount> accountList = new ArrayList<>();

    public Long id = null;

    public String bank = null;
    public String accountType;
    public String accountNumber;
    public String accountHolderName;
    public String ifsc;
    public String userName;

    public BankAccount(Long id, String bank, String accountType, String accountNumber, String accountHolderName, String ifsc) {
        this.id = id;
        this.bank = bank;
        this.accountType = accountType;
        this.accountNumber = accountNumber;
        this.accountHolderName = accountHolderName;
        this.ifsc = ifsc;
    }

    public static void add(BankAccount account) {
        boolean found = false;
        for (int i = 0; i < accountList.size(); i++) {
            BankAccount ac = accountList.get(i);
            if (Utils.equals(account.id, ac.id)) {
                accountList.set(i, account);
                found = true;
            }
        }
        if (!found) {
            accountList.add(account);
        }
    }

    public JSONObject toJson() throws JSONException {
        JSONObject jsonObject = new JSONObject();
        put(jsonObject, "bank", bank);
        put(jsonObject, "account_type", accountType);
        put(jsonObject, "account_number", accountNumber);
        put(jsonObject, "account_holder_name", accountHolderName);
        put(jsonObject, "ifsc", ifsc);
        if (id != null) {
            jsonObject.put("id", id);
        }
        return jsonObject;
    }

    private void put(JSONObject jsonObject, String key, String value) throws JSONException {
        if (value != null) {
            jsonObject.put(key, value);
        }
    }

    public static List<BankAccount> fromJson(JSONArray jsonArray) throws JSONException {
        List<BankAccount> accounts = new ArrayList<>();
        if (jsonArray == null) {
            return accounts;
        }
        for (int i = 0; i < jsonArray.length(); i++) {
            JSONObject obj = jsonArray.getJSONObject(i);
            if (obj != null) {
                accounts.add(fromJson(obj));
            }
        }
        return accounts;
    }

    public static BankAccount fromJson(JSONObject jsonObject) throws JSONException {
        if (jsonObject == null) {
            return null;
        }
        BankAccount account =  new BankAccount(
                Utils.getLong(jsonObject, "id"),
                Utils.get(jsonObject, "bank"),
                Utils.get(jsonObject, "account_type"),
                Utils.get(jsonObject, "account_number"),
                Utils.get(jsonObject, "account_holder_name"),
                Utils.get(jsonObject, "ifsc")
        );
        return account;
    }

    public static void setData(JSONArray accountsData) throws JSONException {
        accountList.clear();
        for (int i = 0; i < accountsData.length(); i++) {
            JSONObject obj = accountsData.getJSONObject(i);
            accountList.add(fromJson(obj));
        }
    }

    public static BankAccount copy(BankAccount other) {
        if (other == null) {
            return null;
        }
        return new BankAccount(
                other.id, other.bank, other.accountType, other.accountNumber, other.accountHolderName,
                other.ifsc
        );
    }

    public boolean notSet() {
        return id == null;
    }

    public String title() {
        String title = "";
        if (!Utils.not(accountHolderName)) {
            title += accountHolderName.trim() + " - ";
        }
        if (!Utils.not(bank)) {
            title += bank.trim() + ", ";
        }
        if (!Utils.not(accountNumber)) {
            title += accountNumber.trim();
        }
        return title;
    }


    public BankAccount(String userName, String bank, String accountType,
                       String accountNumber, String accountHolderName, String ifsc) {
        this.userName = userName;
        this.bank = bank;
        this.accountType = accountType;
        this.accountNumber = accountNumber;
        this.accountHolderName = accountHolderName;
        this.ifsc = ifsc;
    }

    public JSONObject toJsonObject() throws JSONException {
        JSONObject jsonObject = new JSONObject();
        put(jsonObject, "bank", bank);
        put(jsonObject, "account_type", accountType);
        put(jsonObject, "account_number", accountNumber);
        put(jsonObject, "account_holder_name", accountHolderName);
        put(jsonObject, "ifsc", ifsc);
        put(jsonObject,"user", userName);

        return jsonObject;
    }

    public static BankAccount fromJsonObject(JSONObject jsonObject) throws JSONException {
        if (jsonObject == null) {
            return null;
        }
        BankAccount account =  new BankAccount(
                /*Utils.get(jsonObject, "user"),*/
                Utils.getLong(jsonObject, "id"),
                Utils.get(jsonObject, "bank"),
                Utils.get(jsonObject, "account_type"),
                Utils.get(jsonObject, "account_number"),
                Utils.get(jsonObject, "account_holder_name"),
                Utils.get(jsonObject, "ifsc")
        );
        return account;
    }

}
