package in.aaho.android.loads.requests;

import in.aaho.android.loads.common.ApiGetRequest;
import in.aaho.android.loads.common.ApiResponseListener;

/**
 * Created by aaho on 22/04/18.
 */


public class VehicleTypeDataRequest extends ApiGetRequest {

    public VehicleTypeDataRequest(String url, ApiResponseListener listener) {
        super(url, ApiGetRequest.NO_HEADER, listener);
    }

    /** Make the url for GET request with page and search value
     * @param page
     * @param search
     * @return complete url with page count and search keyword
     */
    public static String makeSearchUrl(String page,String search) {
        String url = Api.VEHICLE_TYPE_DATA_URL + "?page="+page + "&search="+search;
//        String url = Api.VEHICLE_TYPE_DATA_URL;

        return url;
    }
}
