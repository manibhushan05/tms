package in.aaho.android.employee;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

import in.aaho.android.employee.common.Utils;

/**
 * Created by suraj.m
 */
public class AvailableQuoteData {

    public long id, noOfVehicles, rate;
    public double tonnage;
    ;
    public String brokerName,brokerPhone;

    private static final String KEY_BROKER_NAME = "broker_name";
    private static final String KEY_BROKER_PHONE = "broker_phone";
    private static final String KEY_NO_OF_VEHICLE = "no_of_vehicles";
    private static final String KEY_RATE = "rate";
    private static final String KEY_TONNAGE = "tonnage";


    public AvailableQuoteData(long rate, double tonnage, long noOfVehicles,
                              String brokerName,String brokerPhone) {
        this.rate = rate;
        this.noOfVehicles = noOfVehicles;
        this.brokerName = brokerName;
        this.brokerPhone = brokerPhone;
        this.tonnage = tonnage;
    }

    public static AvailableQuoteData fromJson(JSONObject jsonObject) throws JSONException {
        if (jsonObject == null || jsonObject.length() == 0) {
            return null;
        }

        String brokerName = "",brokerPhone = "";
        long rate = Utils.getLong(jsonObject, KEY_RATE) == null ? -1 : Utils.getLong(jsonObject, KEY_RATE);
        double tonnage = -1;
        long noOfVehicle = -1;
        JSONObject reqVehicleQuote = jsonObject.getJSONObject("requirement_vehicle_quote");
        if(reqVehicleQuote != null) {
            tonnage = Utils.getDouble(reqVehicleQuote, KEY_TONNAGE) == null ? -1 : Utils.getLong(reqVehicleQuote, KEY_TONNAGE);
            noOfVehicle = Utils.getLong(reqVehicleQuote, KEY_NO_OF_VEHICLE) == null ? -1 : Utils.getLong(reqVehicleQuote, KEY_NO_OF_VEHICLE);
        }
        JSONObject broker = jsonObject.getJSONObject("broker");
        if(broker != null) {
            brokerName = Utils.get(broker, KEY_BROKER_NAME);
            brokerPhone = Utils.get(broker, KEY_BROKER_PHONE);
        }

        return new AvailableQuoteData(
                rate,tonnage,noOfVehicle,brokerName,brokerPhone
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

    public static List<AvailableQuoteData> fromJson(JSONArray jsonArray) throws JSONException {
        List<AvailableQuoteData> vehicles = new ArrayList<>();
        for (int i = 0; i < jsonArray.length(); i++) {
            JSONObject obj = jsonArray.getJSONObject(i);
            AvailableQuoteData vehicle = fromJson(obj);
            vehicles.add(vehicle);
        }
        return vehicles;
    }
}
