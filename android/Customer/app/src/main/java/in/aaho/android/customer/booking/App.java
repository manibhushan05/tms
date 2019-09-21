package in.aaho.android.customer.booking;

import android.util.Log;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.customer.common.Prefs;

/**
 * Created by shobhit on 12/8/16.
 *
 *
 */
public class App {
    public static String userFullName, username, userPhone, userEmail, userDesignation, userContactName;
    public static Long userId;

    public static void clearAppData() {
        City.clear();
        VehicleCategory.clear();
        Vendor.clear();
        Address.clear();
        App.clear();
    }

    private static void clear() {
        setPrefs(null, null, null, null, null, null, null);
        UserAddress.clear();
    }

    private static void setPrefs(String mUserFullName, String mUserContactName, String mUsername,
                                 String mUserPhone, String mUserEmail, String mUserDesignation,
                                 Long mUserId) {
        userFullName = mUserFullName;
        userContactName = mUserContactName;
        username = mUsername;
        userPhone = mUserPhone;
        userEmail = mUserEmail;
        userDesignation = mUserDesignation;
        userId = mUserId;
    }

    public static String nullToBlank(String str) {
        if (str == null) {
            return "";
        } else {
            return str.trim();
        }
    }

    public static String getUserName() {
        if (userFullName == null) {
            return "";
        } else {
            return userFullName;
        }
    }

    public static void setUserData(JSONObject user) throws JSONException {
        Log.e("[user_data]", user.toString());
        userFullName = nullToBlank(user.getString("full_name"));
        userContactName = nullToBlank(user.getString("contact_name"));
        UserAddress.updateAddress(user.getJSONObject("address"));
        username = nullToBlank(user.getString("username"));
        userPhone = nullToBlank(user.getString("phone"));
        userEmail = nullToBlank(user.getString("email"));
        userDesignation = nullToBlank(user.getString("designation"));
        userId = user.getLong("id");
        Prefs.set("user_data", user.toString());
    }

    public static JSONObject getUpdatedUserProfileJson(String name, String contactName,
                                                 String contactPhone, String contactEmail,
                                                 String contactDesignation) throws JSONException {
        JSONObject jsonObject = new JSONObject();
        if (!App.equal(App.userFullName, name)) {
            jsonObject.put("full_name", name == null ? JSONObject.NULL : name);
        }
        if (!App.equal(App.userContactName, contactName)) {
            jsonObject.put("contact_name", contactName == null ? JSONObject.NULL : contactName);
        }
        if (!UserAddress.get().isSynced()) {
            jsonObject.put("address", UserAddress.get().toJson());
        }
        if (!App.equal(App.userPhone, contactPhone)) {
            jsonObject.put("phone", contactPhone == null ? JSONObject.NULL : contactPhone);
        }
        if (!App.equal(App.userEmail, contactEmail)) {
            jsonObject.put("email", contactEmail == null ? JSONObject.NULL : contactEmail);
        }
        if (!App.equal(App.userDesignation, contactDesignation)) {
            jsonObject.put("designation", contactDesignation == null ? JSONObject.NULL : contactDesignation);
        }
        return jsonObject;
    }

    public static void setFromSharedPreferencesIfNeeded() {
        setCityDataFromSharedPreferences();
        setVehicleDataFromSharedPreferences();
        setVendorDataFromSharedPreferences();
        setCityScoresFromSharedPreferences();
        setAddrScoresFromSharedPreferences();
        setUserFromSharedPreferences();
    }

    public static void setUserFromSharedPreferences() {
        if (username != null) {
            return;
        }
        String data = Prefs.get("user_data");
        if (data == null) {
            return;
        }
        try {
            JSONObject userData = new JSONObject(data);
            App.setUserData(userData);
        } catch (JSONException e) {
            return;
        }
    }

    public static void setCityDataFromSharedPreferences() {
        if (!City.isEmpty()) {
            return;
        }
        String data = Prefs.get("city_data");
        if (data == null) {
            return;
        }
        try {
            JSONArray jsonArray = new JSONArray(data);
            City.createFromJson(jsonArray);
        } catch (JSONException e) {
            return;
        }
    }

    public static void setVehicleDataFromSharedPreferences() {
        if (!VehicleCategory.isEmpty()) {
            return;
        }
        String data = Prefs.get("vehicle_data");
        if (data == null) {
            return;
        }
        try {
            JSONArray jsonArray = new JSONArray(data);
            VehicleCategory.createFromJson(jsonArray);
        } catch (JSONException e) {
            return;
        }
    }

    public static void setVendorDataFromSharedPreferences() {
        if (!Vendor.isEmpty()) {
            return;
        }
        String data = Prefs.get("vendor_data");
        if (data == null) {
            return;
        }
        try {
            JSONArray jsonArray = new JSONArray(data);
            Vendor.createFromJson(jsonArray);
        } catch (JSONException e) {
            return;
        }
    }

    public static void setCityScoresFromSharedPreferences() {
        if (!City.hasNoScores()) {
            return;
        }
        String data = Prefs.get("city_scores_data");
        if (data == null) {
            return;
        }
        try {
            JSONArray jsonArray = new JSONArray(data);
            City.setUpRankings(jsonArray);
        } catch (JSONException e) {
            return;
        }
    }

    public static void setAddrScoresFromSharedPreferences() {
        if (!Address.hasNoScores()) {
            return;
        }
        String data = Prefs.get("address_scores_data");
        if (data == null) {
            return;
        }
        try {
            JSONArray jsonArray = new JSONArray(data);
            Address.setUpRankings(jsonArray);
        } catch (JSONException e) {
            return;
        }
    }

    public static void createAppData(String resp) throws JSONException {
        clearAppData();

        JSONObject respData = new JSONObject(resp);
        JSONObject data = respData.getJSONObject("data");

        City.createFromJson(data.getJSONArray("cities"));
        VehicleCategory.createFromJson(data.getJSONArray("vehicles"));
        Vendor.createFromJson(data.getJSONArray("vendors"));
        City.setUpRankings(data.getJSONArray("city_scores"));
        Address.setUpRankings(data.getJSONArray("address_scores"));
        App.setUserData(data.getJSONObject("user"));
    }

    public static void updateAppData(JSONObject data) throws JSONException {
        City.setUpRankings(data.getJSONArray("city_scores"));
        Address.setUpRankings(data.getJSONArray("address_scores"));
        Vendor.clear();
        Vendor.createFromJson(data.getJSONArray("vendors"));
        AddressArrayAdapter.shouldRefresh = true;
    }

    public static boolean equal(String str1, String str2) {
        return (str1 == null ? str2 == null : str1.equals(str2));
    }
}
