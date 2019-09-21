package in.aaho.android.ownr.parser;

import android.text.TextUtils;
import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Iterator;

import in.aaho.android.ownr.common.Utils;
import in.aaho.android.ownr.data.TripDetailsPaymentData;

import static in.aaho.android.ownr.common.Utils.get;
import static in.aaho.android.ownr.common.Utils.round;

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
        double supplier_weight = 0, supplier_rate = 0;
        Log.e("DATA", String.valueOf(jsonObject));
        String[][] arr = {
                {"supplier_charged_weight", "Weight"},
                {"supplier_rate", "Rate"},
                /*{"freight", "Freight"},*/ // As discussed this is now calculated at app side
                {"loading_charge", "(+)Loading Charge"},
                {"unloading_charge", "(+)Unloading Charge"},
                {"detention_charge", "(+)Detention"},
                {"additional_charges_for_owner", "(+)Additional Charge"},
                {"commission", "(-)Commission"},
                {"lr_cost", "(-)LR Charge"},
                {"deduction_for_advance", "(-)Deduction for Advance"},
                {"deduction_for_balance", "(-)Deduction for Balance"},
                {"other_deduction", "Other Deduction"},
                {"remarks_about_deduction", "Deduction Remarks"},
                {"total_amount_to_owner", "Total Amount"},
        };

        tripDetailsPaymentDataArrayList = new ArrayList<>();
        try {
            int count = 0;
            for (String[] anArr : arr) {
                if (Utils.get(jsonObject, anArr[0]) != null) {
                    if (!Utils.get(jsonObject, anArr[0]).equals("0")) {
                        String displayValue = "";
                        if (count == 11) {
                            displayValue = Utils.get(jsonObject, anArr[0]);
                            if (TextUtils.isEmpty(displayValue)) {
                                displayValue = "-";
                            }
                        } else {
                            double value = round(Double.valueOf(Utils.get(jsonObject, anArr[0])), 2);
                            if ((anArr[0]).equals("supplier_charged_weight")) {
                                supplier_weight = value;
                            }
                            if ((anArr[0]).equals("supplier_rate")) {
                                supplier_rate = value;
                            }
                            displayValue = String.valueOf(value);
                        }

                        TripDetailsPaymentData tripDetailsPaymentData = new TripDetailsPaymentData();
                        if(count != 11) {
                            tripDetailsPaymentData.setRateLabel(anArr[1]);
                            tripDetailsPaymentData.setRateValue(displayValue + "");
                            tripDetailsPaymentDataArrayList.add(tripDetailsPaymentData);
                        } else if(count == 11 && !displayValue.equalsIgnoreCase("-")) {
                            tripDetailsPaymentData.setRateLabel(anArr[1]);
                            tripDetailsPaymentData.setRateValue(displayValue + "");
                            tripDetailsPaymentDataArrayList.add(tripDetailsPaymentData);
                        }

                        // Below logic is to calculate freight at APP site
                        if (count == 1) {
                            tripDetailsPaymentData = new TripDetailsPaymentData();
                            tripDetailsPaymentData.setRateLabel("Freight");
                            double freight = round(supplier_weight * supplier_rate, 2);
                            if (freight != 0) {
                                tripDetailsPaymentData.setRateValue(freight + "");
                                tripDetailsPaymentDataArrayList.add(tripDetailsPaymentData);
                            }
                        }
                    }
                }
                count++;
            }


        } catch (JSONException e) {
            e.printStackTrace();
        }
        return tripDetailsPaymentDataArrayList;
    }

    /*public ArrayList<TripDetailsPaymentData> getTripDetailsPaymentDataArrayList() {
        Log.e("DATA", String.valueOf(jsonObject));
        String[][] arr = {
                {"weight", "Weight"},
                {"rate", "Rate"},
                {"freight", "Freight"},
                {"loading", "(+)Loading Charge"},
                {"unloading", "(+)Unloading Charge"},
                {"detention", "(+)Detention"},
                {"additional", "(+)Additional Charge"},
                {"commission", "(-)Commission"},
                {"lr_charge", "(-)LR Charge"},
                {"deduction_for_advance", "(-)Deduction for Advance"},
                {"deduction_for_balance", "(-)Deduction for Balance"},
                {"other_deduction", "Other Deduction"},
                {"total_amount_to_owner", "Total Amount"},
        };

        tripDetailsPaymentDataArrayList = new ArrayList<>();
        try {
            for (String[] anArr : arr) {
                if (!jsonObject.getString(anArr[0]).equals("0")) {
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
    }*/

}
