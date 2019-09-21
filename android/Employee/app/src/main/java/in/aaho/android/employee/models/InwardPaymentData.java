package in.aaho.android.employee.models;

/**
 * Created by Suraj.M
 */

public class InwardPaymentData {
    private String paymentDate;
    private String amount;
    private String modeOfPayment;
    private String receivedFrom;
    private String tds;

    public InwardPaymentData(){}

    public InwardPaymentData(String paymentDate, String amount, String modeOfPayment,
                             String receivedFrom, String tds) {
        this.paymentDate = paymentDate;
        this.amount = amount;
        this.modeOfPayment = modeOfPayment;
        this.receivedFrom = receivedFrom;
        this.tds = tds;
    }

    public String getPaymentDate() {
        return paymentDate;
    }

    public void setPaymentDate(String paymentDate) {
        this.paymentDate = paymentDate;
    }

    public String getAmount() {
        return amount;
    }

    public void setAmount(String amount) {
        this.amount = amount;
    }

    public String getModeOfPayment() {
        return modeOfPayment;
    }

    public void setModeOfPayment(String modeOfPayment) {
        this.modeOfPayment = modeOfPayment;
    }

    public String getReceivedFrom() {
        return receivedFrom;
    }

    public void setReceivedFrom(String receivedFrom) {
        this.receivedFrom = receivedFrom;
    }

    public String getTds() {
        return tds;
    }

    public void setTds(String tds) {
        this.tds = tds;
    }
}
