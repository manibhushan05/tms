package in.aaho.android.customer.common;

import android.util.Log;

/**
 * Created by shobhit on 3/7/16.
 */
public class ApiGetRequest extends ApiRequest {
    private static final String SLASH = "/";

    public ApiGetRequest(String url, Long id, ApiResponseListener listener) {
        super(Method.GET, getUrl(url, id), null, listener);

        Log.e("[REQUEST]", "GET " + getUrl(url, id) + "\n\n");
    }

    private static String getUrl(String url, Long id) {
        if (id == null) {
            return url;
        } else {
            return joinUrl(url, id);
        }
    }

    private static String joinUrl(String url, long id) {
        String sep = url.endsWith(SLASH) ? "" : SLASH;
        return url + sep + id + SLASH;
    }
}

