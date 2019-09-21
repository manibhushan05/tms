package in.aaho.android.aahocustomers.requests;

import in.aaho.android.aahocustomers.common.ApiGetRequest;
import in.aaho.android.aahocustomers.common.ApiResponseListener;

/**
 * Created by Suraj on 1/8/16.
 */
public class VehiclePathDataRequest extends ApiGetRequest {

    public VehiclePathDataRequest(String vehicleId, ApiResponseListener listener) {
        super(Api.VEHICLE_GPS_DATA_URL, vehicleId, listener);
    }

}
