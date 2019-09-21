package in.aaho.android.employee.parser;

import android.text.TextUtils;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

import in.aaho.android.employee.common.Utils;

public class PendingPaymentsParser {

    public String id;
    public String bookingId;
    public String invoiceNumber;
    public String customerName;
    public String pdfFileUrl;
    public String bookingStatusCurrent;
    public String primarySucceededBookingStatus;
    public String secondarySucceededBookingStatus;
    public String bookingStatusComment;
    public String bookingStatusCommentCreatedOn;
    public String bookingStatusMappingIds;
    public String manualBookingIds;
    public Double totalAmount;
    public Double amountToBeReceived;
    public String invoiceDate;
    public String dueDate;

    private static final String KEY_ID = "id";
    private static final String KEY_BOOKING_ID = "booking_id";
    private static final String KEY_CUSTOMER_NAME = "company_name";
    private static final String KEY_INVOICE_NUMBER = "invoice_number";
    private static final String KEY_PDF_FILE_URL = "s3_upload_url";
    private static final String KEY_TOTAL_AMOUNT = "total_amount";
    private static final String KEY_AMOUNT_TO_BE_RECEIVED = "amount_to_be_received";
    private static final String KEY_DUE_DATE = "due_date";
    private static final String KEY_INVOICE_DATE = "date";
    private static final String KEY_BOOKING_STATUS_CURRENT = "booking_status_current";
    private static final String KEY_PRIMARY_SUCCEEDED_BOOKING_STATUS = "primary_succeeded_booking_status";
    private static final String KEY_SECONDARY_SUCCEEDED_BOOKING_STATUS = "secondary_succeeded_booking_status";
    private static final String KEY_BOOKING_STATUS_COMMENT = "booking_status_comment";
    private static final String KEY_BOOKING_STATUS_COMMENT_CREATED_ON = "booking_status_comment_created_on";
    private static final String KEY_BOOKING_STATUS_MAPPING_ID = "booking_status_mapping_id";
    private static final String KEY_MANUAL_BOOKING_IDS = "manual_booking_id";

    private static final String KEY_OBJECT_BOOKING_STATUSES = "booking_statuses";

    public PendingPaymentsParser(String id, String bookingId, String customerName,
                                 String bookingStatusCurrent, String primarySucceededBookingStatus,
                                 String bookingStatusComment, String bookingStatusCommentCreatedOn,
                                 String bookingStatusMappingIds, String invoiceNumber,
                                 String pdfFileUrl, String manualBookingIds,
                                 Double totalAmount,Double amountToBeReceived, String invoiceDate, String dueDate,
                                 String secondarySucceededBookingStatus) {
        this.id = id;
        this.bookingId = bookingId;
        this.customerName = customerName;
        this.bookingStatusCurrent = bookingStatusCurrent;
        this.primarySucceededBookingStatus = primarySucceededBookingStatus;
        this.bookingStatusComment = bookingStatusComment;
        this.bookingStatusCommentCreatedOn = bookingStatusCommentCreatedOn;
        this.bookingStatusMappingIds = bookingStatusMappingIds;
        this.invoiceNumber = invoiceNumber;
        this.pdfFileUrl = pdfFileUrl;
        this.manualBookingIds = manualBookingIds;
        this.totalAmount = totalAmount;
        this.amountToBeReceived = amountToBeReceived;
        this.invoiceDate = invoiceDate;
        this.dueDate = dueDate;
        this.secondarySucceededBookingStatus = secondarySucceededBookingStatus;
    }

    public static PendingPaymentsParser fromJson(JSONObject jsonObject) throws JSONException {
        if (jsonObject == null || jsonObject.length() == 0) {
            return null;
        }

        String customerName = "";
        String invoiceNumber = "";
        String pdfFileUrl = "";
        String bookingStatusCurrent = "";
        String primarySucceededBookingStatus = "";
        String secondarySucceededBookingStatus = "";
        String bookingStatusComment = "";
        String bookingStatusCommentCreatedOn = "";
        String bookingStatusMappingIds = "";
        String manualBookingIds = "";

        // Retrieve customer name
        customerName = Utils.get(jsonObject, KEY_CUSTOMER_NAME);

        // Retrieve invoice number
        invoiceNumber = Utils.get(jsonObject, KEY_INVOICE_NUMBER);

        // Retrieve pdf file url
        pdfFileUrl = Utils.get(jsonObject, KEY_PDF_FILE_URL);

        // Retrieve various booking status
        if (jsonObject.has(KEY_OBJECT_BOOKING_STATUSES)) {
            JSONArray bookingStatuses = jsonObject.getJSONArray(KEY_OBJECT_BOOKING_STATUSES);
            if (bookingStatuses != null && bookingStatuses.length() > 0) {
                for (int count = 0; count < bookingStatuses.length(); count++) {
                    JSONObject booking = bookingStatuses.getJSONObject(count);
                    if (booking != null) {
                        if (count == 0) {
                            // Retrieve one time 0th object since all are having same data excepts ids
                            bookingStatusCurrent = Utils.get(booking, KEY_BOOKING_STATUS_CURRENT);
                            primarySucceededBookingStatus = Utils.get(booking, KEY_PRIMARY_SUCCEEDED_BOOKING_STATUS);
                            secondarySucceededBookingStatus = Utils.get(booking, KEY_SECONDARY_SUCCEEDED_BOOKING_STATUS);
                            bookingStatusComment = Utils.get(booking, KEY_BOOKING_STATUS_COMMENT);
                            bookingStatusCommentCreatedOn = Utils.get(booking, KEY_BOOKING_STATUS_COMMENT_CREATED_ON);
                        }

                        // make comma separated bookingStatusMappingIds
                        if(TextUtils.isEmpty(bookingStatusMappingIds)) {
                            bookingStatusMappingIds = Utils.get(booking, KEY_BOOKING_STATUS_MAPPING_ID) == null ? null : Utils.get(booking, KEY_BOOKING_STATUS_MAPPING_ID);
                            manualBookingIds = Utils.get(booking, KEY_BOOKING_STATUS_MAPPING_ID) == null ? null : Utils.get(booking, KEY_BOOKING_STATUS_MAPPING_ID);
                        } else {
                            bookingStatusMappingIds = bookingStatusMappingIds + "," +
                                    Utils.get(booking, KEY_BOOKING_STATUS_MAPPING_ID) == null ? null : Utils.get(booking, KEY_BOOKING_STATUS_MAPPING_ID);
                        }
                        // make comma separated manualBookingIds
                        if(TextUtils.isEmpty(manualBookingIds)) {
                            manualBookingIds = Utils.get(booking, KEY_BOOKING_STATUS_MAPPING_ID) == null ? null : Utils.get(booking, KEY_BOOKING_STATUS_MAPPING_ID);
                        } else {
                            manualBookingIds = manualBookingIds + "," +
                                    Utils.get(booking, KEY_MANUAL_BOOKING_IDS) == null ? null : Utils.get(booking, KEY_MANUAL_BOOKING_IDS);
                        }
                    }
                }
            }
        }

        return new PendingPaymentsParser(
                Utils.get(jsonObject, KEY_ID),
                Utils.get(jsonObject, KEY_BOOKING_ID),
                customerName,
                bookingStatusCurrent,
                primarySucceededBookingStatus,
                bookingStatusComment,
                bookingStatusCommentCreatedOn,
                bookingStatusMappingIds,
                invoiceNumber,
                pdfFileUrl,
                manualBookingIds,
                Utils.getDouble(jsonObject,KEY_TOTAL_AMOUNT),
                Utils.getDouble(jsonObject,KEY_AMOUNT_TO_BE_RECEIVED),
                Utils.get(jsonObject,KEY_INVOICE_DATE),
                Utils.get(jsonObject,KEY_DUE_DATE),
                secondarySucceededBookingStatus
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

    public static List<PendingPaymentsParser> fromJson(JSONArray jsonArray) throws JSONException {
        List<PendingPaymentsParser> arrayList = new ArrayList<>();
        for (int i = 0; i < jsonArray.length(); i++) {
            JSONObject obj = jsonArray.getJSONObject(i);
            PendingPaymentsParser pendingLRParser = fromJson(obj);
            arrayList.add(pendingLRParser);
        }

        return arrayList;
    }
}
