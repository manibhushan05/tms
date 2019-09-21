package in.aaho.android.ownr.requests;

import java.util.Map;

import in.aaho.android.ownr.common.ApiGetRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by Suraj on 1/8/16.
 */
public class VehiclePathDataRequest extends ApiGetRequest {

    public VehiclePathDataRequest(Map<String, String> params, ApiResponseListener listener) {
        super(Api.VEHICLE_GPS_DATA_URL, params, listener);
    }

}
