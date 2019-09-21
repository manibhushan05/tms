package in.aaho.android.aahocustomers.loads;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import in.aaho.android.aahocustomers.booking.VehicleCategory;
import in.aaho.android.aahocustomers.common.Utils;

/**
 * Created by mani on 6/8/16.
 */
public class VehicleRequest {

    public long id;
    public String vehicleType;
    public VehicleCategory category;
    public String transactionNumber;
    public long transactionId;
    public Date shipmentDate;
    public String fromCity;
    public String fromState;
    public String toCity;
    public String toState;
    public int quantity;
    public VehicleRequestQuote quote;

    private static final String VEHICLE_REQUEST_ID_KEY = "vehicle_request_id";
    private static final String VEHICLE_CATEGORY_KEY = "vehicle_category";
    private static final String VEHICLE_CATEGORY_ID_KEY = "vehicle_category_id";
    private static final String VEHICLE_QUANTITY_KEY = "vehicle_quantity";
    private static final String TRANSACTION_ID_KEY = "transaction_id";
    private static final String TRANSACTION_NUMBER_KEY = "transaction_number";
    private static final String SHIPMENT_DATETIME_KEY = "shipment_datetime";
    private static final String FROM_CITY_KEY = "from_city";
    private static final String FROM_STATE_KEY = "from_state";
    private static final String TO_CITY_KEY = "to_city";
    private static final String TO_STATE_KEY = "to_state";
    private static final String QUOTE_KEY = "quote";


    public VehicleRequest(long id, String vehicleType, Long categoryId, String transactionNumber,
                          long transactionId, Date shipmentDate, String fromCity, String fromState,
                          String toCity, String toState, int quantity, VehicleRequestQuote quote) {
        this.id = id;
        this.vehicleType = vehicleType;
        this.transactionNumber = transactionNumber;
        this.transactionId = transactionId;
        this.shipmentDate = shipmentDate;
        this.fromCity = fromCity;
        this.fromState = fromState;
        this.toCity = toCity;
        this.toState = toState;
        this.quantity = quantity;
        this.quote = quote;
        if (categoryId != null) {
            this.category = VehicleCategory.get(categoryId);
        }
    }

    public String getName() {
        if (category != null) {
            return category.getFullName();
        } else {
            return vehicleType;
        }
    }

    public VehicleCategory getCategory() {
        return category;
    }

    public static VehicleRequest fromJson(JSONObject jsonObject) throws JSONException {
        if (jsonObject == null || jsonObject.length() == 0) {
            return null;
        }
        return new VehicleRequest(
                Utils.getLong(jsonObject, VEHICLE_REQUEST_ID_KEY),
                Utils.get(jsonObject, VEHICLE_CATEGORY_KEY),
                Utils.getLong(jsonObject, VEHICLE_CATEGORY_ID_KEY),
                Utils.get(jsonObject, TRANSACTION_NUMBER_KEY),
                Utils.getLong(jsonObject, TRANSACTION_ID_KEY),
                Utils.getDate(jsonObject, SHIPMENT_DATETIME_KEY),
                Utils.get(jsonObject, FROM_CITY_KEY),
                Utils.get(jsonObject, FROM_STATE_KEY),
                Utils.get(jsonObject, TO_CITY_KEY),
                Utils.get(jsonObject, TO_STATE_KEY),
                jsonObject.getInt(VEHICLE_QUANTITY_KEY),
                VehicleRequestQuote.fromJson(getObject(jsonObject, QUOTE_KEY))
        );
    }

    private static JSONObject getObject(JSONObject jsonObject, String key) {
        if (jsonObject == null || jsonObject.length() == 0) {
            return null;
        }
        if (!jsonObject.has(key) || jsonObject.isNull(key)) {
            return null;
        }
        try {
            return jsonObject.getJSONObject(key);
        } catch (JSONException e) {
            return null;
        }
    }

    public static List<VehicleRequest> fromJson(JSONArray jsonArray) throws JSONException {
        List<VehicleRequest> vehicles = new ArrayList<>();
        for (int i = 0; i < jsonArray.length(); i++) {
            JSONObject obj = jsonArray.getJSONObject(i);
            VehicleRequest vehicle = fromJson(obj);
            vehicles.add(vehicle);
        }
        return vehicles;
    }
}
