package in.aaho.android.ownr.common;

import android.text.TextUtils;
import android.util.Log;

import com.android.volley.AuthFailureError;

import java.util.HashMap;
import java.util.Map;

import in.aaho.android.ownr.Aaho;

/**
 * Created by mani on 3/7/16.
 */
public class ApiGetRequest extends ApiRequest {
    private static final String SLASH = "/";
    public static final long NO_HEADER = -1;

    public ApiGetRequest(String url, ApiResponseListener listener) {
        super(Method.GET, url, null, listener);

        Log.e("[REQUEST]", "GET " + url + "\n\n");
    }

    public ApiGetRequest(String url, Long id, ApiResponseListener listener) {
        super(Method.GET, getUrl(url, id), null, listener);

        Log.e("[REQUEST]", "GET " + getUrl(url, id) + "\n\n");
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

    /********* Added by Suraj *********/
    public ApiGetRequest(String url, String param, ApiResponseListener listener) {
        super(Method.GET, getUrl(url, param), null, listener);

        Log.e("[REQUEST]", "GET " + getUrl(url, param) + "\n\n");
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

    /*********FOR REST API CHANGES by SURAJ M********************/

    public ApiGetRequest(String url, Map<String, String> params, ApiResponseListener listener) {
        super(Method.GET, makeGetRequestWithParams(url,params), null, listener);
    }

    private static String makeGetRequestWithParams(String url, Map<String, String> params) {
        if(params == null)
            return url;

        String urlForGet = "";

        int count = 0;
        for (Map.Entry<String, String> entry : params.entrySet()) {
            String paramName = entry.getKey();
            String paramValue = entry.getValue();
            if(count == 0 && !url.contains("?")) {
                // Add first parameter to url
                urlForGet = "?" + urlForGet + paramName + "=" + paramValue;
            } else {
                // Add another parameter to url
                urlForGet = urlForGet + "&" + paramName + "=" + paramValue;
            }
            count++;
        }

        urlForGet = url + urlForGet;
        Log.e("[REQUEST]", "GET " + urlForGet + "\n\n");
        return urlForGet;
    }

    @Override
    public Map<String, String> getHeaders() throws AuthFailureError {
        Map<String, String>  params = new HashMap<String, String>();
        params.put("Authorization", "Token "+ Aaho.getToken());
        params.put("app-category", "fms");

        return params;
    }

    @Override
    public String getBodyContentType() {
        return "application/json";
    }

}

