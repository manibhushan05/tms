package in.aaho.android.aahocustomers.docs;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.Date;

import in.aaho.android.aahocustomers.common.Utils;

public class Document {
    public static final String RC_DOC_TYPE = "Registration Certificate";
    public static final String INSURANCE_DOC_TYPE = "Insurance";
    public static final String PERMIT_DOC_TYPE = "Permit";
    public static final String FITNESS_DOC_TYPE = "Fitness Certificate";
    public static final String PUC_DOC_TYPE = "PUC Certificate";
    public static final String PAN_DOC_TYPE = "PAN Card";
    public static final String DEC_DOC_TYPE = "Declaration";
    public static final String DL_DOC_TYPE = "Driver's Licence";

    public String id = null;
    public String url = null;
    public String thumbUrl = null;
    public Date validity = null;
    public String type;

    public String manufactureYear = null;
    public String insurerName = null;
    public String issueLocation = null;
    public String permitType = null;

    private boolean modified = false;


    //added by suraj.m
    public static final String URL_KEY = "url";
    public static final String THUMB_URL_KEY = "thumb_url";
    public static final String FILENAME_KEY = "fileName";
    public static final String BUCKETNAME_KEY = "bucketName";
    public static final String FOLDERNAME_KEY = "folderName";
    public static final String UUID_KEY = "uuid";
    public static final String DISPLAY_URL_KEY = "displayUrl";
    public static final String POD_DATA_KEY = "podData";

    public String filename;
    public String foldername;
    public String bucketname;
    public String uuid;
    public String displayUrl;

    public boolean notSet() {
        return (url == null || url.trim().isEmpty()) && (id == null || id.trim().isEmpty());
    }

    public Document(String url, String thumbUrl, String id, Date validity, String type,
                    String bucketname, String foldername, String filename, String uuid,
                    String displayUrl) {
        this.url = url;
        this.thumbUrl = thumbUrl;
        this.type = type;
        this.id = id;
        this.validity = validity;

        this.bucketname = bucketname;
        this.foldername = foldername;
        this.filename = filename;
        this.uuid = uuid;
        this.displayUrl = displayUrl;
    }

    public Document(String url, String thumbUrl, String id, Date validity, String type,
                    String manufactureYear, String insurerName, String issueLocation,
                    String permitType, boolean modified,
                    String bucketname, String foldername, String filename,
                    String uuid, String displayUrl) {
        this.url = url;
        this.thumbUrl = thumbUrl;
        this.type = type;
        this.id = id;
        this.validity = validity;
        this.manufactureYear = manufactureYear;
        this.insurerName = insurerName;
        this.issueLocation = issueLocation;
        this.permitType = permitType;
        this.modified = modified;

        this.bucketname = bucketname;
        this.foldername = foldername;
        this.filename = filename;
        this.uuid = uuid;
        this.displayUrl = displayUrl;
    }

    public boolean isModified() {
        return modified;
    }

    public JSONObject toJson() throws JSONException {
        JSONObject jsonObject = new JSONObject();
        put(jsonObject, URL_KEY, url);
        put(jsonObject, THUMB_URL_KEY, thumbUrl);
        put(jsonObject, "doc_id", id);
        put(jsonObject, "validity", Utils.jsonFormatDate(validity));
        put(jsonObject, "manufacture_year", manufactureYear);
        put(jsonObject, "insurer_name", insurerName);
        put(jsonObject, "issue_location", issueLocation);
        put(jsonObject, "permit_type", permitType);

        put(jsonObject, BUCKETNAME_KEY, bucketname);
        put(jsonObject, FOLDERNAME_KEY, foldername);
        put(jsonObject, FILENAME_KEY, filename);
        put(jsonObject, UUID_KEY, uuid);
        put(jsonObject, DISPLAY_URL_KEY, displayUrl);

        return jsonObject;
    }

    private void put(JSONObject jsonObject, String key, String value) throws JSONException {
        if (value != null) {
            jsonObject.put(key, value);
        }
    }

    public static Document fromJson(JSONObject jsonObject, String type) throws JSONException {
        if (jsonObject == null) {
            return null;
        }
        Document document =  new Document(
                Utils.get(jsonObject, URL_KEY),
                Utils.get(jsonObject, THUMB_URL_KEY),
                Utils.get(jsonObject, "doc_id"),
                Utils.getDate(jsonObject, "validity"),
                type,
                Utils.get(jsonObject,BUCKETNAME_KEY),
                Utils.get(jsonObject,FOLDERNAME_KEY),
                Utils.get(jsonObject,FILENAME_KEY),
                Utils.get(jsonObject,UUID_KEY),
                Utils.get(jsonObject,DISPLAY_URL_KEY)
        );
        if (jsonObject.has("manufacture_year")) {
            document.manufactureYear = Utils.get(jsonObject, "manufacture_year");
        }
        if (jsonObject.has("insurer_name")) {
            document.insurerName = Utils.get(jsonObject, "insurer_name");
        }
        if (jsonObject.has("issue_location")) {
            document.issueLocation = Utils.get(jsonObject, "issue_location");
        }
        if (jsonObject.has("permit_type")) {
            document.permitType = Utils.get(jsonObject, "permit_type");
        }
        return document;

    }

    public static Document copy(Document other) {
        if (other == null) {
            return null;
        }
        return new Document(
                other.url, other.thumbUrl, other.id, other.validity, other.type,
                other.manufactureYear, other.insurerName, other.issueLocation,
                other.permitType, false,
                other.bucketname,other.foldername,other.filename,other.uuid,other.displayUrl
        );
    }

    public String text() {
        if (notSet()) {
            return null;
        }
        String idText = "";
        if (!Utils.not(id)) {
            idText = " - " + id.trim();
        }
        return type + idText;
    }
}
