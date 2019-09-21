package in.aaho.android.customer.data;

/**
 * Created by mani on 21/7/16.
 */
public class DeliveredTransactionData {
    private String transactionId;
    private String pickupFrom;
    private String dropAt;
    private String shipmentDate;
    private String numberOfVehicle;
    private String material;
    private String totalAmount;
    private String paidAmount;
    private String balanceAmount;

    public DeliveredTransactionData() {

    }

    public DeliveredTransactionData(String transactionId, String pickupFrom, String dropAt, String shipmentDate, String numberOfVehicle, String material, String totalAmount, String paidAmount, String balanceAmount) {
        this.transactionId = transactionId;
        this.pickupFrom = pickupFrom;
        this.dropAt = dropAt;
        this.shipmentDate = shipmentDate;
        this.numberOfVehicle = numberOfVehicle;
        this.material = material;
        this.totalAmount = totalAmount;
        this.paidAmount = paidAmount;
        this.balanceAmount = balanceAmount;
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

    public String getTotalAmount() {
        return totalAmount;
    }

    public void setTotalAmount(String totalAmount) {
        this.totalAmount = totalAmount;
    }

    public String getPaidAmount() {
        return paidAmount;
    }

    public void setPaidAmount(String paidAmount) {
        this.paidAmount = paidAmount;
    }

    public String getBalanceAmount() {
        return balanceAmount;
    }

    public void setBalanceAmount(String balanceAmount) {
        this.balanceAmount = balanceAmount;
    }
}
