package in.aaho.android.ownr.parser;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

import in.aaho.android.ownr.common.Utils;
import in.aaho.android.ownr.data.PaymentData;

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
                paymentData.setPaymentDate(jsonObject.getString("payment_date"));
                paymentData.setAmount(jsonObject.getString("actual_amount"));
                paymentData.setModeOfPayment(jsonObject.getString("payment_mode_display"));
                paymentData.setPaidTo(jsonObject.getString("paid_to"));

                if (jsonObject.has("bank_account_detail")) {
                    JSONObject bankAccDetail = jsonObject.getJSONObject("bank_account_detail");
                    Utils.get(bankAccDetail,"");
                    if (Utils.get(bankAccDetail,"account_number") != null) {
                        paymentData.setRemarks(bankAccDetail.getString("account_number"));
                        paymentData.setRemarksLabel("Account Number");
                    }
                }else {
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

    /*public ArrayList<PaymentData> getPaymentDataArrayList() {
        paymentDataArrayList = new ArrayList<>();
        for (int i = 0; i < jsonArray.length(); i++) {
            try {
                JSONObject jsonObject = (JSONObject) jsonArray.get(i);
                PaymentData paymentData = new PaymentData();
                paymentData.setDate(jsonObject.getString("date"));
                paymentData.setAmount(jsonObject.getString("amount"));
                paymentData.setStatus(jsonObject.getString("payment_mode"));
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
    }*/
}
