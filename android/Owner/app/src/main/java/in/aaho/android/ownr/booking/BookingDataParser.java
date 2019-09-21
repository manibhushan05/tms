package in.aaho.android.ownr.booking;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

import in.aaho.android.ownr.data.PendingTransactionData;

/**
 * Created by mani on 19/9/17.
 */

public class BookingDataParser {
    private JSONArray jsonArray;
    private ArrayList<PendingBookingData> pendingBookingDataArrayList;
    private ArrayList<CompletedBookingData> completedBookingDataArrayList;

    public BookingDataParser(JSONArray jsonArray) {
        this.jsonArray = jsonArray;
    }

    public BookingDataParser() {

    }

    public JSONArray getJsonArray() {
        return jsonArray;
    }

    public void setJsonArray(JSONArray jsonArray) {
        this.jsonArray = jsonArray;
    }


    public ArrayList<CompletedBookingData> getCompletedBookingDataArrayList() {
        return completedBookingDataArrayList;
    }

    public ArrayList<PendingBookingData> getPendingBookingDataArrayList() {
        pendingBookingDataArrayList =new ArrayList<>();
        return pendingBookingDataArrayList;
    }
}
