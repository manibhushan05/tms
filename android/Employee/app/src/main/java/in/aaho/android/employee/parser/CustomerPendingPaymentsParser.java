package in.aaho.android.employee.parser;

import android.text.TextUtils;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

import in.aaho.android.employee.common.Utils;

public class CustomerPendingPaymentsParser {

    public Integer id;
    public String customerName;
    public Integer pendingInvoices;
    public Integer overdueInvoices;
    public Double pendingAmount;
    public Double overdueAmount;
    public Double pendingInwardAdjustment;
    public String smeDueDate;

    private static final String KEY_ID = "id";
    private static final String KEY_CUSTOMER_NAME = "name";
    private static final String KEY_PENDING_INVOICES = "pending_invoices";
    private static final String KEY_OVERDUE_INVOICES = "overdue_invoices";
    private static final String KEY_PENDING_AMOUNT = "pending_amount";
    private static final String KEY_OVERDUE_AMOUNT = "overdue_amount";
    private static final String KEY_SME_DUE_DATE = "sme_due_date";
    private static final String KEY_PENDING_INWARD_ADJUSTMENT = "pending_inward_adjustment";
    private static final String KEY_OBJECT_CUSTOMER_DETAILS = "sme_profile";
    private static final String KEY_OBJECT_INVOICE_DETAILS = "invoice_details";

    public CustomerPendingPaymentsParser(Integer id, String customerName,
                                         Integer pendingInvoices, Integer overdueInvoices,
                                         Double pendingAmount, Double overdueAmount,
                                         Double pendingInwardAdjustment, String smeDueDate) {
        this.id = id;
        this.customerName = customerName;
        this.pendingInvoices = pendingInvoices;
        this.overdueInvoices = overdueInvoices;
        this.pendingAmount = pendingAmount;
        this.overdueAmount = overdueAmount;
        this.pendingInwardAdjustment = pendingInwardAdjustment;
        this.smeDueDate = smeDueDate;
    }

    public static CustomerPendingPaymentsParser fromJson(JSONObject jsonObject) throws JSONException {
        if (jsonObject == null || jsonObject.length() == 0) {
            return null;
        }

        String customerName = "";
        Integer pendingInvoices = null;
        Integer overdueInvoices = null;
        Double pendingAmount = null;
        Double overdueAmount = null;
        Double pendingInwardAdjustment = null;
        String smeDueDate = "";

        // Retrieve customer name
        JSONObject customerDetails = getObject(jsonObject,KEY_OBJECT_CUSTOMER_DETAILS);
        if(customerDetails != null) {
            customerName = Utils.get(customerDetails, KEY_CUSTOMER_NAME);
        }
        // Retrieve invoice details
        JSONObject invoiceDetails = getObject(jsonObject,KEY_OBJECT_INVOICE_DETAILS);
        if(invoiceDetails != null) {
            pendingInvoices = Utils.getInteger(invoiceDetails, KEY_PENDING_INVOICES);
            overdueInvoices = Utils.getInteger(invoiceDetails, KEY_OVERDUE_INVOICES);
            pendingAmount = Utils.getDouble(invoiceDetails, KEY_PENDING_AMOUNT);
            overdueAmount = Utils.getDouble(invoiceDetails, KEY_OVERDUE_AMOUNT);
            pendingInwardAdjustment = Utils.getDouble(invoiceDetails, KEY_PENDING_INWARD_ADJUSTMENT);
            smeDueDate = Utils.get(invoiceDetails, KEY_SME_DUE_DATE);
        }

        return new CustomerPendingPaymentsParser(
                Utils.getInteger(jsonObject, KEY_ID),
                customerName,
                pendingInvoices,
                overdueInvoices,
                pendingAmount,
                overdueAmount,
                pendingInwardAdjustment,
                smeDueDate
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

    public static List<CustomerPendingPaymentsParser> fromJson(JSONArray jsonArray) throws JSONException {
        List<CustomerPendingPaymentsParser> pendingLRParserArrayList = new ArrayList<>();
        for (int i = 0; i < jsonArray.length(); i++) {
            JSONObject obj = jsonArray.getJSONObject(i);
            CustomerPendingPaymentsParser pendingLRParser = fromJson(obj);
            pendingLRParserArrayList.add(pendingLRParser);
        }

        return pendingLRParserArrayList;
    }
}
