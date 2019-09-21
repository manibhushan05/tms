package in.aaho.android.aahocustomers.booking;

import android.text.Html;
import android.text.Spanned;

import org.json.JSONArray;
import org.json.JSONException;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import in.aaho.android.aahocustomers.common.Prefs;

/**
 * Created by mani on 19/8/16.
 */
public class Address {
    public String address;
    public City city;

    private static Map<String, Double> addressScoreMap = new HashMap<>();
    private static List<String> rankedAddresses = new ArrayList<>();

    private static Map<String, Address> addressMap = new HashMap<>();
    private static List<Address> addresses = new ArrayList<>();

    private static AddrScoreComparator addrScoreComparator = new AddrScoreComparator();

    private String query;

    private Address(String address, Long cityId) {
        this.address = address;
        this.city = City.get(cityId);
        addressMap.put(this.address, this);
        addresses.add(this);
    }

    public static void clear() {
        addresses.clear();
        addressMap.clear();
        addressScoreMap.clear();
        rankedAddresses.clear();
    }

    public static List<Address> getAll() {
        return addresses;
    }

    public static boolean hasNoScores() {
        return rankedAddresses.isEmpty();
    }

    public static void setUpRankings(JSONArray addrScores) throws JSONException {
        clear();
        for (int i = 0; i < addrScores.length(); i++) {
            JSONArray addrScore = addrScores.getJSONArray(i);
            String addr = addrScore.getString(0);
            Long cityId = addrScore.getLong(1);
            Double score = addrScore.getDouble(2);
            new Address(addr, cityId);
            rankedAddresses.add(addr);
            addressScoreMap.put(addr, score);
        }
        Prefs.set("address_scores_data", addrScores.toString());
    }

    public Spanned getAutoCompleteText() {
        if (query == null) {
            return getFullNameHtml();
        }
        return getAutoCompleteText2();
    }

    private Spanned getAutoCompleteText2() {
        int match_size = query.length();
        int start = address.toLowerCase().indexOf(query);
        String emphName = address.substring(0, start) + "<b>" +
                address.substring(start, start + match_size) + "</b>" +
                address.substring(start + match_size, address.length());
        return Html.fromHtml(emphName);
    }


    public String searchTerm() {
        return (address == null || address.trim().length() == 0) ? null : address.trim().toLowerCase();
    }

    public Spanned getFullNameHtml() {
        return Html.fromHtml(getFullName());
    }

    public String getFullName() {
        return address == null ? "" : address;
    }

    public static List<String> getRankedAddresses() {
        return rankedAddresses;
    }

    public static Address get(String s) {
        return addressMap.get(s);
    }

    public void setQuery(String query) {
        this.query = query == null ? null : query.trim().toLowerCase();
    }

    public static void sortAddresses(List<Address> suggestions) {
        Collections.sort(suggestions, addrScoreComparator);
    }

    private static double getAddrScore(String address) {
        Double score = addressScoreMap.get(address);
        return score == null ? 0 : score;
    }

    private static class AddrScoreComparator implements Comparator<Address> {
        @Override
        public int compare(Address lhs, Address rhs) {
            return (-1) * Double.compare(getAddrScore(lhs.address), getAddrScore(rhs.address));
        }
    }
}
