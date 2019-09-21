package in.aaho.android.employee.parser;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

import in.aaho.android.employee.common.Utils;
import in.aaho.android.employee.models.OutwardPaymentData;

/**
 * Created by mani on 21/9/17.
 */

public class OutwardPaymentDataParser {
    private JSONArray jsonArray;
    private ArrayList<OutwardPaymentData> outwardPaymentDataArrayList;

    public OutwardPaymentDataParser(JSONArray jsonArray) {
        this.jsonArray = jsonArray;
    }


    public ArrayList<OutwardPaymentData> getOutwardPaymentDataArrayList() {
        outwardPaymentDataArrayList = new ArrayList<>();
        for (int i = 0; i < jsonArray.length(); i++) {
            try {
                JSONObject jsonObject = (JSONObject) jsonArray.get(i);
                OutwardPaymentData outwardPaymentData = new OutwardPaymentData();
                outwardPaymentData.setPaymentDate(jsonObject.getString("payment_date"));
                outwardPaymentData.setAmount(jsonObject.getString("actual_amount"));
                outwardPaymentData.setModeOfPayment(jsonObject.getString("payment_mode_display"));
                outwardPaymentData.setPaidTo(jsonObject.getString("paid_to"));

                if (jsonObject.has("bank_account_detail")) {
                    JSONObject bankAccDetail = jsonObject.getJSONObject("bank_account_detail");
                    Utils.get(bankAccDetail,"");
                    if (Utils.get(bankAccDetail,"account_number") != null) {
                        outwardPaymentData.setRemarks(jsonObject.getString("account_number"));
                        outwardPaymentData.setRemarksLabel("Account Number");
                    }
                }else {
                    outwardPaymentData.setRemarks(null);
                    outwardPaymentData.setRemarksLabel(null);
                }

                outwardPaymentDataArrayList.add(outwardPaymentData);

            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
        return outwardPaymentDataArrayList;
    }

    /*public ArrayList<OutwardPaymentData> getOutwardPaymentDataArrayList() {
        outwardPaymentDataArrayList = new ArrayList<>();
        for (int i = 0; i < jsonArray.length(); i++) {
            try {
                JSONObject jsonObject = (JSONObject) jsonArray.get(i);
                OutwardPaymentData paymentData = new OutwardPaymentData();
                paymentData.setPaymentDate(jsonObject.getString("date"));
                paymentData.setAmount(jsonObject.getString("amount"));
                paymentData.setModeOfPayment(jsonObject.getString("payment_mode"));
                paymentData.setReceivedFrom(jsonObject.getString("paid_to"));
                if (!jsonObject.getString("account_number").equals("null")) {
                    paymentData.setRemarks(jsonObject.getString("account_number"));
                    paymentData.setRemarksLabel("Account Number");
                } else {
                    paymentData.setRemarks(null);
                    paymentData.setRemarksLabel(null);
                }

                outwardPaymentDataArrayList.add(paymentData);

            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
        return outwardPaymentDataArrayList;
    }*/
}
