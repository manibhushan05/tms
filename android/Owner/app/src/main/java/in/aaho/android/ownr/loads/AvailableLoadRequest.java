package in.aaho.android.ownr.loads;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import in.aaho.android.ownr.common.Utils;

/**
 * Created by suraj.m
 */
public class AvailableLoadRequest {

    public long id, rate, tonnage, noOfVehicles;
    public String fromShipmentDate, toShipmentDate;
    public String material, toCity, client, fromCity, typeOfVehicle, aahoOffice,
                  fromState, toState;


    private static final String KEY_ID = "id";
    private static final String KEY_TO_SHIPMENT_DATE = "to_shipment_date";
    private static final String KEY_MATERIAL = "material";
    private static final String KEY_RATE = "rate";
    private static final String KEY_TONNAGE = "tonnage";
    private static final String KEY_NO_OF_VEHICLE = "no_of_vehicles";
    private static final String KEY_FROM_SHIPMENT_DATE = "from_shipment_date";
    private static final String KEY_TO_CITY = "to_city";
    private static final String KEY_CLIENT = "client";
    private static final String KEY_FROM_CITY = "from_city";
    private static final String KEY_TYPE_OF_VEHICLE = "type_of_vehicle";
    private static final String KEY_AAHO_OFFICE = "aaho_office";
    private static final String KEY_FROM_STATE = "from_state";
    private static final String KEY_TO_STATE = "to_state";


    public AvailableLoadRequest(long id, long rate, long tonnage, long noOfVehicles,
                                String fromShipmentDate, String toShipmentDate,
                                String material, String toCity, String client, String fromCity,
                                String typeOfVehicle, String aahoOffice, String fromState,String toState) {
        this.id = id;
        this.rate = rate;
        this.tonnage = tonnage;
        this.noOfVehicles = noOfVehicles;
        this.fromShipmentDate = fromShipmentDate;
        this.toShipmentDate = toShipmentDate;
        this.material = material;
        this.toCity = toCity;
        this.client = client;
        this.fromCity = fromCity;
        this.typeOfVehicle = typeOfVehicle;
        this.aahoOffice = aahoOffice;
        this.fromState = fromState;
        this.toState = toState;
    }

    public static AvailableLoadRequest fromJson(JSONObject jsonObject) throws JSONException {
        if (jsonObject == null || jsonObject.length() == 0) {
            return null;
        }
        return new AvailableLoadRequest(
                Utils.getLong(jsonObject, KEY_ID),
                Utils.getLong(jsonObject, KEY_RATE)==null?-1:Utils.getLong(jsonObject, KEY_RATE),
                Utils.getLong(jsonObject, KEY_TONNAGE)==null?-1:Utils.getLong(jsonObject, KEY_TONNAGE),
                Utils.getLong(jsonObject, KEY_NO_OF_VEHICLE)==null?-1:Utils.getLong(jsonObject, KEY_NO_OF_VEHICLE),
                Utils.get(jsonObject, KEY_FROM_SHIPMENT_DATE),
                Utils.get(jsonObject, KEY_TO_SHIPMENT_DATE),
                Utils.get(jsonObject, KEY_MATERIAL),
                Utils.get(jsonObject, KEY_TO_CITY),
                Utils.get(jsonObject, KEY_CLIENT),
                Utils.get(jsonObject, KEY_FROM_CITY),
                Utils.get(jsonObject, KEY_TYPE_OF_VEHICLE),
                Utils.get(jsonObject, KEY_AAHO_OFFICE),
                Utils.get(jsonObject, KEY_FROM_STATE),
                Utils.get(jsonObject, KEY_TO_STATE)
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

    public static List<AvailableLoadRequest> fromJson(JSONArray jsonArray) throws JSONException {
        List<AvailableLoadRequest> vehicles = new ArrayList<>();
        for (int i = 0; i < jsonArray.length(); i++) {
            JSONObject obj = jsonArray.getJSONObject(i);
            AvailableLoadRequest vehicle = fromJson(obj);
            vehicles.add(vehicle);
        }
        return vehicles;
    }
}
