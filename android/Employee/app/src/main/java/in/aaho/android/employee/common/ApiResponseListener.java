package in.aaho.android.employee.common;

import org.json.JSONException;
import org.json.JSONObject;

import com.android.volley.Response;
import com.android.volley.VolleyError;

import java.io.UnsupportedEncodingException;

/**
 * Created by aaho on 18/04/18.
 */

public abstract class ApiResponseListener implements Response.Listener<JSONObject>, Response.ErrorListener {

    @Override
    public void onErrorResponse(VolleyError error) {
        error.printStackTrace();
        String errorMsg = null;
        byte[] errorData = error.networkResponse == null ? null : error.networkResponse.data;
        if (errorData == null || errorData.length == 0) {
            errorMsg = "No response from the server";
        } else {
            try {
                String responseBody = new String(errorData, "utf-8");
                JSONObject jsonObject = new JSONObject(responseBody);
                if(jsonObject != null)
                    errorMsg = jsonObject.getString("msg");
            } catch (JSONException e) {
                e.printStackTrace();
                errorMsg = "error decoding error json";
            } catch (UnsupportedEncodingException e){
                e.printStackTrace();
                errorMsg = "unsupported encoding";
            }
        }
        //Utils.toast("Message : " + errorMsg);
        onError();
    }

    public void onError() {

    }
}

