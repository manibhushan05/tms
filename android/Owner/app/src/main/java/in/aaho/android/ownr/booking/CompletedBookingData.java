package in.aaho.android.ownr.booking;

/**
 * Created by mani on 19/9/17.
 */

public class CompletedBookingData {
    private String bookingId;
    private String pickupFrom;
    private String dropAt;
    private String shipmentDate;
    private String lrNumber;
    private String totalAmount;
    private String vehicleNumber;
    private String lastPaymentDate;

    public CompletedBookingData(String bookingId, String pickupFrom, String dropAt, String shipmentDate, String lrNumber, String totalAmount, String vehicleNumber, String lastPaymentDate) {
        this.bookingId = bookingId;
        this.pickupFrom = pickupFrom;
        this.dropAt = dropAt;
        this.shipmentDate = shipmentDate;
        this.lrNumber = lrNumber;
        this.totalAmount = totalAmount;
        this.vehicleNumber = vehicleNumber;
        this.lastPaymentDate = lastPaymentDate;
    }

    public CompletedBookingData() {
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

    public String getVehicleNumber() {
        return vehicleNumber;
    }

    public void setVehicleNumber(String vehicleNumber) {
        this.vehicleNumber = vehicleNumber;
    }

    public String getLastPaymentDate() {
        return lastPaymentDate;
    }

    public void setLastPaymentDate(String lastPaymentDate) {
        this.lastPaymentDate = lastPaymentDate;
    }

    public String getBookingId() {
        return bookingId;
    }

    public void setBookingId(String bookingId) {
        this.bookingId = bookingId;
    }
}
