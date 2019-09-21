package in.aaho.android.ownr.data;

/**
 * Created by mani on 16/12/16.
 */

public class TripDetailsPaymentData {

    public TripDetailsPaymentData(String rateLabel, String rateValue) {
        this.rateLabel = rateLabel;
        this.rateValue = rateValue;
    }

    public TripDetailsPaymentData() {
    }

    private String rateLabel;
    private String rateValue;

    public String getRateLabel() {
        return rateLabel;
    }

    public void setRateLabel(String rateLabel) {
        this.rateLabel = rateLabel;
    }

    public String getRateValue() {
        return rateValue;
    }

    public void setRateValue(String rateValue) {
        this.rateValue = rateValue;
    }
}
