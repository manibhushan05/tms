package in.aaho.android.ownr.parser;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

import in.aaho.android.ownr.data.PendingTransactionData;

/**
 * Created by mani on 28/7/16.
 */
public class PendingTransactionDataParser {
    private JSONArray jsonArray;
    private ArrayList<PendingTransactionData> pendingTransactionDataArrayList;

    public PendingTransactionDataParser() {
    }


    public PendingTransactionDataParser(JSONArray jsonArray) {
        this.jsonArray = jsonArray;
        setJsonArray(jsonArray);
    }

    public void setData() {

    }

    public JSONArray getJsonArray() {
        return jsonArray;
    }

    public void setJsonArray(JSONArray jsonArray) {
        this.jsonArray = jsonArray;
    }

    public ArrayList<PendingTransactionData> getPendingTransactionDataArrayList() {
        pendingTransactionDataArrayList = new ArrayList<>();
        for (int i = 0; i < getJsonArray().length(); i++) {
            try {
                JSONObject value = (JSONObject)getJsonArray() .get(i);
                PendingTransactionData pendingTransactionData = new PendingTransactionData();
                pendingTransactionData.setTransactionId(value.getString("transaction_id"));
                pendingTransactionData.setpickupFrom(value.getString("source_city"));
                pendingTransactionData.setdropAt(value.getString("destination_city"));
                pendingTransactionData.setShipmentDate(value.getString("shipment_date"));
                pendingTransactionData.setNumberOfVehicle(value.getString("total_vehicle_requested"));
                pendingTransactionData.setMaterial(value.getString("material"));
                pendingTransactionData.setNumberOfQuotes(value.getString("total_amount"));
                pendingTransactionDataArrayList.add(pendingTransactionData);
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
        setPendingTransactionDataArrayList(pendingTransactionDataArrayList);
        return pendingTransactionDataArrayList;
    }

    public void setPendingTransactionDataArrayList(ArrayList<PendingTransactionData> pendingTransactionDataArrayList) {
        this.pendingTransactionDataArrayList = pendingTransactionDataArrayList;
    }
}
