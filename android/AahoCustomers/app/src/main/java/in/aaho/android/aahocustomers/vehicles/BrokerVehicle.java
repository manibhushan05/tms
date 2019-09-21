package in.aaho.android.aahocustomers.vehicles;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

import in.aaho.android.aahocustomers.booking.VehicleCategory;
import in.aaho.android.aahocustomers.common.Utils;

/**
 * Created by shobhit on 6/8/16.
 */
public class BrokerVehicle {

    private long id;
    private String number;
    private String model;
    private VehicleCategory category;

    public static final String ID_KEY = "id";
    public static final String NUMBER_KEY = "vehicle_number";
    public static final String CATEGORY_KEY = "vehicle_type";
    public static final String MODEL_KEY = "vehicle_model";


    public BrokerVehicle(long id, String number, String model, Long categoryId) {
        this.id = id;
        this.number = number;
        this.model = model;
        if (categoryId != null) {
            this.category = VehicleCategory.get(categoryId);
        }
    }

    public String getName() {
        if (category != null) {
            return category.getFullName();
        } else {
            return null;
        }
    }

    public VehicleCategory getCategory() {
        return category;
    }

    public void setCategory(VehicleCategory category) {
        this.category = category;
    }

    public long getId() {
        return id;
    }

    public void setId(long id) {
        this.id = id;
    }

    public String getNumber() {
        return VehicleNumber.displayFormat(number);
    }

    public void setNumber(String number) {
        this.number = number;
    }

    public String getModel() {
        return model;
    }

    public void setModel(String model) {
        this.model = model;
    }

    public static BrokerVehicle fromJson(JSONObject jsonObject) throws JSONException {
        if (jsonObject == null || jsonObject.length() == 0) {
            return null;
        }
        return new BrokerVehicle(
                jsonObject.getLong(ID_KEY),
                Utils.get(jsonObject, NUMBER_KEY),
                Utils.get(jsonObject, MODEL_KEY),
                jsonObject.getLong(CATEGORY_KEY)
        );
    }

    public static List<BrokerVehicle> fromJson(JSONArray jsonArray) throws JSONException {
        List<BrokerVehicle> vehicles = new ArrayList<>();
        for (int i = 0; i < jsonArray.length(); i++) {
            JSONObject obj = jsonArray.getJSONObject(i);
            BrokerVehicle vehicle = fromJson(obj);
            vehicles.add(vehicle);
        }
        return vehicles;
    }




}
