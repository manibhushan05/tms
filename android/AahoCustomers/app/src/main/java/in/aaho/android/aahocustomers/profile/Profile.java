package in.aaho.android.aahocustomers.profile;

import android.text.TextUtils;
import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.aahocustomers.booking.UserAddress;
import in.aaho.android.aahocustomers.common.Utils;
import in.aaho.android.aahocustomers.docs.Document;

/**
 * Created by shobhit on 25/11/16.
 */

public class Profile {
    public static final String PAN_DOC_KEY = "pan_doc";
    public static final String DEC_DOC_KEY = "dec_doc";
    public static final String CITY_ID_KEY = "city_id";
    public static final String CITY_NAME_KEY = "city_name";

    public String userFullName, username, userPhone, userEmail,
            userDesignation, userContactName, mCityId, mCityName;
    public Long userId;

    public Document panDoc;
    public Document decDoc;

    public final UserAddress address = new UserAddress();


    public static Profile fromJson(JSONObject user) throws JSONException {
        Profile profile = new Profile();

        Log.e("[user_data]", user.toString());
        profile.userFullName = nullToBlank(user.getString("full_name"));
        profile.userContactName = nullToBlank(user.getString("contact_name"));
        profile.username = nullToBlank(user.getString("username"));
        profile.userPhone = nullToBlank(user.getString("phone"));
        profile.userEmail = nullToBlank(user.getString("email"));
        profile.userDesignation = nullToBlank(user.getString("designation"));
        profile.userId = user.getLong("id");
        // to get the city name
        profile.mCityId = user.optString(CITY_ID_KEY);
        profile.mCityName = user.optString(CITY_NAME_KEY);

        if (user.has("address") && !user.isNull("address")) {
            JSONObject addressObj = user.getJSONObject("address");
            profile.address.updateAddress(addressObj);
        }

        if (user.has(PAN_DOC_KEY) && !user.isNull(PAN_DOC_KEY)) {
            JSONObject docObj = user.getJSONObject(PAN_DOC_KEY);
            profile.panDoc = Document.fromJson(docObj, Document.PAN_DOC_TYPE);
        }

        if (user.has(DEC_DOC_KEY) && !user.isNull(DEC_DOC_KEY)) {
            JSONObject docObj = user.getJSONObject(DEC_DOC_KEY);
            profile.decDoc = Document.fromJson(docObj, Document.DEC_DOC_TYPE);
        }

        return profile;
    }

    private void update(String mUserFullName, String mUserContactName, String mUsername,
                        String mUserPhone, String mUserEmail, String mUserDesignation,
                        Long mUserId, String cityId) {
        userFullName = mUserFullName;
        userContactName = mUserContactName;
        username = mUsername;
        userPhone = mUserPhone;
        userEmail = mUserEmail;
        userDesignation = mUserDesignation;
        userId = mUserId;
        mCityId = cityId;
    }

    public static String nullToBlank(String str) {
        if (str == null) {
            return "";
        } else {
            return str.trim();
        }
    }

    public JSONObject getUpdatedUserProfileJson(String name, String contactName,
                                                String contactPhone, String contactEmail,
                                                String contactDesignation,
                                                String newAddress,
                                                String cityId) throws JSONException {
        JSONObject jsonObject = new JSONObject();
        if (!Utils.equals(userFullName, name)) {
            jsonObject.put("full_name", name == null ? JSONObject.NULL : name);
        }
        if (!Utils.equals(userContactName, contactName)) {
            jsonObject.put("contact_name", contactName == null ? JSONObject.NULL : contactName);
        }
        if (!Utils.equals(userPhone, contactPhone)) {
            jsonObject.put("phone", contactPhone == null ? JSONObject.NULL : contactPhone);
        }
        if (!Utils.equals(userEmail, contactEmail)) {
            jsonObject.put("email", contactEmail == null ? JSONObject.NULL : contactEmail);
        }
        if (!Utils.equals(userDesignation, contactDesignation)) {
            jsonObject.put("designation", contactDesignation == null ? JSONObject.NULL : contactDesignation);
        }
        if (!Utils.equals(mCityId, cityId)) {
            jsonObject.put(CITY_ID_KEY, cityId == null ? JSONObject.NULL : cityId);
        }

        if (!TextUtils.isEmpty(newAddress)) {
            address.setPin("");
            address.setLine1(newAddress);
            address.setLine2("");
            address.setLine3("");
            address.setCity(null);
            address.setLandmark("");
        }

        if (!address.isSynced()) {
            jsonObject.put("address", address.toJson());
        }
        addDoc(jsonObject, PAN_DOC_KEY, panDoc);
        addDoc(jsonObject, DEC_DOC_KEY, decDoc);

        return jsonObject;
    }

    private void addDoc(JSONObject jsonObject, String key, Document document) throws JSONException {
        if (document != null && document.isModified()) {
            jsonObject.put(key, document.toJson());
        }
    }

    public void clear() {
        update(null, null, null, null,
                null, null, null, null);
        address.clear();
        panDoc = null;
        decDoc = null;
    }
}
