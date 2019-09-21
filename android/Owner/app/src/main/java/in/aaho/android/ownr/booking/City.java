package in.aaho.android.ownr.booking;

import android.text.Html;
import android.text.Spanned;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import in.aaho.android.ownr.common.Prefs;

/**
 * Created by mani on 9/8/16.
 */
public class City {
    private static Map<Long, City> cityMap = new HashMap<>();
    private static List<City> cities = new ArrayList<>();

    private static Map<Long, Double> cityScoreMap = new HashMap<>();
    private static List<Long> rankedCities = new ArrayList<>();

    private static CityScoreComparator cityScoreComparator = new CityScoreComparator();

    public static final String ID_KEY = "id";
    public static final String NAME_KEY = "name";
    public static final String STATE_KEY = "state";

    public long id;
    public String name;
    public String state;

    private String query;

    private City(long id, String name, String state) {
        this.id = id;
        this.name = name;
        this.state = state;
        cityMap.put(this.id, this);
        cities.add(this);
    }

    public static void clear() {
        cityMap.clear();
        cities.clear();
        cityScoreMap.clear();
        rankedCities.clear();
    }

    public static City get(long id) {
        return cityMap.get(id);
    }

    public static List<City> getAll() {
        return cities;
    }

    public static boolean isEmpty() {
        return cities.isEmpty();
    }

    public static boolean hasNoScores() {
        return rankedCities.isEmpty();
    }

    public static void createFromJson(JSONArray jsonArray) throws JSONException {
        clear();
        for (int i = 0; i < jsonArray.length(); i++) {
            JSONObject cityObj = jsonArray.getJSONObject(i);
            new City(cityObj.getLong("id"), cityObj.getString("name"), cityObj.getString("state"));
        }
        Prefs.set("city_data", jsonArray.toString());
    }

    @Override
    public String toString() {
        return name;
    }

    public JSONObject toJson() {
        JSONObject ret = new JSONObject();
        try {
            ret.put(ID_KEY, id);
            ret.put(NAME_KEY, name == null ? JSONObject.NULL : name);
            ret.put(STATE_KEY, state == null ? JSONObject.NULL : state);
        } catch (JSONException e) {
        }
        return ret;
    }

    public void setQuery(String query) {
        this.query = query == null ? null : query.trim().toLowerCase();
    }

    public Spanned getFullNameHtml() {
        String fullName = "";
        if (name != null && state != null) {
            fullName = name + ", <i>" + state + "</i>";
        }
        return Html.fromHtml(fullName);
    }

    public String getFullName() {
        if (name != null && state != null) {
            return name + ", " + state;
        } else {
            return "";
        }
    }

    public Spanned getAutocompleteText() {
        if (query == null) {
            return getFullNameHtml();
        }
        if (!searchTerm().startsWith(query)) {
            return getFullNameHtml();
        } else {
            return getAutoCompleteText2();
        }

    }

    private Spanned getAutoCompleteText2() {
        int match_size = query.length();
        String emphName = "<b>" + name.substring(0, match_size) + "</b>" + name.substring(match_size, name.length());
        return Html.fromHtml(emphName + ", <i>" + state + "</i>");
    }

    public String searchTerm() {
        return (name == null || name.trim().length() == 0) ? null : name.trim().toLowerCase();
    }

    public static List<Long> getRankedCities() {
        return rankedCities;
    }

    public static void setUpRankings(JSONArray cityScores) throws JSONException {
        rankedCities.clear();
        cityScoreMap.clear();
        for (int i = 0; i < cityScores.length(); i++) {
            JSONArray cityScore = cityScores.getJSONArray(i);
            Long city = cityScore.getLong(0);
            Double score = cityScore.getDouble(1);
            rankedCities.add(city);
            cityScoreMap.put(city, score);
        }
        Prefs.set("city_scores_data", cityScores.toString());
    }

    public static void sortCities(List<City> suggestions) {
        Collections.sort(suggestions, cityScoreComparator);
    }

    private static double getCityScore(long cityId) {
        Double score = cityScoreMap.get(cityId);
        return score == null ? 0 : score;
    }

    private static class CityScoreComparator implements Comparator<City> {
        @Override
        public int compare(City lhs, City rhs) {
            return (-1) * Double.compare(getCityScore(lhs.id), getCityScore(rhs.id));
        }
    }

    public static boolean equal(City city1, City city2) {
        if (city1 == null && city2 == null) {
            return true;
        } else if (city1 == null || city2 == null) {
            return false;
        } else {
            return city1.id == city2.id;
        }
    }
}
