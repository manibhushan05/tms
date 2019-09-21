package in.aaho.android.ownr.parser;

import android.util.Log;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

import in.aaho.android.ownr.data.QuotationsData;
import in.aaho.android.ownr.requests.Api;

/**
 * Created by mani on 18/8/16.
 */
public class QuotationParser {
    private JSONArray jsonArray;
    private ArrayList<QuotationsData> quotationsDataArrayList;

    public QuotationParser(JSONArray jsonArray) {
        this.jsonArray = jsonArray;
    }

    public ArrayList<QuotationsData> getQuotationsDataArrayList() {
        Log.e(Api.TAG, String.valueOf(jsonArray.length()));
        quotationsDataArrayList = new ArrayList<>();
        for (int i=0;i<jsonArray.length();i++){
            try {
                JSONObject jsonObject =(JSONObject) jsonArray.get(i);
                QuotationsData quotationsData = new QuotationsData();
                quotationsData.setPickUpFrom(jsonObject.getString("source_city"));
                quotationsData.setDropAt(jsonObject.getString("destination_city"));
                quotationsData.setTransactionId(jsonObject.getString("transaction_id"));
                quotationsData.setShipmentDate(jsonObject.getString("shipment_date"));
                quotationsData.setNumberOfTruck(jsonObject.getString("total_vehicle_requested"));
                quotationsData.setNumberOfQuote(jsonObject.getString("number_of_quotes"));
                quotationsDataArrayList.add(quotationsData);
            } catch (JSONException e) {
                e.printStackTrace();
            }

        }

        return quotationsDataArrayList;
    }

    public void setQuotationsDataArrayList(ArrayList<QuotationsData> quotationsDataArrayList) {
        this.quotationsDataArrayList = quotationsDataArrayList;
    }
}
