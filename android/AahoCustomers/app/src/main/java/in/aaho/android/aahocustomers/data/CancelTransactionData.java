package in.aaho.android.aahocustomers.data;

/**
 * Created by mani on 21/7/16.
 */
public class CancelTransactionData {
    private String transactionId;
    private String pickupFrom;
    private String dropAt;
    private String shipmentDate;
    private String numberOfVehicle;
    private String material;
    private String quoteAmount;
    private String cancellationDate;

    public CancelTransactionData() {

    }

    public CancelTransactionData(String transactionId, String pickupFrom, String dropAt, String shipmentDate, String numberOfVehicle, String material, String quoteAmount, String cancellationDate) {
        this.transactionId = transactionId;
        this.pickupFrom = pickupFrom;
        this.dropAt = dropAt;
        this.shipmentDate = shipmentDate;
        this.numberOfVehicle = numberOfVehicle;
        this.material = material;
        this.quoteAmount = quoteAmount;
        this.cancellationDate = cancellationDate;
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

    public String getQuoteAmount() {
        return quoteAmount;
    }

    public void setQuoteAmount(String quoteAmount) {
        this.quoteAmount = quoteAmount;
    }

    public String getCancellationDate() {
        return cancellationDate;
    }

    public void setCancellationDate(String cancellationDate) {
        this.cancellationDate = cancellationDate;
    }
}
