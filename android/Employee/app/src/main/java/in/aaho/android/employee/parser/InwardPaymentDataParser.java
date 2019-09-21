package in.aaho.android.employee.parser;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

import in.aaho.android.employee.common.Utils;
import in.aaho.android.employee.models.InwardPaymentData;
import in.aaho.android.employee.models.OutwardPaymentData;

/**
 * Created by Suraj.M
 */
public class InwardPaymentDataParser {
    private JSONArray jsonArray;
    private ArrayList<InwardPaymentData> outwardPaymentDataArrayList;

    public InwardPaymentDataParser(JSONArray jsonArray) {
        this.jsonArray = jsonArray;
    }

    public ArrayList<InwardPaymentData> getInwardPaymentDataArrayList() {
        outwardPaymentDataArrayList = new ArrayList<>();
        for (int i = 0; i < jsonArray.length(); i++) {
            try {
                JSONObject jsonObject = (JSONObject) jsonArray.get(i);
                InwardPaymentData inwardPaymentData = new InwardPaymentData();
                inwardPaymentData.setReceivedFrom(jsonObject.getString("received_from"));
                inwardPaymentData.setPaymentDate(jsonObject.getString("payment_date"));
                inwardPaymentData.setModeOfPayment(jsonObject.getString("payment_mode"));
                inwardPaymentData.setAmount(jsonObject.getString("actual_amount"));
                inwardPaymentData.setTds(jsonObject.getString("tds"));

                outwardPaymentDataArrayList.add(inwardPaymentData);

            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
        return outwardPaymentDataArrayList;
    }
}