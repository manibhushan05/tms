package in.aaho.android.ownr.data;

import java.util.ArrayList;

/**
 * Created by mani on 21/7/16.
 */
public class PendingTransactionData {
    private String transactionId;
    private String pickupFrom;
    private String dropAt;
    private String shipmentDate;
    private String numberOfVehicle;
    private String material;
    private String numberOfQuotes;
    private ArrayList<PendingTransactionData> pendingTransactionDataList;

    public PendingTransactionData() {

    }

    public PendingTransactionData(String transactionId, String pickupFrom, String dropAt, String shipmentDate, String numberOfVehicle, String material, String numberOfQuotes) {
        this.transactionId = transactionId;
        this.pickupFrom = pickupFrom;
        this.dropAt = dropAt;
        this.shipmentDate = shipmentDate;
        this.numberOfVehicle = numberOfVehicle;
        this.material = material;
        this.numberOfQuotes = numberOfQuotes;
    }

    public String getTransactionId() {
        return transactionId;
    }

    public void setTransactionId(String transactionId) {
        this.transactionId = transactionId;
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

    public String getNumberOfVehicle() {
        return numberOfVehicle;
    }

    public void setNumberOfVehicle(String numberOfVehicle) {
        this.numberOfVehicle = numberOfVehicle;
    }

    public String getMaterial() {
        return material;
    }

    public void setMaterial(String material) {
        this.material = material;
    }



    public ArrayList<PendingTransactionData> getPendingTransactionDataList() {
        return pendingTransactionDataList;
    }

    public void setPendingTransactionDataList(ArrayList<PendingTransactionData> pendingTransactionDataList) {
        this.pendingTransactionDataList = pendingTransactionDataList;
    }

    public String getNumberOfQuotes() {
        return numberOfQuotes;
    }

    public void setNumberOfQuotes(String numberOfQuotes) {
        this.numberOfQuotes = numberOfQuotes;
    }
}
