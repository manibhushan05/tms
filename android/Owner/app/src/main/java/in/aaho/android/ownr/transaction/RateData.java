package in.aaho.android.ownr.transaction;

/**
 * Created by mani on 18/09/17.
 */

public class RateData {
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

    private String rateLabel;
    private String rateValue;
}
