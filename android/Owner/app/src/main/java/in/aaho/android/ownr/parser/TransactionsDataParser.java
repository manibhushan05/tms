package in.aaho.android.ownr.parser;

import android.util.Log;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

import in.aaho.android.ownr.data.CancelTransactionData;
import in.aaho.android.ownr.data.ConfirmedTransactionData;
import in.aaho.android.ownr.data.DeliveredTransactionData;
import in.aaho.android.ownr.data.InTransitTransactionData;
import in.aaho.android.ownr.data.PendingTransactionData;
import in.aaho.android.ownr.requests.Api;

/**
 * Created by mani on 1/8/16.
 */
public class TransactionsDataParser {
    private JSONObject jsonObject;
    private JSONArray jsonArrayTransactionData;
    private JSONArray jsonArrayPending;
    private JSONArray jsonArrayConfirm;
    private JSONArray jsonArrayInTransit;
    private JSONArray jsonArrayDelivered;
    private JSONArray jsonArrayCancelled;
    private ArrayList<PendingTransactionData> pendingTransactionDataArrayList;
    private ArrayList<ConfirmedTransactionData> confirmedTransactionDataArrayList;
    private ArrayList<InTransitTransactionData> inTransitTransactionDataArrayList;
    private ArrayList<DeliveredTransactionData> deliveredTransactionDataArrayList;
    private ArrayList<CancelTransactionData> cancelTransactionDataArrayList;

    public TransactionsDataParser() {
    }

    public TransactionsDataParser(JSONObject jsonObject) {
        this.jsonObject = jsonObject;
        try {
            setJsonArrayPending(this.jsonObject.getJSONArray("pending"));
            setJsonArrayConfirm(this.jsonObject.getJSONArray("confirmed"));
            setJsonArrayInTransit(this.jsonObject.getJSONArray("in_transit"));
            setJsonArrayDelivered(this.jsonObject.getJSONArray("delivered"));
            setJsonArrayCancelled(this.jsonObject.getJSONArray("cancelled"));
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    public void setJsonObject(JSONObject jsonObject) {
        this.jsonObject = jsonObject;
    }

    public JSONObject getJsonObject() {
        return jsonObject;
    }

    public void setJsonArrayConfirm(JSONArray jsonArrayConfirm) {
        this.jsonArrayConfirm = jsonArrayConfirm;
    }

    public void setJsonArrayInTransit(JSONArray jsonArrayInTransit) {
        this.jsonArrayInTransit = jsonArrayInTransit;
    }

    public void setJsonArrayDelivered(JSONArray jsonArrayDelivered) {
        this.jsonArrayDelivered = jsonArrayDelivered;
    }

    public JSONArray getJsonArrayConfirm() {
        return jsonArrayConfirm;
    }

    public JSONArray getJsonArrayInTransit() {
        return jsonArrayInTransit;
    }

    public JSONArray getJsonArrayDelivered() {
        return jsonArrayDelivered;
    }

    public JSONArray getJsonArrayCancelled() {
        return jsonArrayCancelled;
    }

    public void setJsonArrayCancelled(JSONArray jsonArrayCancelled) {
        this.jsonArrayCancelled = jsonArrayCancelled;
    }

    public ArrayList<PendingTransactionData> getPendingTransactionDataArrayList() {
        pendingTransactionDataArrayList = new ArrayList<>();
        for (int i = 0; i < getJsonArrayPending().length(); i++) {
            try {
                JSONObject value = (JSONObject) jsonArrayPending.get(i);
                PendingTransactionData pendingTransactionData = new PendingTransactionData();
                pendingTransactionData.setTransactionId(value.getString("transaction_id"));
                pendingTransactionData.setpickupFrom(value.getString("source_city"));
                pendingTransactionData.setdropAt(value.getString("destination_city"));
                pendingTransactionData.setShipmentDate(value.getString("shipment_date"));
                pendingTransactionData.setNumberOfVehicle(value.getString("total_vehicle_requested"));
                pendingTransactionData.setMaterial(value.getString("amount"));
                pendingTransactionData.setNumberOfQuotes(value.getString("number_of_quotes"));
                pendingTransactionDataArrayList.add(pendingTransactionData);
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
        return pendingTransactionDataArrayList;
    }

    public void setPendingTransactionDataArrayList(ArrayList<PendingTransactionData> pendingTransactionDataArrayList) {
        this.pendingTransactionDataArrayList = pendingTransactionDataArrayList;
    }

    public JSONArray getJsonArrayPending() {
        return jsonArrayPending;
    }

    public void setJsonArrayPending(JSONArray jsonArrayPending) {
        this.jsonArrayPending = jsonArrayPending;
    }

    public ArrayList<ConfirmedTransactionData> getConfirmedTransactionDataArrayList() {
        confirmedTransactionDataArrayList = new ArrayList<>();
        for (int i = 0; i < getJsonArrayConfirm().length(); i++) {
            try {
                JSONObject value = (JSONObject) jsonArrayConfirm.get(i);
                ConfirmedTransactionData confirmedTransactionData = new ConfirmedTransactionData();
                confirmedTransactionData.setAllocatedVehicleId(value.getString("id"));
                Log.e(Api.TAG,value.getString("id"));
                confirmedTransactionData.setBookingId(value.getString("booking_id"));
                confirmedTransactionData.setpickupFrom(value.getString("source_city"));
                confirmedTransactionData.setdropAt(value.getString("destination_city"));
                confirmedTransactionData.setShipmentDate(value.getString("shipment_date"));
                confirmedTransactionData.setLrNumber(value.getString("total_vehicle_requested"));
                confirmedTransactionData.setMaterial(value.getString("amount"));
                confirmedTransactionData.setTotalAmount(value.getString("amount"));
                confirmedTransactionDataArrayList.add(confirmedTransactionData);
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
        return confirmedTransactionDataArrayList;
    }

    public void setConfirmedTransactionDataArrayList(ArrayList<ConfirmedTransactionData> confirmedTransactionDataArrayList) {
        this.confirmedTransactionDataArrayList = confirmedTransactionDataArrayList;
    }

    public ArrayList<InTransitTransactionData> getInTransitTransactionDataArrayList() {
        inTransitTransactionDataArrayList = new ArrayList<>();
        for (int i = 0; i < getJsonArrayInTransit().length(); i++) {
            try {
                JSONObject value = (JSONObject) jsonArrayInTransit.get(i);
                InTransitTransactionData inTransitTransactionData = new InTransitTransactionData();
                inTransitTransactionData.setBookingId(value.getString("transaction_id"));
                inTransitTransactionData.setpickupFrom(value.getString("source_city"));
                inTransitTransactionData.setdropAt(value.getString("destination_city"));
                inTransitTransactionData.setShipmentDate(value.getString("shipment_date"));
                inTransitTransactionData.setLrNumber(value.getString("total_vehicle_requested"));
                inTransitTransactionData.setMaterial(value.getString("amount"));
                inTransitTransactionData.setTotalAmount(value.getString("amount"));
                inTransitTransactionDataArrayList.add(inTransitTransactionData);
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
        return inTransitTransactionDataArrayList;
    }

    public void setInTransitTransactionDataArrayList(ArrayList<InTransitTransactionData> inTransitTransactionDataArrayList) {
        this.inTransitTransactionDataArrayList = inTransitTransactionDataArrayList;
    }

    public ArrayList<DeliveredTransactionData> getDeliveredTransactionDataArrayList() {
        deliveredTransactionDataArrayList = new ArrayList<>();
        for (int i = 0; i < getJsonArrayDelivered().length(); i++) {
            try {
                JSONObject value = (JSONObject) jsonArrayDelivered.get(i);
                DeliveredTransactionData deliveredTransactionData = new DeliveredTransactionData();
                deliveredTransactionData.setTransactionId(value.getString("transaction_id"));
                deliveredTransactionData.setpickupFrom(value.getString("source_city"));
                deliveredTransactionData.setdropAt(value.getString("destination_city"));
                deliveredTransactionData.setShipmentDate(value.getString("shipment_date"));
                deliveredTransactionData.setLrNumber(value.getString("total_vehicle_requested"));
                deliveredTransactionData.setMaterial(value.getString("amount"));
                deliveredTransactionData.setTotalAmount(value.getString("amount"));
                deliveredTransactionData.setBalanceAmount(value.getString("balance"));
                deliveredTransactionData.setPaidAmount(value.getString("paid"));
                deliveredTransactionDataArrayList.add(deliveredTransactionData);
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
        return deliveredTransactionDataArrayList;
    }

    public void setDeliveredTransactionDataArrayList(ArrayList<DeliveredTransactionData> deliveredTransactionDataArrayList) {
        this.deliveredTransactionDataArrayList = deliveredTransactionDataArrayList;
    }

    public ArrayList<CancelTransactionData> getCancelTransactionDataArrayList() {
        cancelTransactionDataArrayList = new ArrayList<>();
        for (int i = 0; i < getJsonArrayCancelled().length(); i++) {
            try {
                JSONObject value = (JSONObject) jsonArrayCancelled.get(i);
                CancelTransactionData cancelTransactionData = new CancelTransactionData();
                cancelTransactionData.setTransactionId(value.getString("transaction_id"));
                cancelTransactionData.setpickupFrom(value.getString("source_city"));
                cancelTransactionData.setdropAt(value.getString("destination_city"));
                cancelTransactionData.setShipmentDate(value.getString("shipment_date"));
                cancelTransactionData.setNumberOfVehicle(value.getString("total_vehicle_requested"));
                cancelTransactionData.setMaterial(value.getString("amount"));
                cancelTransactionData.setQuoteAmount(value.getString("amount"));
                cancelTransactionData.setCancellationDate(value.getString("cancellation_date"));
                cancelTransactionDataArrayList.add(cancelTransactionData);
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
        return cancelTransactionDataArrayList;
    }

    public void setCancelTransactionDataArrayList(ArrayList<CancelTransactionData> cancelTransactionDataArrayList) {
        this.cancelTransactionDataArrayList = cancelTransactionDataArrayList;
    }
}
