package in.aaho.android.customer.booking;

/**
 * Created by shobhit on 11/8/16.
 */
public interface LocationFormAdapter {
    void setCityField(int position, City city);
    City getCityField(int position);
    void setAddressField(int position, Address address);
    Address getAddressField(int position);
}
