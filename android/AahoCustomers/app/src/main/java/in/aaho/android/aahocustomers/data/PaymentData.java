package in.aaho.android.aahocustomers.data;

/**
 * Created by mani on 21/9/17.
 */

public class PaymentData {
    private String paymentDate;
    private String amount;
    private String modeOfPayment;
    private String paidTo;
    private String remarks;
    private String remarksLabel;
    public PaymentData(){}

    public PaymentData(String paymentDate, String amount, String modeOfPayment, String paidTo, String remarks, String remarksLabel) {
        this.paymentDate = paymentDate;
        this.amount = amount;
        this.modeOfPayment = modeOfPayment;
        this.paidTo = paidTo;
        this.remarks = remarks;
        this.remarksLabel = remarksLabel;
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

    public String getPaidTo() {
        return paidTo;
    }

    public void setPaidTo(String paidTo) {
        this.paidTo = paidTo;
    }

    public String getRemarks() {
        return remarks;
    }

    public void setRemarks(String remarks) {
        this.remarks = remarks;
    }

    public String getRemarksLabel() {
        return remarksLabel;
    }

    public void setRemarksLabel(String remarksLabel) {
        this.remarksLabel = remarksLabel;
    }
}
