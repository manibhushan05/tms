package in.aaho.android.customer.data;

/**
 * Created by mani on 22/7/16.
 */
public class TrackingDataList {
    private String transactionId;
    private String status;
    private String pickupFrom;
    private String dropAt;
    private String startedOn;
    private String lastKnownLocation;
    private String currentDateTime;

    public TrackingDataList(String transactionId, String status, String pickupFrom, String dropAt, String startedOn, String lastKnownLocation, String currentDateTime) {
        this.transactionId = transactionId;
        this.status = status;
        this.pickupFrom = pickupFrom;
        this.dropAt = dropAt;
        this.startedOn = startedOn;
        this.lastKnownLocation = lastKnownLocation;
        this.currentDateTime = currentDateTime;
    }

    public String getTransactionId() {
        return transactionId;
    }

    public void setTransactionId(String transactionId) {
        this.transactionId = transactionId;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getPickupFrom() {
        return pickupFrom;
    }

    public void setPickupFrom(String pickupFrom) {
        this.pickupFrom = pickupFrom;
    }

    public String getdropAt() {
        return dropAt;
    }

    public void setdropAt(String dropAt) {
        this.dropAt = dropAt;
    }

    public String getStartedOn() {
        return startedOn;
    }

    public void setStartedOn(String startedOn) {
        this.startedOn = startedOn;
    }

    public String getLastKnownLocation() {
        return lastKnownLocation;
    }

    public void setLastKnownLocation(String lastKnownLocation) {
        this.lastKnownLocation = lastKnownLocation;
    }

    public String getCurrentDateTime() {
        return currentDateTime;
    }

    public void setCurrentDateTime(String currentDateTime) {
        this.currentDateTime = currentDateTime;
    }


}
