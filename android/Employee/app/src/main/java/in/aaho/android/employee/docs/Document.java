package in.aaho.android.employee.docs;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.Date;

import in.aaho.android.employee.common.Utils;

/**
 * Created by mani on 26/10/16.
 */

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
    public static final String DOCUMENT_CATEGORY_KEY = "document_category";

    public String filename;
    public String foldername;
    public String bucketname;
    public String uuid;
    public String displayUrl;
    public String docCategory;

    public boolean notSet() {
        return (url == null || url.trim().isEmpty()) && (id == null || id.trim().isEmpty());
    }

    public Document(String url, String thumbUrl, String id, Date validity, String type,
                    String bucketname, String foldername, String filename, String uuid,
                    String displayUrl, String docCategory) {
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
        this.docCategory = docCategory;
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
                Utils.get(jsonObject,DISPLAY_URL_KEY),
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

    public static Document fromJsonObject(JSONObject jsonObjectData, JSONObject jsonObjectDoc,
                                          String type, String docCategory) throws JSONException {
        if (jsonObjectDoc == null) {
            return null;
        }

        Date validity = null;
        String name = "";
        String insuranceNumber = "";
        if (docCategory.equalsIgnoreCase("REG")) {
            validity = Utils.parseShipmentDate(Utils.get(jsonObjectData,"registration_validity"));
        } else if (docCategory.equalsIgnoreCase("INS")) {
            validity = Utils.parseShipmentDate(Utils.get(jsonObjectData,"insurance_validity"));
            name = Utils.get(jsonObjectData,"insurance_number");
        } else if (docCategory.equalsIgnoreCase("PERM")) {
            validity = Utils.parseShipmentDate(Utils.get(jsonObjectData,"permit_validity"));
            name = Utils.get(jsonObjectData,"permit");
        } else if (docCategory.equalsIgnoreCase("FIT")) {
            validity = Utils.parseShipmentDate(Utils.get(jsonObjectData,"fitness_certificate_validity_date"));
            name = Utils.get(jsonObjectData,"fitness_certificate_number");
        } else if (docCategory.equalsIgnoreCase("PUC")) {
            validity = Utils.parseShipmentDate(Utils.get(jsonObjectData,"puc_certificate_validity_date"));
            name = Utils.get(jsonObjectData,"puc_certificate_number");
        } else if (docCategory.equalsIgnoreCase("PAN")) {
            JSONObject ownerPanData = jsonObjectData.getJSONObject("owner_data");
            name = Utils.get(ownerPanData,"pan");
        } else if (docCategory.equalsIgnoreCase("DEC")) {
            JSONObject ownerPanData = jsonObjectData.getJSONObject("owner_data");
            validity = Utils.parseShipmentDate(Utils.get(ownerPanData,"declaration_validity"));
        } else if (docCategory.equalsIgnoreCase("DL")) {
            JSONObject driverData = jsonObjectData.getJSONObject("driver_data");
            name = Utils.get(driverData,"dl_number");
            validity = Utils.parseShipmentDate(Utils.get(driverData,"dl_validity"));
        } else {
            // do nothing
        }

        Document document =  new Document(
                Utils.get(jsonObjectDoc, URL_KEY),
                Utils.get(jsonObjectDoc, THUMB_URL_KEY),
                /*Utils.get(jsonObjectDoc, "id"),*/
                name,
                /*Utils.getDate(jsonObjectDoc, "validity"),*/
                validity,
                type,
                Utils.get(jsonObjectDoc,"bucket"),
                Utils.get(jsonObjectDoc,"folder"),
                Utils.get(jsonObjectDoc,"filename"),
                Utils.get(jsonObjectDoc,UUID_KEY),
                Utils.get(jsonObjectDoc,URL_KEY),
                Utils.get(jsonObjectDoc,DOCUMENT_CATEGORY_KEY)
        );

        if (jsonObjectData.has("registration_year")) {
            document.manufactureYear = Utils.get(jsonObjectData, "registration_year");
        }
        if (jsonObjectData.has("insurer")) {
            document.insurerName = Utils.get(jsonObjectData, "insurer");
        }

        if(jsonObjectData.has("driver_data")) {
            JSONObject driverData = jsonObjectData.getJSONObject("driver_data");
            if (driverData.has("dl_location")) {
                document.issueLocation = Utils.get(driverData, "dl_location");
            }
        }
        /*if (jsonObjectData.has("issue_location")) {
            document.issueLocation = Utils.get(jsonObjectData, "issue_location");
        }*/

        if (jsonObjectData.has("permit_type")) {
            document.permitType = Utils.get(jsonObjectData, "permit_type");
        }

        return document;

    }

    public static Document fromJsonObjectDriver(JSONObject jsonObjectData, JSONObject jsonObjectDoc,
                                                String type, String docCategory) throws JSONException {
        if (jsonObjectDoc == null) {
            return null;
        }

        Date validity = null;
        String name = "";
        String insuranceNumber = "";
        if (docCategory.equalsIgnoreCase("PAN")) {
            name = Utils.get(jsonObjectData,"pan");
        } else if (docCategory.equalsIgnoreCase("DL")) {
            name = Utils.get(jsonObjectData,"driving_licence_number");
            validity = Utils.parseShipmentDate(Utils.get(jsonObjectData,"driving_licence_validity"));
        } else {
            // do nothing
        }

        Document document =  new Document(
                Utils.get(jsonObjectDoc, URL_KEY),
                Utils.get(jsonObjectDoc, THUMB_URL_KEY),
                /*Utils.get(jsonObjectDoc, "id"),*/
                name,
                /*Utils.getDate(jsonObjectDoc, "validity"),*/
                validity,
                type,
                Utils.get(jsonObjectDoc,"bucket"),
                Utils.get(jsonObjectDoc,"folder"),
                Utils.get(jsonObjectDoc,"filename"),
                Utils.get(jsonObjectDoc,UUID_KEY),
                Utils.get(jsonObjectDoc,URL_KEY),
                Utils.get(jsonObjectDoc,DOCUMENT_CATEGORY_KEY)
        );

        return document;

    }


    public static Document fromProfileJsonObject(JSONObject jsonObjectData, JSONObject jsonObjectDoc,
                                                 String type, String docCategory) throws JSONException {
        if (jsonObjectDoc == null) {
            return null;
        }

        Date validity = null;
        String name = "";
        String insuranceNumber = "";
        if (docCategory.equalsIgnoreCase("PAN")) {
            JSONObject user = jsonObjectData.getJSONObject("user");
            name = Utils.get(user,"pan");
        } else if (docCategory.equalsIgnoreCase("DEC")) {
            JSONObject user = jsonObjectData.getJSONObject("user");
            validity = Utils.parseShipmentDate(Utils.get(user,"declaration_validity"));
        } else {
            // do nothing
        }

        Document document =  new Document(
                Utils.get(jsonObjectDoc, URL_KEY),
                Utils.get(jsonObjectDoc, THUMB_URL_KEY),
                /*Utils.get(jsonObjectDoc, "id"),*/
                name,
                /*Utils.getDate(jsonObjectDoc, "validity"),*/
                validity,
                type,
                Utils.get(jsonObjectDoc,"bucket"),
                Utils.get(jsonObjectDoc,"folder"),
                Utils.get(jsonObjectDoc,"filename"),
                Utils.get(jsonObjectDoc,UUID_KEY),
                Utils.get(jsonObjectDoc,URL_KEY),
                Utils.get(jsonObjectDoc,DOCUMENT_CATEGORY_KEY)
        );

        return document;

    }
}
