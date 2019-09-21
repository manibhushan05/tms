package in.aaho.android.employee.parser;

import android.text.TextUtils;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

import in.aaho.android.employee.common.Utils;

public class InTransitParser {

    public Integer id;
    public String bookingId;
    public String customerName;
    public Integer fromCityId;
    public Integer toCityId;
    public String fromCity;
    public String toCity;
    public String bookingStatusCurrent;
    public String primarySucceededBookingStatus;
    public String bookingStatusComment;
    public String bookingStatusCommentCreatedOn;
    public String bookingStatusLocationCreatedOn;
    public String vehicleNumber;
    public String vehicleType;
    public Integer vehicleId;
    public Integer bookingStatusMappingId;
    public String location;
    public boolean location_overdue;
    public String loadingDate;
    public String lrNumber;
    public String driverPhone;

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
    private static final String KEY_VEHICLE_NUMBER = "vehicle_number";
    private static final String KEY_TYPE_OF_VEHICLE = "type_of_vehicle";
    private static final String KEY_TYPE_OF_VEHICLE_ID = "type_of_vehicle_id";
    private static final String KEY_BOOKING_STATUS_MAPPING_ID = "booking_status_mapping_id";

    private static final String KEY_OBJECT_CUSTOMER_PLACED_ORDER_DATA = "customer_placed_order_data";
    private static final String KEY_OBJECT_BOOKING_STATUS_DETAILS = "booking_status_details";
    private static final String KEY_OBJECT_VEHICLE_DATA = "vehicle_data";
    private static final String KEY_OBJECT_STATUS_MAPPING_COMMENT_DATA = "booking_status_mapping_comment";
    private static final String KEY_OBJECT_STATUS_MAPPING_LOCATION_DATA = "booking_status_mapping_location";
    private static final String KEY_BOOKING_LOADING_DATE = "booking_loading_date";
    private static final String KEY_CITY = "city";
    private static final String KEY_DISTRICT = "district";
    private static final String KEY_STATE = "state";
    private static final String KEY_COUNTRY = "country";
    private static final String KEY_LOCATION_OVERDUE = "location_overdue";
    private static final String KEY_BOOKING_STATUS_LOCATION_CREATED_ON = "created_on";
    private static final String KEY_LRNUMBER = "lr_numbers";
    private static final String KEY_OBJECT_DRIVER_DATA = "driver_data";
    private static final String KEY_DRIVER_PHONE = "phone";

    public InTransitParser(Integer id, String bookingId, String customerName,
                           Integer fromCityId, Integer toCityId, String fromCity,
                           String toCity, String bookingStatusCurrent, String primarySucceededBookingStatus,
                           String bookingStatusComment, String bookingStatusCommentCreatedOn, String bookingStatusLocationCreatedOn,
                           String vehicleNumber, String vehicleType, Integer vehicleId,
                           Integer bookingStatusMappingId, String location, String loadingDate,
                           String lrNumber, String driverPhone, boolean location_overdue) {
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
        this.bookingStatusLocationCreatedOn = bookingStatusLocationCreatedOn;
        this.vehicleNumber = vehicleNumber;
        this.vehicleType = vehicleType;
        this.vehicleId = vehicleId;
        this.bookingStatusMappingId = bookingStatusMappingId;
        this.location = location;
        this.loadingDate = loadingDate;
        this.lrNumber = lrNumber;
        this.driverPhone = driverPhone;
        this.location_overdue = location_overdue;
    }

    public static InTransitParser fromJson(JSONObject jsonObject) throws JSONException {
        if (jsonObject == null || jsonObject.length() == 0) {
            return null;
        }

        String customerName = "";
        String vehicleNumber = "";
        String bookingStatusCurrent = "";
        String primarySucceededBookingStatus = "";
        String bookingStatusComment = "";
        String bookingStatusCommentCreatedOn = "";
        String bookingStatusLocationCreatedOn = "";
        Integer bookingStatusMappingId = null;
        String location = "";
        String loadingDate = "";
        String driverPhone = "";
        boolean location_overdue = true;

        // Retrieve customer name
        JSONObject customerPlacedOrderData = getObject(jsonObject,KEY_OBJECT_CUSTOMER_PLACED_ORDER_DATA);
        if(customerPlacedOrderData != null) {
            customerName = Utils.get(customerPlacedOrderData, KEY_CUSTOMER_NAME);
        }
        // Retrieve various booking status
        JSONObject bookingStatusDetail = getObject(jsonObject,KEY_OBJECT_BOOKING_STATUS_DETAILS);
        // Retrieve location
        JSONObject bookingStatusMappingLocation = getObject(bookingStatusDetail,KEY_OBJECT_STATUS_MAPPING_LOCATION_DATA);
        if(bookingStatusMappingLocation != null) {
            String city = Utils.get(bookingStatusMappingLocation, KEY_CITY);
            city = TextUtils.isEmpty(city)?"":city+", ";
            String district = Utils.get(bookingStatusMappingLocation, KEY_DISTRICT);
            district = TextUtils.isEmpty(district)?"":district+", ";
            String state = Utils.get(bookingStatusMappingLocation, KEY_STATE);
            state = TextUtils.isEmpty(state)?"":state+" ";
            String country = Utils.get(bookingStatusMappingLocation, KEY_COUNTRY);
            country = TextUtils.isEmpty(country)?"":country;
            bookingStatusLocationCreatedOn = Utils.get(bookingStatusMappingLocation, KEY_BOOKING_STATUS_LOCATION_CREATED_ON);
            String location_created_on = TextUtils.isEmpty(bookingStatusLocationCreatedOn)?"":"\n"+bookingStatusLocationCreatedOn;
            location = city + district + state + location_created_on;
            String location_overdue_string = Utils.get(bookingStatusMappingLocation, KEY_LOCATION_OVERDUE);
            location_overdue = TextUtils.isEmpty(location_overdue_string) || location_overdue_string.equalsIgnoreCase("true");

        }
        // Retrieve loading date
        loadingDate = Utils.get(bookingStatusDetail, KEY_BOOKING_LOADING_DATE);
        // Retrieve booking status mapping id
        bookingStatusMappingId = Utils.getInteger(bookingStatusDetail, KEY_BOOKING_STATUS_MAPPING_ID) == null
                ? null : Utils.getInteger(bookingStatusDetail, KEY_BOOKING_STATUS_MAPPING_ID);
        // Retrieve mapping comment related fields
        JSONObject bookingStatusMappingComment = getObject(bookingStatusDetail,KEY_OBJECT_STATUS_MAPPING_COMMENT_DATA);
        if(bookingStatusMappingComment != null) {
            bookingStatusCurrent = Utils.get(bookingStatusMappingComment, KEY_BOOKING_STATUS_CURRENT);
            primarySucceededBookingStatus = Utils.get(bookingStatusMappingComment, KEY_PRIMARY_SUCCEEDED_BOOKING_STATUS);
            bookingStatusComment = Utils.get(bookingStatusMappingComment, KEY_BOOKING_STATUS_COMMENT);
            bookingStatusCommentCreatedOn = Utils.get(bookingStatusMappingComment, KEY_BOOKING_STATUS_COMMENT_CREATED_ON);
        }
        // Retrieve vehicle number
        JSONObject vehicleData = getObject(jsonObject,KEY_OBJECT_VEHICLE_DATA);
        if(vehicleData != null) {
            vehicleNumber = Utils.get(vehicleData,KEY_VEHICLE_NUMBER);
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

        // Retrieve driver contact number
        JSONObject driverData = getObject(jsonObject,KEY_OBJECT_DRIVER_DATA);
        if(driverData != null) {
            driverPhone = Utils.get(driverData,KEY_DRIVER_PHONE);
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
                    lrList = lrList + "," + jsonLRNumbers.getJSONObject(j)
                            .getString("lr_number");
                }
            }
        }

        return new InTransitParser(
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
                bookingStatusLocationCreatedOn,
                vehicleNumber,
                Utils.get(jsonObject, KEY_TYPE_OF_VEHICLE),
                Utils.getInteger(jsonObject, KEY_TYPE_OF_VEHICLE_ID),
                bookingStatusMappingId,
                location,
                loadingDate,
                lrList,
                driverPhone,
                location_overdue
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

    public static List<InTransitParser> fromJson(JSONArray jsonArray) throws JSONException {
        List<InTransitParser> pendingLRParserArrayList = new ArrayList<>();
        for (int i = 0; i < jsonArray.length(); i++) {
            JSONObject obj = jsonArray.getJSONObject(i);
            InTransitParser pendingLRParser = fromJson(obj);
            pendingLRParserArrayList.add(pendingLRParser);
        }

        return pendingLRParserArrayList;
    }
}
