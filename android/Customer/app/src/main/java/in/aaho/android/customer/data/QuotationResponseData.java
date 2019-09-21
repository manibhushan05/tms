package in.aaho.android.customer.data;

/**
 * Created by mani on 10/8/16.
 */
public class QuotationResponseData {
    private String responseId;
    private String responseDatetime;
    private String vendorName;
    private String message;
    public QuotationResponseData(){}

    public QuotationResponseData(String responseId, String responseDatetime, String vendorName, String message) {
        this.responseId = responseId;
        this.responseDatetime = responseDatetime;
        this.vendorName = vendorName;
        this.message = message;
    }

    public String getResponseId() {
        return responseId;
    }

    public void setResponseId(String responseId) {
        this.responseId = responseId;
    }

    public String getResponseDatetime() {
        return responseDatetime;
    }

    public void setResponseDatetime(String responseDatetime) {
        this.responseDatetime = responseDatetime;
    }

    public String getVendorName() {
        return vendorName;
    }

    public void setVendorName(String vendorName) {
        this.vendorName = vendorName;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}
