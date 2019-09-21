package in.aaho.android.ownr.requests;

import android.util.Log;

import com.android.volley.AuthFailureError;
import com.google.gson.Gson;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import in.aaho.android.ownr.Aaho;
import in.aaho.android.ownr.common.ApiPostRequest;
import in.aaho.android.ownr.common.ApiResponseListener;
import in.aaho.android.ownr.common.Utils;
import in.aaho.android.ownr.data.PODData;
import in.aaho.android.ownr.docs.Document;

/**
 * Created by suraj
 */
public class PODUploadRequest extends ApiPostRequest {

    // url, thumburl, uuid, bucketname, filename, foldername

    public static final String LR_NUMBER_KEY = "lr_number";

    public PODUploadRequest(String lr_number, String url, String thumbUrl, String bucketname,
                            String foldername, String filename, String uuid, String displayUrl,
                            ArrayList<PODData> podDataArrayList, ApiResponseListener listener) {
        super(Api.UPLOAD_POD_URL, data(lr_number,url,thumbUrl,bucketname,foldername,filename,
                uuid,displayUrl,podDataArrayList), listener);
    }

    private static JSONObject data(String lr_number, String url, String thumbUrl,
                                   String bucketname, String foldername, String filename,
                                   String uuid, String displayUrl, ArrayList<PODData> podDataArrayList) {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put(LR_NUMBER_KEY, lr_number);
            jsonObject.put(Document.URL_KEY, url);
            jsonObject.put(Document.THUMB_URL_KEY, thumbUrl);
            jsonObject.put(Document.BUCKETNAME_KEY, bucketname);
            jsonObject.put(Document.FOLDERNAME_KEY, foldername);
            jsonObject.put(Document.FILENAME_KEY, filename);
            jsonObject.put(Document.UUID_KEY, uuid);
            jsonObject.put(Document.DISPLAY_URL_KEY, displayUrl);
            Gson gson = new Gson();
            String podJsonObject = gson.toJson(podDataArrayList);
            jsonObject.put(Document.POD_DATA_KEY,podJsonObject);
            Log.i("PODUploadRequest","JsonObject = "+jsonObject);
        } catch (JSONException e) {
            Log.e("PODUploadRequest","Error while making podUploadRequest, " +
                    "ex= "+e.getLocalizedMessage());
        }

        return jsonObject;
    }


    @Override
    public Map<String, String> getHeaders() throws AuthFailureError {
        Map<String, String>  params = new HashMap<String, String>();
        params.put("Authorization", "Token "+ Aaho.getToken());

        return params;
    }
}
