package in.aaho.android.ownr.parser;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

import in.aaho.android.ownr.data.AddressData;

/**
 * Created by mani on 19/8/16.
 */
public class AddressParser {
    private JSONArray jsonArray;
    private ArrayList<AddressData> addressDataArrayList;

    public AddressParser(JSONArray jsonArray) {
        this.jsonArray = jsonArray;
    }

    public ArrayList<AddressData> getAddressDataArrayList() {
        addressDataArrayList = new ArrayList<>();
        for (int i = 0; i < jsonArray.length();i++){
            try {
                JSONObject jsonObject = (JSONObject)jsonArray.get(i);
                AddressData addressData = new AddressData();
                addressData.setAddress(jsonObject.getString("address"));
                addressData.setCity(jsonObject.getString("city"));
                addressDataArrayList.add(addressData);
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
        return addressDataArrayList;
    }

    public void setAddressDataArrayList(ArrayList<AddressData> addressDataArrayList) {
        this.addressDataArrayList = addressDataArrayList;
    }
}
