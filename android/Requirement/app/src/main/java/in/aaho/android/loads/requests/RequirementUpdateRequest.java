package in.aaho.android.loads.requests;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.loads.common.ApiPostRequest;
import in.aaho.android.loads.common.ApiResponseListener;

/**
 * Created by aaho on 18/04/18.
 */

public class RequirementUpdateRequest extends ApiPostRequest {

    private static final String REQ_ID_KEY = "requirement_id";
    private static final String REQ_CITY_KEY = "client_id";
    private static final String FROM_SHIP_DATE_KEY = "from_shipment_date";
    private static final String TO_SHIP_DATE_KEY = "to_shipment_date";
    private static final String FROM_CITY_KEY = "from_city_id";
    private static final String TO_CITY_KEY = "to_city_id";
    private static final String AAHO_OFFICE_KEY = "aaho_office_id";
    private static final String TONNAGE_KEY = "tonnage";
    private static final String NO_OF_VEHICLES_KEY = "no_of_vehicles";
    private static final String MATERIAL_KEY = "material";
    private static final String VEHICLE_TYPE_ID_KEY = "vehicle_type_id";
    private static final String RATE_KEY = "rate";
    private static final String REMARK_KEY = "remark";
    private static final String REQ_STATUS = "req_status";

    public RequirementUpdateRequest(Integer id,Integer client_id, String from_ship_date, String to_ship_date,
                                    Integer from_city_id, Integer to_city_id, Integer aaho_office_id,
                                    String tonnage, String no_of_vehicles, String material,
                                    Integer vehicleTypeId, String rate, String remark,boolean isVerified,
                                    boolean isFullfilled, boolean isCancelled, ApiResponseListener listener) {
        super(Api.UPDATE_REQUIREMENT_URL, data(id,client_id, from_ship_date, to_ship_date, from_city_id,
                to_city_id, aaho_office_id, tonnage, no_of_vehicles, material, vehicleTypeId, rate, remark, isVerified,
                isFullfilled, isCancelled), listener);
    }

    private static JSONObject data(Integer id,Integer client_id, String from_ship_date, String to_ship_date,
                                   Integer from_city_id, Integer to_city_id, Integer aaho_office_id,
                                   String tonnage, String no_of_vehicles, String material,
                                   Integer vehicleTypeId, String rate, String remark, boolean isVerified,
                                   boolean isFullfilled, boolean isCancelled) {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put(REQ_ID_KEY, id);
            jsonObject.put(REQ_CITY_KEY, client_id);
            jsonObject.put(FROM_SHIP_DATE_KEY, from_ship_date);
            jsonObject.put(TO_SHIP_DATE_KEY, to_ship_date);
            jsonObject.put(FROM_CITY_KEY, from_city_id);
            jsonObject.put(TO_CITY_KEY, to_city_id);
            jsonObject.put(AAHO_OFFICE_KEY, aaho_office_id);
            jsonObject.put(TONNAGE_KEY, tonnage);
            jsonObject.put(NO_OF_VEHICLES_KEY, no_of_vehicles);
            jsonObject.put(MATERIAL_KEY, material);
            jsonObject.put(VEHICLE_TYPE_ID_KEY, vehicleTypeId);
            jsonObject.put(RATE_KEY, rate);
            jsonObject.put(REMARK_KEY, remark);
            String reqStatus = "unverified";
            if(isFullfilled) {
                reqStatus = "fulfilled";
            }else if(isCancelled){
                reqStatus = "cancelled";
            }else if(isVerified){
                reqStatus = "open";
            }
            jsonObject.put(REQ_STATUS, reqStatus);
        } catch (JSONException e) {
        }
        return jsonObject;
    }
}
