package in.aaho.android.customer.data;

import java.util.ArrayList;

/**
 * Created by mani on 10/8/16.
 */
public class QuotationsData {
    private String transactionId;
    private String pickUpFrom;
    private String dropAt;
    private String numberOfTruck;
    private String shipmentDate;
    private  String NumberOfQuote;
    private ArrayList<QuotationsData> quotationsDataArrayList;
    public QuotationsData(){}

    public QuotationsData(String transactionId, String pickUpFrom, String dropAt, String numberOfTruck, String shipmentDate, String numberOfQuote) {
        this.transactionId = transactionId;
        this.pickUpFrom = pickUpFrom;
        this.dropAt = dropAt;
        this.numberOfTruck = numberOfTruck;
        this.shipmentDate = shipmentDate;
        NumberOfQuote = numberOfQuote;
    }

    public String getTransactionId() {
        return transactionId;
    }

    public void setTransactionId(String transactionId) {
        this.transactionId = transactionId;
    }

    public String getPickUpFrom() {
        return pickUpFrom;
    }

    public void setPickUpFrom(String pickUpFrom) {
        this.pickUpFrom = pickUpFrom;
    }

    public String getDropAt() {
        return dropAt;
    }

    public void setDropAt(String dropAt) {
        this.dropAt = dropAt;
    }

    public String getNumberOfTruck() {
        return numberOfTruck;
    }

    public void setNumberOfTruck(String numberOfTruck) {
        this.numberOfTruck = numberOfTruck;
    }

    public String getShipmentDate() {
        return shipmentDate;
    }

    public void setShipmentDate(String shipmentDate) {
        this.shipmentDate = shipmentDate;
    }

    public String getNumberOfQuote() {
        return NumberOfQuote;
    }

    public void setNumberOfQuote(String numberOfQuote) {
        NumberOfQuote = numberOfQuote;
    }

    public ArrayList<QuotationsData> getQuotationsDataArrayList() {
        return quotationsDataArrayList;
    }

    public void setQuotationsDataArrayList(ArrayList<QuotationsData> quotationsDataArrayList) {
        this.quotationsDataArrayList = quotationsDataArrayList;
    }
}
