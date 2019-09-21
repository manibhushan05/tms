package in.aaho.android.driver.common;

import android.annotation.TargetApi;
import android.content.Context;
import android.content.res.Configuration;
import android.content.res.Resources;
import android.os.Build;
import android.util.Log;

import java.util.HashMap;
import java.util.Locale;
import java.util.Map;

/**
 * Created by shobhit on 17/1/17.
 */

public class Lang {

    private static final String LANGUAGE_PREF_KEY = "language";

    private static final Lang[] LANGUAGES = new Lang[] {
            new Lang("en", "English"),
            new Lang("hi", "हिंदी"),
            new Lang("te", "తెలుగు")
    };
    private static final Lang DEFAULT_LANG = LANGUAGES[0];
    private static final Map<String, Lang> LANGUAGE_MAP = getLangMap();

    private static Map<String, Lang> getLangMap() {
        Map<String, Lang> langMap = new HashMap<>();
        for (Lang lang :  LANGUAGES) {
            langMap.put(lang.code, lang);
        }
        return langMap;
    }

    public static Lang[] getLanguages() {
        return LANGUAGES;
    }

    public static Lang getLanguage() {
        String lang = Prefs.get(LANGUAGE_PREF_KEY);
        if (lang == null) {
            // no language set get device locale
            lang = Locale.getDefault().getLanguage();
        }
        // if our app does not support the default locale, default to en
        if (!LANGUAGE_MAP.containsKey(lang)) {
            lang = DEFAULT_LANG.code;
        }
        return LANGUAGE_MAP.get(lang);
    }

    public static boolean setLanguage(String lang) {
        boolean isValid = isChangeValid(lang);
        if (isValid) {
            Prefs.set(LANGUAGE_PREF_KEY, lang);
            return true;
        }
        return false;
    }

    private static boolean isChangeValid(String lang) {
        if (Utils.not(lang)) {
            Log.e("[LANG]", "Language: <blank>");
            return false;
        }
        if (!LANGUAGE_MAP.containsKey(lang)) {
            Log.e("[LANG]", "Unsupported language: " + lang);
            return false;
        }
        if (getLanguage().code.equals(lang)) {
            Log.w("[LANG]", "Nothing to update");
            return false;
        }
        return true;
    }


    public final String code;
    public final String name;

    private Lang(String code, String name) {
        this.code = code;
        this.name = name;
    }

    public static Context onAttach(Context context) {
        String lang = Lang.getLanguage().code;
        return setLocale(context, lang);
    }

    private static Context setLocale(Context context, String language) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            return updateResources(context, language);
        }

        return updateResourcesLegacy(context, language);
    }

    @TargetApi(Build.VERSION_CODES.N)
    private static Context updateResources(Context context, String language) {
        Locale locale = new Locale(language);
        Locale.setDefault(locale);

        Configuration configuration = context.getResources().getConfiguration();
        configuration.setLocale(locale);

        return context.createConfigurationContext(configuration);
    }

    @SuppressWarnings("deprecation")
    private static Context updateResourcesLegacy(Context context, String language) {
        Locale locale = new Locale(language);
        Locale.setDefault(locale);

        Resources resources = context.getResources();

        Configuration configuration = resources.getConfiguration();
        configuration.locale = locale;

        resources.updateConfiguration(configuration, resources.getDisplayMetrics());

        return context;
    }

    public boolean isCurrent() {
        return code.equals(Lang.getLanguage().code);
    }
}
