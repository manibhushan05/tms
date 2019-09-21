package in.aaho.android.aahocustomers.parser;

import android.util.Log;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

import in.aaho.android.aahocustomers.POD_DOCS;
import in.aaho.android.aahocustomers.data.CancelTransactionData;
import in.aaho.android.aahocustomers.data.ConfirmedTransactionData;
import in.aaho.android.aahocustomers.data.DeliveredTransactionData;
import in.aaho.android.aahocustomers.data.InTransitTransactionData;
import in.aaho.android.aahocustomers.data.PendingTransactionData;
import in.aaho.android.aahocustomers.map.TimeLocation;

/**
 * Created by mani on 11/11/16.
 */

public class BookingDataParser {
    private JSONArray jsonArray;
    private ArrayList<PendingTransactionData> pendingTransactionDataArrayList;
    private ArrayList<CancelTransactionData> cancelTransactionDataArrayList;
    private int numberOfBooking = 0;
    private int totalAmount = 0;
    private int paidAmount = 0;
    private int balanceAmount = 0;

    private static final String TAG = "BookingDataParser";
    public static final String POD_PENDING = "pending";
    public static final String POD_UNVERIFIED = "unverified";
    public static final String POD_DELIVERED = "completed";

    public BookingDataParser(JSONArray jsonArray) {
        this.jsonArray = jsonArray;
    }

    public JSONArray getJsonArray() {
        return jsonArray;
    }

    public void setJsonArray(JSONArray jsonArray) {
        this.jsonArray = jsonArray;
    }

    public ArrayList<ConfirmedTransactionData> getConfirmedTransactionDataArrayList() {

        ArrayList<ConfirmedTransactionData> confirmedTransactionDataArrayList = new ArrayList<>();
//        Log.d(TAG,"Total Array Length :"+getJsonArray().length());
        for (int i = 0; i < getJsonArray().length(); i++) {
            try {
                JSONObject value = (JSONObject) jsonArray.get(i);
                if (value.getString("status").equals("unpaid")) {
                    if (!value.getString("pod_status").equals(POD_PENDING)
                            && (!value.getString("pod_status").equals(POD_UNVERIFIED))) {
                        ConfirmedTransactionData confirmedTransactionData = new ConfirmedTransactionData();
                        TimeLocation tl = null;
                        if(value.getJSONObject("current_location").length() > 0){
                            tl = TimeLocation.fromJson(value.getJSONObject("current_location"));
                        }
                        confirmedTransactionData.setLastLocation(tl == null ? "-" : tl.text());
                        confirmedTransactionData.setBookingId(value.getString("booking_id"));
                        confirmedTransactionData.setAllocatedVehicleId(value.getString("id"));
                        confirmedTransactionData.setTransactionId(value.getString("transaction_id"));
                        confirmedTransactionData.setpickupFrom(value.getString("source_city"));
                        confirmedTransactionData.setdropAt(value.getString("destination_city"));
                        confirmedTransactionData.setShipmentDate(value.getString("shipment_date"));
                        confirmedTransactionData.setLrNumber(value.getString("lr_number"));
                        confirmedTransactionData.setMaterial(value.getString("amount"));
                        confirmedTransactionData.setTotalAmount(value.getString("amount"));
                        confirmedTransactionData.setBalance(value.getString("balance"));
                        confirmedTransactionData.setPaid(value.getString("paid"));
                        confirmedTransactionData.setVehicleNumber(value.getString("vehicle_number"));
                        confirmedTransactionData.setPodStatus(value.getString("pod_status"));
                        confirmedTransactionData.setPod_docsArrayList(
                                POD_DOCS.getListFromJsonArray(
                                        value.getJSONArray("pod_docs")));

                        confirmedTransactionDataArrayList.add(confirmedTransactionData);
                        numberOfBooking += 1;
                        totalAmount += Integer.parseInt(value.getString("amount"));
                        paidAmount += Integer.parseInt(value.getString("paid"));
                        balanceAmount += Integer.parseInt(value.getString("balance"));
                    }
                }

            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
        return confirmedTransactionDataArrayList;
    }


    public ArrayList<ConfirmedTransactionData> getPODPendingDataArrayList() {

        ArrayList<ConfirmedTransactionData> confirmedTransactionDataArrayList = new ArrayList<>();
        for (int i = 0; i < getJsonArray().length(); i++) {
            try {
                JSONObject value = (JSONObject) jsonArray.get(i);
                if (value.getString("status").equals("unpaid")) {
                    if (value.getString("pod_status").equals(POD_PENDING)
                            || value.getString("pod_status").equals(POD_UNVERIFIED)) {
                        ConfirmedTransactionData confirmedTransactionData = new ConfirmedTransactionData();
                        confirmedTransactionData.setBookingId(value.getString("booking_id"));
                        TimeLocation tl = null;
                        if(value.getJSONObject("current_location").length() > 0){
                            tl = TimeLocation.fromJson(value.getJSONObject("current_location"));
                        }
                        confirmedTransactionData.setLastLocation(tl == null ? "-" : tl.text());
                        confirmedTransactionData.setAllocatedVehicleId(value.getString("id"));
                        confirmedTransactionData.setTransactionId(value.getString("transaction_id"));
                        confirmedTransactionData.setpickupFrom(value.getString("source_city"));
                        confirmedTransactionData.setdropAt(value.getString("destination_city"));
                        confirmedTransactionData.setShipmentDate(value.getString("shipment_date"));
                        confirmedTransactionData.setLrNumber(value.getString("lr_number"));
                        confirmedTransactionData.setMaterial(value.getString("amount"));
                        confirmedTransactionData.setTotalAmount(value.getString("amount"));
                        confirmedTransactionData.setBalance(value.getString("balance"));
                        confirmedTransactionData.setPaid(value.getString("paid"));
                        confirmedTransactionData.setVehicleNumber(value.getString("vehicle_number"));
                        confirmedTransactionData.setPodStatus(value.getString("pod_status"));
                        confirmedTransactionData.setPod_docsArrayList(
                                POD_DOCS.getListFromJsonArray(
                                        value.getJSONArray("pod_docs")));

                        confirmedTransactionDataArrayList.add(confirmedTransactionData);
                        numberOfBooking += 1;
                        totalAmount += Integer.parseInt(value.getString("amount"));
                        paidAmount += Integer.parseInt(value.getString("paid"));
                        balanceAmount += Integer.parseInt(value.getString("balance"));
                    }
                }

            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
        return confirmedTransactionDataArrayList;
    }



    public ArrayList<InTransitTransactionData> getInTransitTransactionDataArrayList() {
        ArrayList<InTransitTransactionData> inTransitTransactionDataArrayList = new ArrayList<>();
        for (int i = 0; i < getJsonArray().length(); i++) {
            try {
                JSONObject value = (JSONObject) jsonArray.get(i);
                if (value.getString("status").equals("paid")) {
                    InTransitTransactionData inTransitTransactionData = new InTransitTransactionData();
                    inTransitTransactionData.setTransactionId(value.getString("id"));
                    inTransitTransactionData.setpickupFrom(value.getString("source_city"));
                    inTransitTransactionData.setdropAt(value.getString("destination_city"));
                    inTransitTransactionData.setShipmentDate(value.getString("shipment_date"));
                    inTransitTransactionData.setLrNumber(value.getString("lr_number"));
                    inTransitTransactionData.setMaterial(value.getString("amount"));
                    inTransitTransactionData.setTotalAmount(value.getString("amount"));
                    inTransitTransactionData.setBalance(value.getString("final_payment_date"));
                    inTransitTransactionData.setPaid(value.getString("paid"));
                    inTransitTransactionData.setVehicleNumber(value.getString("vehicle_number"));
                    //inTransitTransactionData.setPodStatus(value.getString("pod_status"));
                    inTransitTransactionData.setPod_docsArrayList(
                            POD_DOCS.getListFromJsonArray(
                                    value.getJSONArray("pod_docs")));

                    inTransitTransactionDataArrayList.add(inTransitTransactionData);
                    numberOfBooking += 1;
                    totalAmount += Integer.parseInt(value.getString("amount"));
                    paidAmount += Integer.parseInt(value.getString("paid"));
                    balanceAmount += Integer.parseInt(value.getString("balance"));
                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
        return inTransitTransactionDataArrayList;
    }


    public ArrayList<DeliveredTransactionData> getDeliveredTransactionDataArrayList() {
        ArrayList<DeliveredTransactionData> deliveredTransactionDataArrayList = new ArrayList<>();
        for (int i = 0; i < getJsonArray().length(); i++) {
            try {
                JSONObject value = (JSONObject) jsonArray.get(i);
                if (value.getString("status").equals("completed")) {
                    DeliveredTransactionData deliveredTransactionData = new DeliveredTransactionData();
                    deliveredTransactionData.setTransactionId(value.getString("transaction_id"));
                    deliveredTransactionData.setpickupFrom(value.getString("source_city"));
                    deliveredTransactionData.setdropAt(value.getString("destination_city"));
                    deliveredTransactionData.setShipmentDate(value.getString("shipment_date"));
                    deliveredTransactionData.setLrNumber(value.getString("lr_number"));
                    deliveredTransactionData.setMaterial(value.getString("amount"));
                    deliveredTransactionData.setTotalAmount(value.getString("amount"));
                    deliveredTransactionData.setBalanceAmount(value.getString("balance"));
                    deliveredTransactionData.setPaidAmount(value.getString("paid"));
                    deliveredTransactionData.setVehicleNumber(value.getString("vehicle_number"));
                    deliveredTransactionDataArrayList.add(deliveredTransactionData);
                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
        return deliveredTransactionDataArrayList;
    }

    public ArrayList<PendingTransactionData> getPendingTransactionDataArrayList() {
        return pendingTransactionDataArrayList;
    }

    public ArrayList<CancelTransactionData> getCancelTransactionDataArrayList() {
        return cancelTransactionDataArrayList;
    }

    public int getNumberOfBooking() {
        return numberOfBooking;
    }

    public int getTotalAmount() {
        return totalAmount;
    }

    public int getBalanceAmount() {
        return balanceAmount;
    }

    public int getPaidAmount() {
        return paidAmount;
    }
}
