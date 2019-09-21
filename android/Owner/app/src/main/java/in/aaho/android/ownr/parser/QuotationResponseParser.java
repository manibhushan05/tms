package in.aaho.android.ownr.parser;

import android.util.Log;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

import in.aaho.android.ownr.data.QuotationResponseData;
import in.aaho.android.ownr.requests.Api;

/**
 * Created by mani on 19/8/16.
 */
public class QuotationResponseParser {
    private JSONArray jsonArray;
    private ArrayList<QuotationResponseData> quotationResponseDataArrayList;

    public QuotationResponseParser(JSONArray jsonArray) {
        this.jsonArray = jsonArray;
    }

    public ArrayList<QuotationResponseData> getQuotationResponseDataArrayList() {
        Log.e(Api.TAG, String.valueOf(jsonArray.length()));
        quotationResponseDataArrayList = new ArrayList<>();
        for (int i = 0; i < jsonArray.length(); i++) {
            try {
                JSONObject jsonObject = (JSONObject) jsonArray.get(i);
                QuotationResponseData quotationResponseData = new QuotationResponseData();
                quotationResponseData.setVendorName(jsonObject.getString("vendor_name"));
                quotationResponseData.setResponseId(jsonObject.getString("response_id"));
                quotationResponseData.setMessage(jsonObject.getString("text"));
                quotationResponseData.setResponseDatetime(jsonObject.getString("datetime"));
                quotationResponseDataArrayList.add(quotationResponseData);
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
        return quotationResponseDataArrayList;
    }

    public void setQuotationResponseDataArrayList(ArrayList<QuotationResponseData> quotationResponseDataArrayList) {
        this.quotationResponseDataArrayList = quotationResponseDataArrayList;
    }
}
