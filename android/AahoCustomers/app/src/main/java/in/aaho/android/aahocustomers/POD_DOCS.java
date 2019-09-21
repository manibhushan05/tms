package in.aaho.android.aahocustomers;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.Serializable;
import java.util.ArrayList;

/**
 * Created by aaho on 14/06/18.
 */

public class POD_DOCS implements Serializable {
    private String url;
    private String thumb_url;
    private String lr_number;

    public String getLr_number() {
        return lr_number;
    }

    public void setLr_number(String lr_number) {
        this.lr_number = lr_number;
    }

    public String getUrl() {
        return url;
    }

    public void setUrl(String url) {
        this.url = url;
    }

    public String getThumb_url() {
        return thumb_url;
    }

    public void setThumb_url(String thumb_url) {
        this.thumb_url = thumb_url;
    }

    public static ArrayList<POD_DOCS> getListFromJsonArray(JSONArray jsonArray) {
        ArrayList<POD_DOCS> pod_docsArrayList = new ArrayList<>();
        if(jsonArray !=null && jsonArray.length() != 0) {
            for (int i = 0; i < jsonArray.length(); i++) {
                try {
                    JSONObject jsonObject = (JSONObject) jsonArray.get(i);
                    if(jsonObject != null) {
                        POD_DOCS pod_docs = new POD_DOCS();
                        pod_docs.setUrl(jsonObject.getString("url"));
                        pod_docs.setThumb_url(jsonObject.getString("thumb_url"));
                        pod_docs.setLr_number(jsonObject.getString("lr_number"));
                        pod_docsArrayList.add(pod_docs);
                    }
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            }
        }
        return pod_docsArrayList;
    }
}
