package in.aaho.android.aahocustomers.parser;

import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

import in.aaho.android.aahocustomers.data.TripDetailsPaymentData;

/**
 * Created by mani on 16/12/16.
 */

public class TripDetailsPaymentParser {
    private JSONObject jsonObject;
    private ArrayList<TripDetailsPaymentData> tripDetailsPaymentDataArrayList;


    public TripDetailsPaymentParser(JSONObject jsonObject) {
        this.jsonObject = jsonObject;
    }

    public ArrayList<TripDetailsPaymentData> getTripDetailsPaymentDataArrayList() {
        Log.e("DATA", String.valueOf(jsonObject));
        String[][] arr = {
                {"weight", "Weight"},
                {"rate", "Rate"},
//                {"freight", "Freight"},
//                {"loading", "(+)Loading Charge"},
//                {"unloading", "(+)Unloading Charge"},
//                {"detention", "(+)Detention"},
                {"additional", "(+)Additional Charge"},
                {"company_remarks", "Charge Remarks"},
                {"deductions_for_company", "(-)Deduction"},
                {"deduction_remarks_company", "Deduction Remarks"},
//                {"commission", "(-)Commission"},
//                {"lr_charge", "(-)LR Charge"},
//                {"deduction_for_advance", "(-)Deduction for Advance"},
//                {"deduction_for_balance", "(-)Deduction for Balance"},
//                {"other_deduction", "Other Deduction"},
                {"total_amount_to_company", "Total Amount"},
        };

        tripDetailsPaymentDataArrayList = new ArrayList<>();
        try {
            for (String[] anArr : arr) {
                if (!jsonObject.getString(anArr[0]).equals("0") && !jsonObject.getString(anArr[0]).equals("null") &&
                        !jsonObject.getString(anArr[0]).equals("")) {
                    TripDetailsPaymentData tripDetailsPaymentData = new TripDetailsPaymentData();
                    tripDetailsPaymentData.setRateLabel(anArr[1]);
                    tripDetailsPaymentData.setRateValue(jsonObject.getString(anArr[0]));
                    tripDetailsPaymentDataArrayList.add(tripDetailsPaymentData);
                }
            }
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return tripDetailsPaymentDataArrayList;
    }

}
