package in.aaho.android.employee.models;

/**
 * Created by Suraj.M
 */

public class DebitNoteSupplierData {
    private String paidTo;
    private String amount;
    private String date;
    private String status;
    private String debitNoteNo;

    public DebitNoteSupplierData(){}

    public DebitNoteSupplierData(String paymentDate, String amount, String status,
                                 String paidTo, String debitNoteNo) {
        this.paidTo = paidTo;
        this.amount = amount;
        this.date = paymentDate;
        this.status = status;
        this.debitNoteNo = debitNoteNo;
    }

    public String getDate() {
        return date;
    }

    public void setDate(String date) {
        this.date = date;
    }

    public String getAmount() {
        return amount;
    }

    public void setAmount(String amount) {
        this.amount = amount;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getPaidTo() {
        return paidTo;
    }

    public void setPaidTo(String paidTo) {
        this.paidTo = paidTo;
    }

    public String getDebitNoteNo() {
        return debitNoteNo;
    }

    public void setDebitNoteNo(String debitNoteNo) {
        this.debitNoteNo = debitNoteNo;
    }
}
