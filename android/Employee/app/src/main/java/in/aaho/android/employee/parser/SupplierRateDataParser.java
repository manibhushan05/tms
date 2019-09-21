package in.aaho.android.employee.parser;

import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

import in.aaho.android.employee.common.Utils;
import in.aaho.android.employee.models.BookingDetailsRateData;

import static in.aaho.android.employee.common.Utils.round;

/**
 * Created by mani on 16/12/16.
 */

public class SupplierRateDataParser {
    private JSONObject jsonObject;
    private ArrayList<BookingDetailsRateData> bookingDetailsRateDataArrayList;


    public SupplierRateDataParser(JSONObject jsonObject) {
        this.jsonObject = jsonObject;
    }

    public ArrayList<BookingDetailsRateData> getBookingDetailsRateDataArrayList() {
        double supplier_weight = 0,supplier_rate = 0;
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
                {"total_amount_to_owner", "Total Amount"},
        };

        bookingDetailsRateDataArrayList = new ArrayList<>();
        try {
            int count = 0;
            for (String[] anArr : arr) {
                if (Utils.get(jsonObject,anArr[0]) != null) {
                    if(!Utils.get(jsonObject,anArr[0]).equals("0")) {
                        double value = round(Double.valueOf(Utils.get(jsonObject, anArr[0])), 2);
                        if ((anArr[0]).equals("supplier_charged_weight")) {
                            supplier_weight = value;
                        }
                        if ((anArr[0]).equals("supplier_rate")) {
                            supplier_rate = value;
                        }

                        BookingDetailsRateData bookingDetailsRateData = new BookingDetailsRateData();
                        bookingDetailsRateData.setRateLabel(anArr[1]);
                        bookingDetailsRateData.setRateValue(value + "");
                        bookingDetailsRateDataArrayList.add(bookingDetailsRateData);

                        // Below logic is to calculate freight at APP site
                        if (count == 1) {
                            bookingDetailsRateData = new BookingDetailsRateData();
                            bookingDetailsRateData.setRateLabel("Freight");
                            double freight = round(supplier_weight * supplier_rate, 2);
                            if (freight != 0) {
                                bookingDetailsRateData.setRateValue(freight + "");
                                bookingDetailsRateDataArrayList.add(bookingDetailsRateData);
                            }
                        }
                    }
                }
                count++;
            }


        } catch (JSONException e) {
            e.printStackTrace();
        }
        return bookingDetailsRateDataArrayList;
    }

    /*public ArrayList<BookingDetailsRateData> getBookingDetailsRateDataArrayList() {
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

        bookingDetailsRateDataArrayList = new ArrayList<>();
        try {
            for (String[] anArr : arr) {
                if (!jsonObject.getString(anArr[0]).equals("0")) {
                    BookingDetailsRateData tripDetailsPaymentData = new BookingDetailsRateData();
                    tripDetailsPaymentData.setRateLabel(anArr[1]);
                    tripDetailsPaymentData.setRateValue(jsonObject.getString(anArr[0]));
                    bookingDetailsRateDataArrayList.add(tripDetailsPaymentData);
                }
            }
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return bookingDetailsRateDataArrayList;
    }*/

}
