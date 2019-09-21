package in.aaho.android.driver.docs;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.driver.common.Utils;

/**
 * Created by shobhit on 26/10/16.
 */

public class Pod {
    public String url = null;
    public String thumbUrl = null;

    private boolean modified = false;

    public boolean notSet() {
        return url == null || url.trim().isEmpty();
    }

    public Pod(String url, String thumbUrl) {
        this.url = url;
        this.thumbUrl = thumbUrl;
    }

    public Pod(String url, String thumbUrl, boolean modified) {
        this.url = url;
        this.thumbUrl = thumbUrl;
        this.modified = modified;
    }

    public boolean isModified() {
        return modified;
    }

    public JSONObject toJson() throws JSONException {
        JSONObject jsonObject = new JSONObject();
        put(jsonObject, "pod", url);
        put(jsonObject, "pod_thumb", url);
        return jsonObject;
    }

    private void put(JSONObject jsonObject, String key, String value) throws JSONException {
        if (value != null) {
            jsonObject.put(key, value);
        }
    }

    public static Pod fromJson(JSONObject jsonObject) throws JSONException {
        if (jsonObject == null) {
            return null;
        }
        Pod pod =  new Pod(
                Utils.get(jsonObject, "pod"),
                Utils.get(jsonObject, "pod_thumb")
        );
        return pod;

    }

    public static Pod copy(Pod other) {
        if (other == null) {
            return null;
        }
        return new Pod(other.url, other.thumbUrl, false);
    }
}
