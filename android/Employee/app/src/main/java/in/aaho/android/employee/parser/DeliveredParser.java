package in.aaho.android.employee.parser;

import android.text.TextUtils;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

import in.aaho.android.employee.common.Utils;
import in.aaho.android.employee.other.POD_DOCS;

public class DeliveredParser {

    public Integer id;
    public String bookingId;
    public String customerName;
    public Integer fromCityId;
    public Integer toCityId;
    public String fromCity;
    public String toCity;
    public String bookingStatusCurrent;
    public boolean bookingStatusCurrentOverdue;
    public String primarySucceededBookingStatus;
    public String bookingStatusComment;
    public String bookingStatusCommentCreatedOn;
    public String vehicleNumber;
    public String vehicleType;
    public Integer vehicleId;
    public Integer bookingStatusMappingId;
    public String lrNumber;
    public Double weight;
    public Double rate;
    public String podStatus;
    public String dueDate;
    public String supplierPhone;
    public Integer bookingStatusMappingChainId;
    private ArrayList<POD_DOCS> pod_docsArrayList;

    private static final String KEY_ID = "id";
    private static final String KEY_BOOKING_ID = "booking_id";
    private static final String KEY_CUSTOMER_NAME = "name";
    private static final String KEY_FROM_CITY = "from_city_fk_data";
    private static final String KEY_TO_CITY = "to_city_fk_data";
    private static final String KEY_FROM_CITY_ID = "from_city_id";
    private static final String KEY_TO_CITY_ID = "to_city_id";
    private static final String KEY_BOOKING_STATUS_CURRENT = "booking_status_current";
    private static final String KEY_PRIMARY_SUCCEEDED_BOOKING_STATUS = "primary_succeeded_booking_status";
    private static final String KEY_BOOKING_STATUS_COMMENT = "booking_status_comment";
    private static final String KEY_BOOKING_STATUS_COMMENT_CREATED_ON = "booking_status_comment_created_on";
    private static final String KEY_VEHICLE_TYPE = "type";
    /*private static final String KEY_VEHICLE_NUMBER = "lorry_number";*/
    private static final String KEY_VEHICLE_NUMBER = "vehicle_number";
    private static final String KEY_TYPE_OF_VEHICLE = "type_of_vehicle";
    private static final String KEY_TYPE_OF_VEHICLE_ID = "type_of_vehicle_id";
    private static final String KEY_BOOKING_STATUS_MAPPING_ID = "booking_status_mapping_id";

    private static final String KEY_OBJECT_CUSTOMER_PLACED_ORDER_DATA = "customer_placed_order_data";
    private static final String KEY_OBJECT_BOOKING_STATUS_DETAILS = "booking_status_details";
    private static final String KEY_OBJECT_VEHICLE_DATA = "vehicle_data";
    private static final String KEY_OBJECT_VEHICLE_CATEGORY_DATA = "vehicle_category_data";
    private static final String KEY_LRNUMBER = "lr_numbers";
    private static final String KEY_WEIGHT = "charged_weight";
    private static final String KEY_RATE = "party_rate";
    private static final String KEY_DUE_DATE = "due_date";
    private static final String KEY_POD_STATUS = "pod_status";
    private static final String KEY_POD_DATA = "pod_data";
    private static final String KEY_OBJECT_SUPPLIER_DATA = "supplier_data";
    private static final String KEY_SUPPLIER_PHONE = "phone";
    private static final String KEY_BOOKING_STATUS_CURRENT_OVERDUE = "current_status_overdue";
    private static final String KEY_BOOKING_STATUS_MAPPING_CHAIN_ID = "booking_status_mapping_chain_id";

    public DeliveredParser(Integer id, String bookingId, String customerName,
                           Integer fromCityId, Integer toCityId, String fromCity,
                           String toCity, String bookingStatusCurrent, String primarySucceededBookingStatus,
                           String bookingStatusComment, String bookingStatusCommentCreatedOn,
                           String vehicleNumber, String vehicleType, Integer vehicleId, Integer bookingStatusMappingId,
                           String lrNumber, Double weight, Double rate, String podStatus, String due_date,
                           String supplierPhone, ArrayList<POD_DOCS> pod_docsArrayList, boolean bookingStatusCurrentOverdue,
                           Integer bookingStatusMappingChainId) {
        this.id = id;
        this.bookingId = bookingId;
        this.customerName = customerName;
        this.fromCityId = fromCityId;
        this.toCityId = toCityId;
        this.fromCity = fromCity;
        this.toCity = toCity;
        this.bookingStatusCurrent = bookingStatusCurrent;
        this.primarySucceededBookingStatus = primarySucceededBookingStatus;
        this.bookingStatusComment = bookingStatusComment;
        this.bookingStatusCommentCreatedOn = bookingStatusCommentCreatedOn;
        this.vehicleNumber = vehicleNumber;
        this.vehicleType = vehicleType;
        this.vehicleId = vehicleId;
        this.bookingStatusMappingId = bookingStatusMappingId;
        this.lrNumber = lrNumber;
        this.weight = weight;
        this.rate = rate;
        this.podStatus = podStatus;
        this.dueDate = due_date;
        this.supplierPhone = supplierPhone;
        this.pod_docsArrayList = pod_docsArrayList;
        this.bookingStatusCurrentOverdue = bookingStatusCurrentOverdue;
        this.bookingStatusMappingChainId = bookingStatusMappingChainId;
    }

    public static DeliveredParser fromJson(JSONObject jsonObject) throws JSONException {
        if (jsonObject == null || jsonObject.length() == 0) {
            return null;
        }

        String customerName = "";
        String vehicleType = "";
        String vehicleNumber = "";
        String bookingStatusCurrent = "";
        String primarySucceededBookingStatus = "";
        String bookingStatusComment = "";
        String bookingStatusCommentCreatedOn = "";
        String dueDate = "";
        Integer bookingStatusMappingId = null;
        Integer bookingStatusMappingChainId = null;
        String supplierPhone = "";
        boolean booking_status_overdue = true;

        // Retrieve customer name
        JSONObject customerPlacedOrderData = getObject(jsonObject,KEY_OBJECT_CUSTOMER_PLACED_ORDER_DATA);
        if(customerPlacedOrderData != null) {
            customerName = Utils.get(customerPlacedOrderData, KEY_CUSTOMER_NAME);
        }
        // Retrieve various booking status
        JSONObject bookingStatusDetail = getObject(jsonObject,KEY_OBJECT_BOOKING_STATUS_DETAILS);
        if(bookingStatusDetail != null) {
            bookingStatusCurrent = Utils.get(bookingStatusDetail, KEY_BOOKING_STATUS_CURRENT);
            primarySucceededBookingStatus = Utils.get(bookingStatusDetail, KEY_PRIMARY_SUCCEEDED_BOOKING_STATUS);
            bookingStatusComment = Utils.get(bookingStatusDetail, KEY_BOOKING_STATUS_COMMENT);
            bookingStatusCommentCreatedOn = Utils.get(bookingStatusDetail, KEY_BOOKING_STATUS_COMMENT_CREATED_ON);
            bookingStatusMappingId = Utils.getInteger(bookingStatusDetail, KEY_BOOKING_STATUS_MAPPING_ID) == null
                    ? null : Utils.getInteger(bookingStatusDetail, KEY_BOOKING_STATUS_MAPPING_ID);
            bookingStatusMappingChainId = Utils.getInteger(bookingStatusDetail, KEY_BOOKING_STATUS_MAPPING_CHAIN_ID) == null
                    ? null : Utils.getInteger(bookingStatusDetail, KEY_BOOKING_STATUS_MAPPING_CHAIN_ID);
            String booking_status_overdue_string = Utils.get(bookingStatusDetail, KEY_BOOKING_STATUS_CURRENT_OVERDUE);
            booking_status_overdue = TextUtils.isEmpty(booking_status_overdue_string) || booking_status_overdue_string.equalsIgnoreCase("true");
            dueDate = Utils.get(bookingStatusDetail, KEY_DUE_DATE);

        }
        // Retrieve vehicle number
        /*vehicleNumber = Utils.get(jsonObject,KEY_VEHICLE_NUMBER).toUpperCase();*/
        JSONObject vehicleData = getObject(jsonObject,KEY_OBJECT_VEHICLE_DATA);
        if(vehicleData != null) {
            vehicleNumber = Utils.get(vehicleData,KEY_VEHICLE_NUMBER);
        }
        // Retrieve vehicle type
        JSONObject vehicleCategoryData = getObject(jsonObject,KEY_OBJECT_VEHICLE_CATEGORY_DATA);
        if(vehicleCategoryData != null) {
            vehicleType = Utils.get(vehicleCategoryData,KEY_VEHICLE_TYPE);
        }

        // Retrieve driver contact number
        JSONObject driverData = getObject(jsonObject, KEY_OBJECT_SUPPLIER_DATA);
        if(driverData != null) {
            supplierPhone = Utils.get(driverData, KEY_SUPPLIER_PHONE);
        }

        String lrList = "";
        if(jsonObject.has(KEY_LRNUMBER)) {
            // Retrieve LR numbers
            JSONArray jsonLRNumbers = jsonObject.getJSONArray(KEY_LRNUMBER);
            for (int j = 0; j < jsonLRNumbers.length(); j++) {
                if (TextUtils.isEmpty(lrList)) {
                    lrList = jsonLRNumbers.getJSONObject(j)
                            .getString("lr_number");
                } else {
                    lrList = lrList + "\n" + jsonLRNumbers.getJSONObject(j)
                            .getString("lr_number");
                }
            }
        }

        // get from city
        String fromCity = "";
        if(jsonObject != null && jsonObject.has(KEY_FROM_CITY)) {
            JSONObject fromVehicleData = jsonObject.getJSONObject(KEY_FROM_CITY);
            if (fromVehicleData!=null && fromVehicleData.has("name")) {
                fromCity = Utils.get(fromVehicleData,"name");
            }
        }

        // get to city
        String toCity = "";
        if(jsonObject != null && jsonObject.has(KEY_TO_CITY)) {
            JSONObject toVehicleData = jsonObject.getJSONObject(KEY_TO_CITY);
            if (toVehicleData!=null && toVehicleData.has("name")) {
                toCity = Utils.get(toVehicleData,"name");
            }
        }

        // set pod data
        ArrayList<POD_DOCS> pod_docsArrayList;
        if(jsonObject.has(KEY_POD_DATA)) {
            pod_docsArrayList = POD_DOCS.getListFromJsonArray(
                            jsonObject.getJSONArray(KEY_POD_DATA));
        } else {
            pod_docsArrayList = null;
        }

        return new DeliveredParser(
                Utils.getInteger(jsonObject, KEY_ID),
                Utils.get(jsonObject, KEY_BOOKING_ID),
                customerName,
                Utils.getInteger(jsonObject, KEY_FROM_CITY_ID) == null ? null : Utils.getInteger(jsonObject, KEY_FROM_CITY_ID),
                Utils.getInteger(jsonObject, KEY_TO_CITY_ID) == null ? null : Utils.getInteger(jsonObject, KEY_TO_CITY_ID),
                fromCity,
                toCity,
                bookingStatusCurrent,
                primarySucceededBookingStatus,
                bookingStatusComment,
                bookingStatusCommentCreatedOn,
                vehicleNumber,
                vehicleType,
                Utils.getInteger(jsonObject, KEY_TYPE_OF_VEHICLE_ID),
                bookingStatusMappingId,
                lrList,
                Utils.getDouble(jsonObject, KEY_WEIGHT),
                Utils.getDouble(jsonObject, KEY_RATE),
                Utils.get(jsonObject, KEY_POD_STATUS),
                dueDate,
                supplierPhone,
                pod_docsArrayList,
                booking_status_overdue,
                bookingStatusMappingChainId
        );
    }

    private static JSONObject getObject(JSONObject jsonObject, String key) {
        if (jsonObject == null || jsonObject.length() == 0) {
            return null;
        }
        if (!jsonObject.has(key) || jsonObject.isNull(key)) {
            return null;
        }
        try {
            return jsonObject.getJSONObject(key);
        } catch (JSONException e) {
            return null;
        }
    }

    public static List<DeliveredParser> fromJson(JSONArray jsonArray) throws JSONException {
        List<DeliveredParser> pendingLRParserArrayList = new ArrayList<>();
        for (int i = 0; i < jsonArray.length(); i++) {
            JSONObject obj = jsonArray.getJSONObject(i);
            DeliveredParser pendingLRParser = fromJson(obj);
            pendingLRParserArrayList.add(pendingLRParser);
        }

        return pendingLRParserArrayList;
    }

    public ArrayList<POD_DOCS> getPod_docsArrayList() {
        return pod_docsArrayList;
    }

}
