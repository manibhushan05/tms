package in.aaho.android.aahocustomers.requests;

import in.aaho.android.aahocustomers.common.ApiGetRequest;
import in.aaho.android.aahocustomers.common.ApiResponseListener;

/**
 * Created by aaho on 21/04/18.
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
