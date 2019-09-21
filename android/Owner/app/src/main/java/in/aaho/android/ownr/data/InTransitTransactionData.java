package in.aaho.android.ownr.data;

import java.util.ArrayList;

import in.aaho.android.ownr.POD_DOCS;

/**
 * Created by mani on 21/7/16.
 */
public class InTransitTransactionData {
    private String id;
    private String bookingId;
    private String pickupFrom;
    private String dropAt;
    private String shipmentDate;
    private String lrNumber;
    private String material;
    private String totalAmount;
    private String balance;
    private String paid;
    private String vehicleNumber;
    private String latestPaymentDate;
    private ArrayList<POD_DOCS> pod_docsArrayList;

    public InTransitTransactionData() {

    }

    public InTransitTransactionData(String bookingId, String pickupFrom, String dropAt, String shipmentDate, String lrNumber,
                                    String material, String totalAmount, String balance,
                                    String paid, String vehicleNumber,String latestPaymentDate) {
        this.bookingId = bookingId;
        this.pickupFrom = pickupFrom;
        this.dropAt = dropAt;
        this.shipmentDate = shipmentDate;
        this.lrNumber = lrNumber;
        this.material = material;
        this.totalAmount = totalAmount;
        this.balance = balance;
        this.paid = paid;
        this.vehicleNumber = vehicleNumber;
        this.latestPaymentDate = latestPaymentDate;
    }

    public String getBookingId() {
        return bookingId;
    }

    public void setBookingId(String transactionId) {
        this.bookingId = transactionId;
    }

    public String getpickupFrom() {
        return pickupFrom;
    }

    public void setpickupFrom(String pickupFrom) {
        this.pickupFrom = pickupFrom;
    }

    public String getdropAt() {
        return dropAt;
    }

    public void setdropAt(String dropAt) {
        this.dropAt = dropAt;
    }

    public String getShipmentDate() {
        return shipmentDate;
    }

    public void setShipmentDate(String shipmentDate) {
        this.shipmentDate = shipmentDate;
    }


    public String getMaterial() {
        return material;
    }

    public void setMaterial(String material) {
        this.material = material;
    }

    public String getTotalAmount() {
        return totalAmount;
    }

    public void setTotalAmount(String totalAmount) {
        this.totalAmount = totalAmount;
    }

    public String getBalance() {
        return balance;
    }

    public void setBalance(String balance) {
        this.balance = balance;
    }

    public String getPaid() {
        return paid;
    }

    public void setPaid(String paid) {
        this.paid = paid;
    }

    public String getVehicleNumber() {
        return vehicleNumber;
    }

    public void setVehicleNumber(String vehicleNumber) {
        this.vehicleNumber = vehicleNumber;
    }

    public String getLrNumber() {
        return lrNumber;
    }

    public void setLrNumber(String lrNumber) {
        this.lrNumber = lrNumber;
    }

    public String getLatestPaymentDate() {
        return latestPaymentDate;
    }

    public void setLatestPaymentDate(String latestPaymentDate) {
        this.latestPaymentDate = latestPaymentDate;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    // Added by Suraj M

    public ArrayList<POD_DOCS> getPod_docsArrayList() {
        return pod_docsArrayList;
    }

    public void setPod_docsArrayList(ArrayList<POD_DOCS> pod_docsArrayList) {
        this.pod_docsArrayList = pod_docsArrayList;
    }
}
