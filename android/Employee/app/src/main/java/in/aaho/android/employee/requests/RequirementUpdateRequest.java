package in.aaho.android.employee.requests;

import android.text.TextUtils;
import android.util.Log;

import com.android.volley.AuthFailureError;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.HashMap;
import java.util.Map;

import in.aaho.android.employee.Aaho;
import in.aaho.android.employee.common.ApiPostRequest;
import in.aaho.android.employee.common.ApiResponseListener;

/**
 * Created by Suraj M
 */

public class RequirementUpdateRequest extends ApiPostRequest {
    private static final String TAG = "ReqUpdateRequest";
    private static final String REQ_ID_KEY = "requirement_id";

    public RequirementUpdateRequest(Integer id,Integer client_id, String from_ship_date, String to_ship_date,
                                    Integer from_city_id, Integer to_city_id, Integer aaho_office_id,
                                    String tonnage, String no_of_vehicles, String material,
                                    Integer vehicleTypeId, String rate,String remark,boolean isVerified,
                                    boolean isFullfilled, boolean isCancelled,
                                    String cancelReason,ApiResponseListener listener) {
        super(Api.UPDATE_REQUIREMENT_URL+id+"/", data(id,client_id, from_ship_date, to_ship_date, from_city_id,
                to_city_id, aaho_office_id, tonnage, no_of_vehicles, material, vehicleTypeId, rate, remark, isVerified,
                isFullfilled, isCancelled, cancelReason), listener);
    }

    private static JSONObject data(Integer id,Integer client_id, String from_ship_date, String to_ship_date,
                                   Integer from_city_id, Integer to_city_id, Integer aaho_office_id,
                                   String tonnage, String no_of_vehicles, String material,
                                   Integer vehicleTypeId, String rate,String remark, boolean isVerified,
                                   boolean isFullfilled, boolean isCancelled,String cancelReason) {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put(REQ_ID_KEY, id);
            if(client_id != 0) {
                jsonObject.put(RequirementRequest.REQ_CLIENT_KEY, client_id);
            }
            if(!TextUtils.isEmpty(from_ship_date)) {
                jsonObject.put(RequirementRequest.FROM_SHIP_DATE_KEY, from_ship_date);
            }
            if(!TextUtils.isEmpty(to_ship_date)) {
                jsonObject.put(RequirementRequest.TO_SHIP_DATE_KEY, to_ship_date);
            }
            if(from_city_id != 0) {
                jsonObject.put(RequirementRequest.FROM_CITY_KEY, from_city_id);
            }
            if(to_city_id != 0) {
                jsonObject.put(RequirementRequest.TO_CITY_KEY, to_city_id);
            }
            if(aaho_office_id != 0) {
                jsonObject.put(RequirementRequest.AAHO_OFFICE_KEY, aaho_office_id);
            }
            if(!TextUtils.isEmpty(tonnage)) {
                jsonObject.put(RequirementRequest.TONNAGE_KEY, tonnage);
            }
            if(!TextUtils.isEmpty(no_of_vehicles)) {
                jsonObject.put(RequirementRequest.NO_OF_VEHICLES_KEY, no_of_vehicles);
            }
            if(!TextUtils.isEmpty(material)) {
                jsonObject.put(RequirementRequest.MATERIAL_KEY, material);
            }
            if(vehicleTypeId != 0) {
                jsonObject.put(RequirementRequest.VEHICLE_TYPE_ID_KEY, vehicleTypeId);
            }
            if(!TextUtils.isEmpty(rate)) {
                jsonObject.put(RequirementRequest.RATE_KEY, rate);
            }
            if(!TextUtils.isEmpty(remark)) {
                jsonObject.put(RequirementRequest.REMARK_KEY, remark);
            }
            String reqStatus = "unverified";
            if(isFullfilled) {
                reqStatus = "fulfilled";
            } else if(isCancelled){
                reqStatus = "cancelled";
                // Add cancelled reason in request
                if(!TextUtils.isEmpty(cancelReason)) {
                    jsonObject.put(RequirementRequest.REQ_CANCEL_REASON, cancelReason);
                }
            } else if(isVerified){
                reqStatus = "open";
            }
            jsonObject.put(RequirementRequest.REQ_STATUS, reqStatus);
        } catch (JSONException e) {
            Log.i(TAG,"Exception = "+e.getLocalizedMessage());
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
