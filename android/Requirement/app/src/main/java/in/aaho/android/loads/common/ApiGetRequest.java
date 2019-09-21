package in.aaho.android.loads.common;

import android.text.TextUtils;

/**
 * Created by aaho on 18/04/18.
 */

public class ApiGetRequest extends ApiRequest {
    private static final String SLASH = "/";
    public static final long NO_HEADER = -1;

    public ApiGetRequest(String url, ApiResponseListener listener) {
        super(Method.GET, url, null, listener);

        //Log.e("[REQUEST]", "GET " + url + "\n\n");
    }

    public ApiGetRequest(String url, Long id, ApiResponseListener listener) {
        super(Method.GET, getUrl(url, id), null, listener);

        //Log.e("[REQUEST]", "GET " + getUrl(url, id) + "\n\n");
    }

    private static String getUrl(String url, Long id) {
        if (id == null || id == NO_HEADER) {
            return url;
        } else {
            return joinUrl(url, id);
        }
    }

    private static String joinUrl(String url, long id) {
        String sep = url.endsWith(SLASH) ? "" : SLASH;
        return url + sep + id + SLASH;
    }

    public ApiGetRequest(String url, String param, ApiResponseListener listener) {
        super(Method.GET, getUrl(url, param), null, listener);

        //Log.e("[REQUEST]", "GET " + getUrl(url, param) + "\n\n");
    }

    private static String joinUrl(String url, String param) {
        String sep = url.endsWith(SLASH) ? "" : SLASH;
        return url + sep + param + SLASH;
    }

    private static String getUrl(String url, String param) {
        if (TextUtils.isEmpty(param)) {
            return url;
        } else {
            return joinUrl(url, param);
        }
    }
}

