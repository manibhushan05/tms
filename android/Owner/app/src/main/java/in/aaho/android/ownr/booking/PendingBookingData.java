package in.aaho.android.ownr.booking;

/**
 * Created by mani on 19/9/17.
 */

public class PendingBookingData {
    private String bookingID;
    private String pickupFrom;
    private String dropAt;
    private String shipmentDate;
    private String lrNumber;
    private String totalAmount;
    private String balance;
    private String paid;
    private String vehicleNumber;

    public PendingBookingData(String bookingID, String pickupFrom, String dropAt, String shipmentDate, String lrNumber, String totalAmount, String balance, String paid, String vehicleNumber) {
        this.bookingID = bookingID;
        this.pickupFrom = pickupFrom;
        this.dropAt = dropAt;
        this.shipmentDate = shipmentDate;
        this.lrNumber = lrNumber;
        this.totalAmount = totalAmount;
        this.balance = balance;
        this.paid = paid;
        this.vehicleNumber = vehicleNumber;
    }

    public String getBookingID() {
        return bookingID;
    }

    public void setBookingID(String bookingID) {
        this.bookingID = bookingID;
    }

    public String getPickupFrom() {
        return pickupFrom;
    }

    public void setPickupFrom(String pickupFrom) {
        this.pickupFrom = pickupFrom;
    }

    public String getDropAt() {
        return dropAt;
    }

    public void setDropAt(String dropAt) {
        this.dropAt = dropAt;
    }

    public String getShipmentDate() {
        return shipmentDate;
    }

    public void setShipmentDate(String shipmentDate) {
        this.shipmentDate = shipmentDate;
    }

    public String getLrNumber() {
        return lrNumber;
    }

    public void setLrNumber(String lrNumber) {
        this.lrNumber = lrNumber;
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
}
