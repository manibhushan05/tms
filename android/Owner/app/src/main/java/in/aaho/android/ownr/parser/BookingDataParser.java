package in.aaho.android.ownr.parser;

import android.text.TextUtils;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import in.aaho.android.ownr.POD_DOCS;
import in.aaho.android.ownr.common.Utils;
import in.aaho.android.ownr.data.CancelTransactionData;
import in.aaho.android.ownr.data.ConfirmedTransactionData;
import in.aaho.android.ownr.data.DeliveredTransactionData;
import in.aaho.android.ownr.data.InTransitTransactionData;
import in.aaho.android.ownr.data.PendingTransactionData;

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

    public static final String POD_PENDING = "pending";
    public static final String POD_UNVERIFIED = "unverified";
    public static final String POD_DELIVERED = "completed";
    private List<String> pendingPODStatusList = Arrays.asList(
        "pending","unverified","rejected"
    );

    private List<String> pendingPaymentStatusList = Arrays.asList(
            "no_payment_made","partial"
    );

    private List<String> completePaymentStatusList = Arrays.asList(
            "complete","excess"
    );

    private final String KEY_ID = "id";
    private final String BOOKING_KEY_ID = "booking_id";
    private final String KEY_PAYMENT_STATUS = "outward_payment_status";
    private final String KEY_POD_STATUS = "pod_status";
    private final String KEY_FROM_CITY = "from_city";
    private final String KEY_TO_CITY = "to_city";
    private final String KEY_SHIPMENT_DATE = "shipment_date";
    private final String KEY_LR_NUMBERS = "lr_numbers";
    private final String KEY_TOTAL_AMOUNT = "amount";
    private final String KEY_BALANCE_AMOUNT = "balance_amount";
    private final String KEY_PAID_AMOUNT = "paid_amount";
    private final String KEY_LORRY_NUMBER = "lorry_number";
    private final String KEY_POD_DATA = "pod_data";
    private final String KEY_LATEST_PAYMENT_DATE = "latest_payment_date";


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
        for (int i = 0; i < getJsonArray().length(); i++) {
            try {
                JSONObject jsonObject = (JSONObject) jsonArray.get(i);
                /*if (jsonObject.getString("status").equals("unpaid")) {*/
//                if(pendingPaymentStatusList.contains(Utils.get(jsonObject,KEY_PAYMENT_STATUS))) {
                    /*if (!jsonObject.getString("pod_status").equals(POD_PENDING)
                            && (!jsonObject.getString("pod_status").equals(POD_UNVERIFIED))) {*/
                    if(!pendingPODStatusList.contains(Utils.get(jsonObject,KEY_POD_STATUS))) {
                        ConfirmedTransactionData confirmedTransactionData = new ConfirmedTransactionData();
                        confirmedTransactionData.setId(Utils.get(jsonObject,KEY_ID));
                        confirmedTransactionData.setBookingId(Utils.get(jsonObject,BOOKING_KEY_ID));
                        /*confirmedTransactionData.setAllocatedVehicleId(jsonObject.getString("id"));*/
                        confirmedTransactionData.setpickupFrom(jsonObject.getString(KEY_FROM_CITY));
                        confirmedTransactionData.setdropAt(jsonObject.getString(KEY_TO_CITY));
                        confirmedTransactionData.setShipmentDate(jsonObject.getString(KEY_SHIPMENT_DATE));

                        JSONArray jsonLRNumbers = jsonObject.getJSONArray(KEY_LR_NUMBERS);
                        String strLRList = "";
                        for (int j = 0; j < jsonLRNumbers.length() ; j++) {
                            if(TextUtils.isEmpty(strLRList)) {
                                strLRList = jsonLRNumbers.getJSONObject(j)
                                        .getString("lr_number");
                            } else {
                                strLRList = strLRList + "\n" + jsonLRNumbers.getJSONObject(j)
                                        .getString("lr_number");
                            }
                        }
                        confirmedTransactionData.setLrNumber(strLRList);
                        /*confirmedTransactionData.setLrNumber(jsonObject.getString(KEY_LR_NUMBERS));*/

                        /*confirmedTransactionData.setMaterial(jsonObject.getString("amount"));*/
                        confirmedTransactionData.setTotalAmount(jsonObject.getString(KEY_TOTAL_AMOUNT));
                        confirmedTransactionData.setBalance(jsonObject.getString(KEY_BALANCE_AMOUNT));
                        confirmedTransactionData.setPaid(jsonObject.getString(KEY_PAID_AMOUNT));
                        confirmedTransactionData.setVehicleNumber(jsonObject.getString(KEY_LORRY_NUMBER));
                        confirmedTransactionData.setPodStatus(jsonObject.getString(KEY_POD_STATUS));
                        if(jsonObject.has(KEY_POD_DATA)) {
                            confirmedTransactionData.setPod_docsArrayList(
                                    POD_DOCS.getListFromJsonArray(
                                            jsonObject.getJSONArray(KEY_POD_DATA)));
                        } else {
                            confirmedTransactionData.setPod_docsArrayList(null);
                        }

                        confirmedTransactionDataArrayList.add(confirmedTransactionData);
                        numberOfBooking += 1;
                        /*totalAmount += Integer.parseInt(jsonObject.getString("amount"));
                        paidAmount += Integer.parseInt(jsonObject.getString("paid"));
                        balanceAmount += Integer.parseInt(jsonObject.getString("balance"));*/
                    }
//                }

            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
        return confirmedTransactionDataArrayList;
    }


    public ArrayList<ConfirmedTransactionData> getPODPendingBookingDataArrayList() {

        ArrayList<ConfirmedTransactionData> podPendingBookingDataArrayList = new ArrayList<>();
        for (int i = 0; i < getJsonArray().length(); i++) {
            try {
                JSONObject jsonObject = (JSONObject) jsonArray.get(i);
                /*if (jsonObject.getString("status").equals("unpaid"))*/
//                if(pendingPaymentStatusList.contains(Utils.get(jsonObject,KEY_PAYMENT_STATUS))) {
                    /*if (jsonObject.getString("pod_status").equals(POD_PENDING)
                            || jsonObject.getString("pod_status").equals(POD_UNVERIFIED)) {*/
                    if(pendingPODStatusList.contains(Utils.get(jsonObject,KEY_POD_STATUS))) {
                        ConfirmedTransactionData podPendingBookingData = new ConfirmedTransactionData();
                        podPendingBookingData.setId(Utils.get(jsonObject,KEY_ID));
                        podPendingBookingData.setBookingId(Utils.get(jsonObject,BOOKING_KEY_ID));
                        /*podPendingBookingData.setAllocatedVehicleId(jsonObject.getString("id"));*/
                        /*podPendingBookingData.setpickupFrom(jsonObject.getString("source_city"));*/
                        podPendingBookingData.setpickupFrom(Utils.get(jsonObject,KEY_FROM_CITY));
                        /*podPendingBookingData.setdropAt(jsonObject.getString("destination_city"));*/
                        podPendingBookingData.setdropAt(Utils.get(jsonObject,KEY_TO_CITY));
                        podPendingBookingData.setShipmentDate(Utils.get(jsonObject,KEY_SHIPMENT_DATE));
                        /*podPendingBookingData.setLrNumber(jsonObject.getString("lr_number"));*/

                        JSONArray jsonLRNumbers = jsonObject.getJSONArray(KEY_LR_NUMBERS);
                        String strLRList = "";
                        for (int j = 0; j < jsonLRNumbers.length() ; j++) {
                            if(TextUtils.isEmpty(strLRList)) {
                                strLRList = jsonLRNumbers.getJSONObject(j)
                                        .getString("lr_number");
                            } else {
                                strLRList = strLRList + "\n" + jsonLRNumbers.getJSONObject(j)
                                        .getString("lr_number");
                            }
                        }

                        podPendingBookingData.setLrNumber(strLRList);
                        /*podPendingBookingData.setLrNumber(Utils.get(jsonObject,KEY_LR_NUMBERS));*/

                        /*podPendingBookingData.setMaterial(Utils.get(jsonObject,"amount"));*/
                        podPendingBookingData.setTotalAmount(Utils.get(jsonObject,KEY_TOTAL_AMOUNT));
                        podPendingBookingData.setBalance(Utils.get(jsonObject,KEY_BALANCE_AMOUNT));
                        podPendingBookingData.setPaid(Utils.get(jsonObject,KEY_PAID_AMOUNT));
                        podPendingBookingData.setVehicleNumber(Utils.get(jsonObject,KEY_LORRY_NUMBER));
                        podPendingBookingData.setPodStatus(Utils.get(jsonObject,KEY_POD_STATUS));
                        if(jsonObject.has(KEY_POD_DATA)) {
                            podPendingBookingData.setPod_docsArrayList(
                                    POD_DOCS.getListFromJsonArray(
                                            jsonObject.getJSONArray(KEY_POD_DATA)));
                        } else {
                            podPendingBookingData.setPod_docsArrayList(null);
                        }

                        numberOfBooking += 1;
                        /*totalAmount += Integer.parseInt(Utils.get(jsonObject,"amount"));*/
                        /*totalAmount += (Double.valueOf(Utils.get(jsonObject,"total_amount_to_owner"))).intValue();
                        podPendingBookingData.setTotalAmount(totalAmount+"");
                        *//*paidAmount += Integer.parseInt(Utils.get(jsonObject,"paid"));*//*
                        paidAmount += (Double.valueOf(Utils.get(jsonObject,"total_out_ward_amount")).intValue());
                        podPendingBookingData.setPaid(paidAmount+"");
                        *//*balanceAmount += Integer.parseInt(Utils.get(jsonObject,"balance"));*//*
                        balanceAmount = totalAmount - paidAmount;
                        podPendingBookingData.setBalance(balanceAmount+"");*/


                        podPendingBookingDataArrayList.add(podPendingBookingData);
                    }
                //}

            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
        return podPendingBookingDataArrayList;
    }

    public ArrayList<InTransitTransactionData> getCompleteBookingDataArrayList() {
        ArrayList<InTransitTransactionData> inTransitTransactionDataArrayList = new ArrayList<>();
        for (int i = 0; i < getJsonArray().length(); i++) {
            try {
                JSONObject jsonObject = (JSONObject) jsonArray.get(i);
                /*if (jsonObject.getString("status").equals("paid")) {*/
//                if(completePaymentStatusList.contains(Utils.get(jsonObject,KEY_PAYMENT_STATUS))) {
                    InTransitTransactionData inTransitTransactionData = new InTransitTransactionData();
                    inTransitTransactionData.setId(Utils.get(jsonObject,KEY_ID));
                    inTransitTransactionData.setBookingId(Utils.get(jsonObject,BOOKING_KEY_ID));
                    inTransitTransactionData.setpickupFrom(Utils.get(jsonObject,KEY_FROM_CITY));
                    inTransitTransactionData.setdropAt(Utils.get(jsonObject,KEY_TO_CITY));
                    inTransitTransactionData.setShipmentDate(Utils.get(jsonObject,KEY_SHIPMENT_DATE));

                    JSONArray jsonLRNumbers = jsonObject.getJSONArray(KEY_LR_NUMBERS);
                    String strLRList = "";
                    for (int j = 0; j < jsonLRNumbers.length() ; j++) {
                        if(TextUtils.isEmpty(strLRList)) {
                            strLRList = jsonLRNumbers.getJSONObject(j)
                                    .getString("lr_number");
                        } else {
                            strLRList = strLRList + "\n" + jsonLRNumbers.getJSONObject(j)
                                    .getString("lr_number");
                        }
                    }
                    inTransitTransactionData.setLrNumber(strLRList);
                    /*inTransitTransactionData.setLrNumber(Utils.get(jsonObject,KEY_LR_NUMBERS));*/

                    /*inTransitTransactionData.setMaterial(Utils.get(jsonObject,KEY_TOTAL_AMOUNT));*/
                    inTransitTransactionData.setTotalAmount(Utils.get(jsonObject,KEY_TOTAL_AMOUNT));
                    inTransitTransactionData.setBalance(Utils.get(jsonObject,KEY_BALANCE_AMOUNT));
                    inTransitTransactionData.setPaid(Utils.get(jsonObject,KEY_PAID_AMOUNT));
                    inTransitTransactionData.setVehicleNumber(Utils.get(jsonObject,KEY_LORRY_NUMBER));
                    inTransitTransactionData.setLatestPaymentDate(Utils.get(jsonObject,KEY_LATEST_PAYMENT_DATE));
                    //inTransitTransactionData.setPodStatus(jsonObject.getString("pod_status"));
                    /*inTransitTransactionData.setPod_docsArrayList(
                            POD_DOCS.getListFromJsonArray(
                                    jsonObject.getJSONArray("pod_docs")));*/

                    if(jsonObject.has(KEY_POD_DATA)) {
                        inTransitTransactionData.setPod_docsArrayList(
                                POD_DOCS.getListFromJsonArray(
                                        jsonObject.getJSONArray(KEY_POD_DATA)));
                    } else {
                        inTransitTransactionData.setPod_docsArrayList(null);
                    }

                    inTransitTransactionDataArrayList.add(inTransitTransactionData);
                    numberOfBooking += 1;
                    /*totalAmount += Integer.parseInt(jsonObject.getString("amount"));
                    paidAmount += Integer.parseInt(jsonObject.getString("paid"));
                    balanceAmount += Integer.parseInt(jsonObject.getString("balance"));*/
//                }
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
