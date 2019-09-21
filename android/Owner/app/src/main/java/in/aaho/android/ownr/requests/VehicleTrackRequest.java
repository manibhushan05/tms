package in.aaho.android.ownr.requests;

import in.aaho.android.ownr.common.ApiGetRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by shobhit on 1/8/16.
 */
public class VehicleTrackRequest extends ApiGetRequest {

    public VehicleTrackRequest(ApiResponseListener listener) {
        super(Api.VEHICLE_TRACK_URL, ApiGetRequest.NO_HEADER, listener);
    }
}
