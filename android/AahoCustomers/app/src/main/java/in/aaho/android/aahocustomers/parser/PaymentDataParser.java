package in.aaho.android.aahocustomers.parser;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

import in.aaho.android.aahocustomers.data.PaymentData;

/**
 * Created by mani on 21/9/17.
 */

public class PaymentDataParser {
    private JSONArray jsonArray;
    private ArrayList<PaymentData> paymentDataArrayList;

    public PaymentDataParser(JSONArray jsonArray) {
        this.jsonArray = jsonArray;
    }

    public ArrayList<PaymentData> getPaymentDataArrayList() {
        paymentDataArrayList = new ArrayList<>();
        for (int i = 0; i < jsonArray.length(); i++) {
            try {
                JSONObject jsonObject = (JSONObject) jsonArray.get(i);
                PaymentData paymentData = new PaymentData();
                paymentData.setPaymentDate(jsonObject.getString("date"));
                paymentData.setAmount(jsonObject.getString("amount"));
                paymentData.setModeOfPayment(jsonObject.getString("payment_mode"));
                paymentData.setPaidTo(jsonObject.getString("paid_to"));
                if (!jsonObject.getString("account_number").equals("null")) {
                    paymentData.setRemarks(jsonObject.getString("account_number"));
                    paymentData.setRemarksLabel("Account Number");
                } else {
                    paymentData.setRemarks(null);
                    paymentData.setRemarksLabel(null);
                }

                paymentDataArrayList.add(paymentData);

            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
        return paymentDataArrayList;
    }
}
