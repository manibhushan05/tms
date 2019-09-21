package in.aaho.android.ownr.requests;

import in.aaho.android.ownr.common.ApiGetRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by Suraj
 */
public class GetCityDataRequest extends ApiGetRequest {

    public GetCityDataRequest(String url, ApiResponseListener listener) {
        super(url, ApiGetRequest.NO_HEADER, listener);
    }

    /** Make the url for GET request with page and search value
     * @param page
     * @param search
     * @return complete url with page count and search keyword
     */
    public static String makeSearchUrl(String page,String search) {
        String url = Api.CITY_DATA_URL + "?page="+page + "&search="+search;

        return url;
    }
}
