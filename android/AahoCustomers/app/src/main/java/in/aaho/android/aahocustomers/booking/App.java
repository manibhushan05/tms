package in.aaho.android.aahocustomers.booking;

import android.util.Log;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.aahocustomers.AahoOffice;
import in.aaho.android.aahocustomers.common.Prefs;
import in.aaho.android.aahocustomers.common.Utils;
import in.aaho.android.aahocustomers.drivers.ListDriversActivity;
import in.aaho.android.aahocustomers.loads.AvailableLoadsActivity;
import in.aaho.android.aahocustomers.profile.Profile;
import in.aaho.android.aahocustomers.vehicles.BankAccount;
import in.aaho.android.aahocustomers.vehicles.VehicleDriver;
import in.aaho.android.aahocustomers.vehicles.VehicleListActivity;
import in.aaho.android.aahocustomers.vehicles.VehicleOwner;

/**
 * Created by aaho on 14/06/18.
 */


public class App {

    private static Profile profile;

    public static void clearAppData() {
        City.clear();
        VehicleCategory.clear();
        Vendor.clear();
        Address.clear();
        App.clear();
        VehicleListActivity.getVehicleList().clear();
        ListDriversActivity.getDriverList().clear();
        AvailableLoadsActivity.getRequestList().clear();
        BankAccount.accountList.clear();
    }

    public static Profile getProfile() {
        if (profile == null) {
            profile = new Profile();
        }
        return profile;
    }

    private static void clear() {
        if (profile != null) {
            profile.clear();
        }
    }

    public static String nullToBlank(String str) {
        if (str == null) {
            return "";
        } else {
            return str.trim();
        }
    }

    public static String getUserName() {
        if (profile == null) {
            return "";
        } else {
            return Utils.def(profile.userFullName, "");
        }
    }

    public static void setUserData(JSONObject user) throws JSONException {
        Log.e("[user_data]", user.toString());
        profile = Profile.fromJson(user);
        Prefs.set("user_data", user.toString());
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
        if (profile != null) {
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
        BankAccount.setData(data.getJSONArray("accounts_data"));
        AahoOffice.setAahoOfficeData(data.getJSONObject("aaho_office"));
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

