package in.aaho.android.ownr.booking;

/**
 * Created by mani on 11/8/16.
 */
public interface LocationFormAdapter {
    void setCityField(int position, City city);
    City getCityField(int position);
    void setAddressField(int position, Address address);
    Address getAddressField(int position);
}
