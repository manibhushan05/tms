package in.aaho.android.driver.common;

import com.android.volley.Response;
import com.android.volley.VolleyError;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.UnsupportedEncodingException;

/**
 * Created by shobhit on 7/11/16.
 */

public abstract class ApiResponseListener implements Response.Listener<JSONObject>, Response.ErrorListener {

    @Override
    public void onErrorResponse(VolleyError error) {
        error.printStackTrace();
        String errorMsg;
        byte[] errorData = error.networkResponse == null ? null : error.networkResponse.data;
        if (errorData == null || errorData.length == 0) {
            errorMsg = "No response from the server";
        } else {
            try {
                String responseBody = new String(errorData, "utf-8");
                JSONObject jsonObject = new JSONObject(responseBody);
                errorMsg = jsonObject.getString("msg");
            } catch (JSONException e) {
                e.printStackTrace();
                errorMsg = "error decoding error json";
            } catch (UnsupportedEncodingException e){
                e.printStackTrace();
                errorMsg = "unsupported encoding";
            }
        }
        Utils.toast("Error: " + errorMsg);
        onError();
    }

    public void onError() {

    }
}
