package in.aaho.android.aahocustomers.common;

import android.content.SharedPreferences;

/**
 * Created by aaho on 18/04/18.
 */

public class Prefs {

    public static boolean get(String key, boolean def) {
        SharedPreferences sharedPreferences = MainApplication.getPrefs();
        if (sharedPreferences == null) {
            return def;
        }
        return sharedPreferences.getBoolean(key, def);
    }

    public static String get(String key) {
        SharedPreferences sharedPreferences = MainApplication.getPrefs();
        if (sharedPreferences == null) {
            return null;
        }
        return sharedPreferences.getString(key, null);
    }

    public static String get(String key, String def) {
        String pref = get(key);
        if (pref == null) {
            return def;
        } else {
            return pref;
        }
    }

    public static boolean has(String key) {
        SharedPreferences sharedPreferences = MainApplication.getPrefs();
        if (sharedPreferences == null) {
            return false;
        }
        return sharedPreferences.contains(key);
    }

    public static void set(String key, String value) {
        SharedPreferences sharedPreferences = MainApplication.getPrefs();
        if (sharedPreferences == null) {
            return;
        }
        sharedPreferences.edit().putString(key, value).apply();
    }

    public static SharedPreferences.Editor editor() {
        SharedPreferences sharedPreferences = MainApplication.getPrefs();
        if (sharedPreferences == null) {
            return null;
        }
        return sharedPreferences.edit();
    }

}

