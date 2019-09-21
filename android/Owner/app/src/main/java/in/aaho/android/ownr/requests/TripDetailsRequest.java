package in.aaho.android.ownr.requests;

import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.ownr.common.ApiGetRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by mani on 12/11/16.
 */


public class TripDetailsRequest extends ApiGetRequest {

    public TripDetailsRequest(String transactionID, ApiResponseListener listener) {
        super(Api.COMPLETE_TRIP_DETAILS, ApiGetRequest.NO_HEADER, listener);
    }
    private static JSONObject data(String transactionID) {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put("transactionId", transactionID);
        } catch (JSONException e) {
            Log.e(Api.TAG,"Error in trip history");
        }
        return jsonObject;
    }

}