package in.aaho.android.employee;

import java.util.Arrays;

public class TDFunctionality {
    public static final String PENDING_PAYMENTS = "pending_payments";
    public static final String CUSTOMER_INQUIRY = "customer_inquiries";
    public static final String PENDING_LR = "pending_lr";
    public static final String IN_TRANSIT = "in_transit";
    public static final String DELIVERED = "delivered";
    public static final String INVOICE_CONFIRMATION = "invoice_confirmation";
    public static final String NEW_INQUIRY = "new_inquiry";
    public static final String MY_INQUIRY = "my_inquiries";
    public static final String OPEN_INQUIRY = "open_inquiries";
    public static final String SEND_INVOICE = "send_invoice";
    public static final String PAY_BALANCE = "pay_balance";
    public static final String PAY_ADVANCE = "pay_advance";
    public static final String LR_GENERATION = "lr_generation";
    public static final String CONFIRM_BOOKING = "confirm_booking";
    public static final String RECONCILE = "reconcile";
    public static final String PROCESS_PAYMENTS = "process_payments";
    public static final String INWARD_ENTRY = "inward_entry";
    public static final String CONFIRM_INVOICE = "confirm_invoice";
    public static final String RAISE_INVOICE = "raise_invoice";
    public static final String VERIFY_POD = "verify_pod";

    /* This array maintains the working functionality at android side */
    private static String[] workingFunctionality = {
            CUSTOMER_INQUIRY,
            NEW_INQUIRY,
            MY_INQUIRY,
            OPEN_INQUIRY,
            PENDING_LR,
            IN_TRANSIT,
            DELIVERED,
            INVOICE_CONFIRMATION,
            PENDING_PAYMENTS
    };

    /** check if given functionality is ready to work */
    public static boolean isWorkingFunctionality(String functionalityName) {
        return Arrays.asList(workingFunctionality).contains(functionalityName);
    }

}
