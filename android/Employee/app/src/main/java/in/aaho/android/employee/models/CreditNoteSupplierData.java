package in.aaho.android.employee.models;

/**
 * Created by Suraj.M
 */

public class CreditNoteSupplierData {
    private String paidTo;
    private String amount;
    private String date;
    private String status;
    private String creditNoteNo;

    public CreditNoteSupplierData(){}

    public CreditNoteSupplierData(String paymentDate, String amount, String status,
                                  String paidTo, String creditNoteNo) {
        this.paidTo = paidTo;
        this.amount = amount;
        this.date = paymentDate;
        this.status = status;
        this.creditNoteNo = creditNoteNo;
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

    public String getCreditNoteNo() {
        return creditNoteNo;
    }

    public void setCreditNoteNo(String creditNoteNo) {
        this.creditNoteNo = creditNoteNo;
    }
}
