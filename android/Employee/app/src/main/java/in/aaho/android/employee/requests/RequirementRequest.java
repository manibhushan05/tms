package in.aaho.android.employee.requests;

import android.text.TextUtils;

import com.android.volley.AuthFailureError;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.HashMap;
import java.util.Map;

import in.aaho.android.employee.Aaho;
import in.aaho.android.employee.common.ApiPostRequest;
import in.aaho.android.employee.common.ApiResponseListener;

/**
 * Created by aaho on 18/04/18.
 */

public class RequirementRequest extends ApiPostRequest {

    public static final String REQ_CLIENT_KEY = "client_id";
    public static final String FROM_SHIP_DATE_KEY = "from_shipment_date";
    public static final String TO_SHIP_DATE_KEY = "to_shipment_date";
    public static final String FROM_CITY_KEY = "from_city_id";
    public static final String TO_CITY_KEY = "to_city_id";
    public static final String AAHO_OFFICE_KEY = "aaho_office_id";
    public static final String TONNAGE_KEY = "tonnage";
    public static final String NO_OF_VEHICLES_KEY = "no_of_vehicles";
    public static final String MATERIAL_KEY = "material";
    public static final String VEHICLE_TYPE_ID_KEY = "type_of_vehicle_id";
    /*public static final String VEHICLE_TYPE_ID_KEY = "vehicle_type_id";*/
    public static final String RATE_KEY = "rate";
    public static final String REMARK_KEY = "remark";
    public static final String REQ_STATUS = "req_status";
    public static final String REQ_CANCEL_REASON = "cancel_reason";

    public RequirementRequest(Integer client_id, String from_ship_date, String to_ship_date,
                              Integer from_city_id, Integer to_city_id, Integer aaho_office_id,
                              String tonnage, String no_of_vehicles, String material,
                              Integer truck_type, String rate, String remark, ApiResponseListener listener) {
        super(Api.REQUIREMENT_SUBMIT_URL, data(client_id, from_ship_date, to_ship_date, from_city_id,
                to_city_id, aaho_office_id, tonnage, no_of_vehicles, material, truck_type, rate, remark), listener);
    }

    private static JSONObject data(Integer client_id, String from_ship_date, String to_ship_date,
                                   Integer from_city_id, Integer to_city_id, Integer aaho_office_id,
                                   String tonnage, String no_of_vehicles, String material,
                                   Integer vehicle_type, String rate, String remark) {
        JSONObject jsonObject = new JSONObject();
        try {
            if(client_id != 0) {
                jsonObject.put(REQ_CLIENT_KEY, client_id);
            }
            if(!TextUtils.isEmpty(from_ship_date)) {
                jsonObject.put(FROM_SHIP_DATE_KEY, from_ship_date);
            }
            if(!TextUtils.isEmpty(to_ship_date)) {
                jsonObject.put(TO_SHIP_DATE_KEY, to_ship_date);
            }
            if(from_city_id != 0) {
                jsonObject.put(FROM_CITY_KEY, from_city_id);
            }
            if(to_city_id != 0) {
                jsonObject.put(TO_CITY_KEY, to_city_id);
            }
            if(aaho_office_id != 0) {
                jsonObject.put(AAHO_OFFICE_KEY, aaho_office_id);
            }
            if(!TextUtils.isEmpty(tonnage)) {
                jsonObject.put(TONNAGE_KEY, tonnage);
            }
            if(!TextUtils.isEmpty(no_of_vehicles)) {
                jsonObject.put(NO_OF_VEHICLES_KEY, no_of_vehicles);
            }
            if(!TextUtils.isEmpty(material)) {
                jsonObject.put(MATERIAL_KEY, material);
            }
            if(vehicle_type != 0) {
                jsonObject.put(VEHICLE_TYPE_ID_KEY, vehicle_type);
            }
            if(!TextUtils.isEmpty(rate)) {
                jsonObject.put(RATE_KEY, rate);
            }
            if(!TextUtils.isEmpty(remark)) {
                jsonObject.put(REMARK_KEY, remark);
            }
            jsonObject.put(REQ_STATUS, "open");
        } catch (JSONException e) {
        }
        return jsonObject;
    }

    @Override
    public Map<String, String> getHeaders() throws AuthFailureError {
        Map<String, String> params = new HashMap<String, String>();
        params.put("Authorization", "Token "+ Aaho.getToken());
        /*params.put("Content-Type", "application/json");*/
        /*params.put("Content-Type", "application/json;charset=utf-8");*/

        return params;
    }

    @Override
    public String getBodyContentType() {
        return "application/json";
    }
}
