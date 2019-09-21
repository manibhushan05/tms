package in.aaho.android.aahocustomers.vehicles;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

import in.aaho.android.aahocustomers.booking.City;
import in.aaho.android.aahocustomers.booking.VehicleCategory;
import in.aaho.android.aahocustomers.common.Utils;
import in.aaho.android.aahocustomers.docs.Document;


/**
 * Created by shobhit on 6/8/16.
 */
public class BrokerVehicleDetails {
    public static final String ID_KEY = "id";
    public static final String NUMBER_KEY = "vehicle_number";
    public static final String MODEL_KEY = "vehicle_model";
    public static final String CATEGORY_KEY = "vehicle_type";
    public static final String CATEGORY_DATA_KEY = "vehicle_type_data";
    public static final String NEW_CATEGORY_TYPE_KEY = "new_vehicle_category_type";
    public static final String NEW_CATEGORY_CAPACITY_KEY = "new_vehicle_category_capacity";
    public static final String CITY_KEY = "current_city";
    public static final String STATUS_KEY = "status";
    public static final String OWNER_KEY = "owner";
    public static final String DRIVER_KEY = "driver";
    public static final String ACCOUNT_KEY = "account";

    public static final String RC_DOC_KEY = "rc_doc";
    public static final String INSURANCE_DOC_KEY = "insurance_doc";
    public static final String PERMIT_DOC_KEY = "permit_doc";
    public static final String FITNESS_DOC_KEY = "fitness_doc";
    public static final String PUC_DOC_KEY = "puc_doc";
    public static final String OWNER_PAN_DOC_KEY = "owner_pan_doc";
    public static final String OWNER_DEC_DOC_KEY = "owner_dec_doc";
    public static final String DRIVER_DL_DOC_KEY = "driver_dl_doc";

    public Long id = null;
    private String number;
    public String model;
    public VehicleCategory category;

    public City city;

    public String status;
    public VehicleOwner vehicleOwner;
    public VehicleDriver vehicleDriver;
    public BankAccount account;

    public String newCategoryType = null;
    public String newCategoryCapacity = null;

    public Document rcDoc = null;
    public Document permitDoc = null;
    public Document insuranceDoc = null;
    public Document fitnessDoc = null;
    public Document pucDoc = null;
    public Document ownerPanDoc = null;
    public Document ownerDecDoc = null;
    public Document driverDlDoc = null;


    public BrokerVehicleDetails() {

    }

    public String getName() {
        if (category == null) {
            return null;
        } else {
            return category.getFullName();
        }
    }

    public String getNumber() {
        return VehicleNumber.displayFormat(number);
    }

    public void setNumber(String number) {
        this.number = number;
    }

    public boolean isNotEmpty(Document doc) {
        return doc != null && !doc.notSet();
    }

    public boolean hasDocuments() {
        Document[] docs = new Document[] {
                rcDoc, insuranceDoc, permitDoc, fitnessDoc, pucDoc, ownerDecDoc, ownerPanDoc, driverDlDoc
        };
        for (Document doc : docs) {
            if (isNotEmpty(doc)) {
                return true;
            }
        }
        return account != null && !account.notSet();
    }

    public JSONObject toJson() throws JSONException {
        JSONObject jsonObject = new JSONObject();
        addDoc(jsonObject, RC_DOC_KEY, rcDoc);
        addDoc(jsonObject, INSURANCE_DOC_KEY, insuranceDoc);
        addDoc(jsonObject, PERMIT_DOC_KEY, permitDoc);
        addDoc(jsonObject, FITNESS_DOC_KEY, fitnessDoc);
        addDoc(jsonObject, PUC_DOC_KEY, pucDoc);
        addDoc(jsonObject, OWNER_PAN_DOC_KEY, ownerPanDoc);
        addDoc(jsonObject, OWNER_DEC_DOC_KEY, ownerDecDoc);
        addDoc(jsonObject, DRIVER_DL_DOC_KEY, driverDlDoc);
        addOwner(jsonObject);
        addDriver(jsonObject);
        addAccount(jsonObject);
        addString(jsonObject, NUMBER_KEY, number);
        addString(jsonObject, STATUS_KEY, status);
        addString(jsonObject, MODEL_KEY, model);
        addString(jsonObject, NEW_CATEGORY_TYPE_KEY, newCategoryType);
        addString(jsonObject, NEW_CATEGORY_CAPACITY_KEY, newCategoryCapacity);

        if (city != null) {
            jsonObject.put(CITY_KEY, city.id);
        }
        if (category != null) {
            jsonObject.put(CATEGORY_KEY, category.id);
        }
        if (id != null) {
            jsonObject.put(ID_KEY, id);
        }
        return jsonObject;
    }

    private void addString(JSONObject jsonObject, String key, String value) throws JSONException {
        if (value != null) {
            jsonObject.put(key, value);
        }
    }

    private void addOwner(JSONObject jsonObject) throws JSONException {
        if (vehicleOwner != null) {
            jsonObject.put(OWNER_KEY, vehicleOwner.toJson());
        }
    }

    private void addDriver(JSONObject jsonObject) throws JSONException {
        if (vehicleDriver != null) {
            jsonObject.put(DRIVER_KEY, vehicleDriver.toJson());
        }
    }

    private void addAccount(JSONObject jsonObject) throws JSONException {
        if (account != null) {
            jsonObject.put(ACCOUNT_KEY, account.toJson());
        }
    }

    private void addDoc(JSONObject jsonObject, String key, Document document) throws JSONException {
        if (document != null && document.isModified()) {
            jsonObject.put(key, document.toJson());
        }
    }

    public static BrokerVehicleDetails fromJson(JSONObject jsonObject) throws JSONException {
        BrokerVehicleDetails vehicle = new BrokerVehicleDetails();

        vehicle.id = jsonObject.getLong(ID_KEY);
        vehicle.number = Utils.get(jsonObject, NUMBER_KEY);
        vehicle.model = Utils.get(jsonObject, MODEL_KEY);
        vehicle.status = Utils.get(jsonObject, STATUS_KEY);

        if (jsonObject.has(CATEGORY_DATA_KEY) && !jsonObject.isNull(CATEGORY_DATA_KEY)) {
            JSONObject catData = jsonObject.getJSONObject(CATEGORY_DATA_KEY);
            if (catData.has(CATEGORY_KEY) && !catData.isNull(CATEGORY_KEY)) {
                long catId = jsonObject.getLong(CATEGORY_KEY);
                if (!VehicleCategory.has(catId)) {
                    VehicleCategory.add(catData);
                }
            }
        }

        if (jsonObject.has(CATEGORY_KEY) && !jsonObject.isNull(CATEGORY_KEY)) {
            long catId = jsonObject.getLong(CATEGORY_KEY);
            vehicle.category = VehicleCategory.get(catId);
        }

        if (jsonObject.has(CITY_KEY) && !jsonObject.isNull(CITY_KEY)) {
            long cityId = jsonObject.getLong(CITY_KEY);
            vehicle.city = City.get(cityId);
        }

        if (jsonObject.has(OWNER_KEY) && !jsonObject.isNull(OWNER_KEY)) {
            JSONObject ownerDetails = jsonObject.getJSONObject(OWNER_KEY);
            vehicle.vehicleOwner = VehicleOwner.fromJson(ownerDetails);
        }

        if (jsonObject.has(DRIVER_KEY) && !jsonObject.isNull(DRIVER_KEY)) {
            JSONObject driverDetails = jsonObject.getJSONObject(DRIVER_KEY);
            vehicle.vehicleDriver = VehicleDriver.fromJson(driverDetails);
        }

        if (jsonObject.has(ACCOUNT_KEY) && !jsonObject.isNull(ACCOUNT_KEY)) {
            JSONObject accountDetails = jsonObject.getJSONObject(ACCOUNT_KEY);
            vehicle.account = BankAccount.fromJson(accountDetails);
        }

        if (jsonObject.has(RC_DOC_KEY) && !jsonObject.isNull(RC_DOC_KEY)) {
            JSONObject docObj = jsonObject.getJSONObject(RC_DOC_KEY);
            vehicle.rcDoc = Document.fromJson(docObj, Document.RC_DOC_TYPE);
        }

        if (jsonObject.has(PERMIT_DOC_KEY) && !jsonObject.isNull(PERMIT_DOC_KEY)) {
            JSONObject docObj = jsonObject.getJSONObject(PERMIT_DOC_KEY);
            vehicle.permitDoc = Document.fromJson(docObj, Document.PERMIT_DOC_TYPE);
        }

        if (jsonObject.has(INSURANCE_DOC_KEY) && !jsonObject.isNull(INSURANCE_DOC_KEY)) {
            JSONObject docObj = jsonObject.getJSONObject(INSURANCE_DOC_KEY);
            vehicle.insuranceDoc = Document.fromJson(docObj, Document.INSURANCE_DOC_TYPE);
        }

        if (jsonObject.has(FITNESS_DOC_KEY) && !jsonObject.isNull(FITNESS_DOC_KEY)) {
            JSONObject docObj = jsonObject.getJSONObject(FITNESS_DOC_KEY);
            vehicle.fitnessDoc = Document.fromJson(docObj, Document.FITNESS_DOC_TYPE);
        }

        if (jsonObject.has(PUC_DOC_KEY) && !jsonObject.isNull(PUC_DOC_KEY)) {
            JSONObject docObj = jsonObject.getJSONObject(PUC_DOC_KEY);
            vehicle.pucDoc = Document.fromJson(docObj, Document.PUC_DOC_TYPE);
        }

        if (jsonObject.has(OWNER_PAN_DOC_KEY) && !jsonObject.isNull(OWNER_PAN_DOC_KEY)) {
            JSONObject docObj = jsonObject.getJSONObject(OWNER_PAN_DOC_KEY);
            vehicle.ownerPanDoc = Document.fromJson(docObj, Document.PAN_DOC_TYPE);
        }

        if (jsonObject.has(OWNER_DEC_DOC_KEY) && !jsonObject.isNull(OWNER_DEC_DOC_KEY)) {
            JSONObject docObj = jsonObject.getJSONObject(OWNER_DEC_DOC_KEY);
            vehicle.ownerDecDoc = Document.fromJson(docObj, Document.DEC_DOC_TYPE);
        }

        if (jsonObject.has(DRIVER_DL_DOC_KEY) && !jsonObject.isNull(DRIVER_DL_DOC_KEY)) {
            JSONObject docObj = jsonObject.getJSONObject(DRIVER_DL_DOC_KEY);
            vehicle.driverDlDoc = Document.fromJson(docObj, Document.DL_DOC_TYPE);
        }

        return vehicle;
    }


    public static BrokerVehicleDetails copy(BrokerVehicleDetails other) {
        if (other == null) {
            return null;
        }
        BrokerVehicleDetails details = new BrokerVehicleDetails();
        details.id = other.id;
        details.number = other.number;
        details.model = other.model;
        details.category = other.category;

        details.city = other.city;

        details.status = other.status;
        details.vehicleOwner = VehicleOwner.copy(other.vehicleOwner);
        details.vehicleDriver = VehicleDriver.copy(other.vehicleDriver);
        details.account = BankAccount.copy(other.account);

        details.rcDoc = Document.copy(other.rcDoc);
        details.permitDoc = Document.copy(other.permitDoc);
        details.insuranceDoc = Document.copy(other.insuranceDoc);
        details.fitnessDoc = Document.copy(other.fitnessDoc);
        details.pucDoc = Document.copy(other.pucDoc);
        details.ownerPanDoc = Document.copy(other.ownerPanDoc);
        details.ownerDecDoc = Document.copy(other.ownerDecDoc);
        details.driverDlDoc = Document.copy(other.driverDlDoc);
        return details;
    }

    public List<DocDetail> getDocDetailsList() {
        List<DocDetail> docDetails = new ArrayList<>();
        addIfNeeded(docDetails, "rc", rcDoc);
        addIfNeeded(docDetails, "in", insuranceDoc);
        addIfNeeded(docDetails, "perm", permitDoc);
        addIfNeeded(docDetails, "fit", fitnessDoc);
        addIfNeeded(docDetails, "puc", pucDoc);
        addIfNeeded(docDetails, "pan", ownerPanDoc);
        addIfNeeded(docDetails, "dec", ownerDecDoc);
        addIfNeeded(docDetails, "dl", driverDlDoc);

        if (account != null && !account.notSet()) {
            docDetails.add(new DocDetail("ac", "Bank Account", account.title(), true));
        }

        return docDetails;
    }

    private void addIfNeeded(List<DocDetail> docDetails, String type, Document doc) {
        DocDetail detail = getDocDetail(doc, type);
        if (detail != null) {
            docDetails.add(detail);
        }
    }

    private DocDetail getDocDetail(Document doc, String type) {
        return doc == null ? null : new DocDetail(type, doc.type, doc.id == null ? "" : doc.id, true);
    }
}
