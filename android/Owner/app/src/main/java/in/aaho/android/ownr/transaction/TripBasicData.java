package in.aaho.android.ownr.transaction;

/**
 * Created by mani on 18/09/17.
 */

class TripBasicData {
    String getDataLabel() {
        return dataLabel;
    }

    void setDataLabel(String dataLabel) {
        this.dataLabel = dataLabel;
    }

    String getDataValue() {
        return dataValue;
    }

    void setDataValue(String dataValue) {
        this.dataValue = dataValue;
    }

    public TripBasicData(String dataLabel, String dataValue) {
        this.dataLabel = dataLabel;
        this.dataValue = dataValue;
    }

    TripBasicData(){}

    private String dataLabel;
    private String dataValue;

}
