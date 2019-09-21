package in.aaho.android.ownr.data;

/**
 * Created by mani on 3/8/16.
 */
public class AddressData {
    private String address;
    private String city;
    public AddressData(){}
    public AddressData(String address, String city) {
        this.address = address;
        this.city = city;
    }

    public String getAddress() {
        return address;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public String getCity() {
        return city;
    }

    public void setCity(String city) {
        this.city = city;
    }
}
