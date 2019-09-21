package in.aaho.android.employee.activity;

import android.os.Bundle;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.text.TextUtils;
import android.util.Log;
import android.view.View;
import android.widget.TextView;

import com.android.volley.VolleyError;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.UnsupportedEncodingException;
import java.util.List;

import in.aaho.android.employee.R;
import in.aaho.android.employee.adapter.BookingDetailsRateAdapter;
import in.aaho.android.employee.adapter.CreditNoteDirectAdvanceAdapter;
import in.aaho.android.employee.adapter.CreditNoteSupplierAdapter;
import in.aaho.android.employee.adapter.DebitNoteSupplierAdapter;
import in.aaho.android.employee.adapter.InwardPaymentAdapter;
import in.aaho.android.employee.adapter.OutwardPaymentAdapter;
import in.aaho.android.employee.common.ApiResponseListener;
import in.aaho.android.employee.common.BaseActivity;
import in.aaho.android.employee.common.Utils;
import in.aaho.android.employee.loads.AvailableLoadsActivity;
import in.aaho.android.employee.models.BookingDetailsRateData;
import in.aaho.android.employee.models.InwardPaymentData;
import in.aaho.android.employee.models.OutwardPaymentData;
import in.aaho.android.employee.parser.CreditNoteDirectAdvanceParser;
import in.aaho.android.employee.parser.CreditNoteSupplierParser;
import in.aaho.android.employee.parser.DebitNoteSupplierParser;
import in.aaho.android.employee.parser.InwardPaymentDataParser;
import in.aaho.android.employee.parser.OutwardPaymentDataParser;
import in.aaho.android.employee.parser.SupplierRateDataParser;
import in.aaho.android.employee.requests.BookingDetailsRequest;

public class BookingDetailsActivity extends BaseActivity {
    private final String TAG = getClass().getSimpleName();
    private TextView tvTripStatus;
    private TextView tvPickUpCity;
    private TextView tvDropCity;
    private TextView tvLrNumber;
    private TextView tvShipmentDate;
    private TextView tvTitleDebitNoteSupplier, tvTitleCreditNoteSupplier,
            tvTitleCreditNoteForDirectAdvance;
    private TextView tvOutwardPaymentLabel,tvInwardPaymentLabel;
    public OutwardPaymentAdapter outwardPaymentAdapter;
    public InwardPaymentAdapter inwardPaymentAdapter;
    public BookingDetailsRateAdapter mBookingDetailsRateAdapter;

    public DebitNoteSupplierAdapter mDebitNoteSupplierAdapter;
    public CreditNoteSupplierAdapter mCreditNoteSupplierAdapter;
    public CreditNoteDirectAdvanceAdapter mCreditNoteDirectAdvanceAdapter;

    public LinearLayoutManager layoutManagerPayment;
    private RecyclerView recyclerViewOutwardPayments;
    private RecyclerView recyclerViewSupplierRates;
    private RecyclerView recyclerViewInwardPayments;
    private RecyclerView recyclerViewDebitNoteSupplier;
    private RecyclerView recyclerViewCreditNoteSupplier;
    private RecyclerView recyclerViewCreditNoteForDirectAdvance;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_booking_details);
        setToolbarTitle("Booking Details");
        setViewVariables();
        loadDataFromServer();
    }

    private void setViewVariables() {
        recyclerViewSupplierRates = findViewById(R.id.recycler_view_supplier_rates);
        recyclerViewOutwardPayments = findViewById(R.id.recycler_view_outward_payments);
        recyclerViewInwardPayments = findViewById(R.id.recycler_view_inward_payments);
        recyclerViewDebitNoteSupplier = findViewById(R.id.recycler_view_debit_note_supplier);
        recyclerViewCreditNoteSupplier = findViewById(R.id.recycler_view_credit_note_supplier);
        recyclerViewCreditNoteForDirectAdvance = findViewById(R.id.recycler_view_credit_note_for_direct_advance);
        tvTripStatus = findViewById(R.id.tvTripDetailsStatus);
        tvPickUpCity = findViewById(R.id.tvNumberOfBookingsValue);
        tvDropCity = findViewById(R.id.tvTotalAmountValue);
        tvLrNumber = findViewById(R.id.tvTripDetailsLrNumber);
        tvShipmentDate = findViewById(R.id.tvTripDetailsShipmentDate);
        tvOutwardPaymentLabel = findViewById(R.id.tvOutwardPaymentLabel);
        tvInwardPaymentLabel = findViewById(R.id.tvInwardPaymentLabel);

        tvTitleDebitNoteSupplier = findViewById(R.id.tvTitleDebitNoteSupplier);
        tvTitleCreditNoteSupplier = findViewById(R.id.tvTitleCreditNoteSupplier);
        tvTitleCreditNoteForDirectAdvance = findViewById(R.id.tvTitleCreditNoteForDirectAdvance);
    }

    private void loadDataFromServer() {
        long bookingID = getIntent().getIntExtra("id",0);

        BookingDetailsRequest bookingDetailsRequest = new BookingDetailsRequest(bookingID, new TripDetailsResponseListener());
        queue(bookingDetailsRequest);
    }

    private class TripDetailsResponseListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            String resp = response.toString();
            try {
                JSONObject jsonObject = new JSONObject(resp);
                if(jsonObject != null & jsonObject.has("data")) {
                    JSONObject bookingData = jsonObject.getJSONObject("data");
                    if (bookingData != null) {
                        updateUI(bookingData);
                    }
                }
            } catch (JSONException e) {
                e.printStackTrace();
                toast("error reading response data:\n" + resp);
            }
        }

        @Override
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);
            dismissProgress();
            try {
                if (error != null && error.networkResponse != null
                        && error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    JSONObject errorData = new JSONObject(errorMsg);
                    Utils.showInfoDialog(BookingDetailsActivity.this,
                            Utils.getRequestMessage(errorData),Utils.getRequestData(errorData));
                    Log.i(TAG, errorMsg);
                }
            } catch (UnsupportedEncodingException ex) {
                Log.e(TAG,"UnsupportedEncodingException = "+ex.getLocalizedMessage());
            } catch (Exception ex) {
                Log.e(TAG,"Exception = "+ex.getLocalizedMessage());
            }
        }
    }

    private void updateUI(JSONObject jsonObject) {
        try {
            updateBasicDetailsUI(jsonObject);

            SupplierRateDataParser supplierRateDataParser = new SupplierRateDataParser(jsonObject);
            setupRecycleViewPaymentInfo(recyclerViewSupplierRates, supplierRateDataParser.getBookingDetailsRateDataArrayList());

            if(jsonObject.has("outward_payments")) {
                JSONArray outwardJsonArray = jsonObject.getJSONArray("outward_payments");
                if(outwardJsonArray != null && outwardJsonArray.length() > 0) {
                    tvOutwardPaymentLabel.setVisibility(View.VISIBLE);
                    OutwardPaymentDataParser outwardPaymentDataParser = new OutwardPaymentDataParser(outwardJsonArray);
                    bindOutwardPaymentDataToRecycleView(outwardPaymentDataParser.getOutwardPaymentDataArrayList());
                } else {
                    tvOutwardPaymentLabel.setVisibility(View.GONE);
                }
            } else {
                tvOutwardPaymentLabel.setVisibility(View.GONE);
            }

            if(jsonObject.has("inward_payments")) {
                JSONArray inwardJsonArray = jsonObject.getJSONArray("inward_payments");
                if(inwardJsonArray != null && inwardJsonArray.length() > 0) {
                    tvInwardPaymentLabel.setVisibility(View.VISIBLE);
                    InwardPaymentDataParser inwardPaymentsDataParser = new InwardPaymentDataParser(inwardJsonArray);
                    bindInwardPaymentDataToRecycleView(inwardPaymentsDataParser.getInwardPaymentDataArrayList());
                } else {
                    tvInwardPaymentLabel.setVisibility(View.GONE);
                }
            } else {
                tvInwardPaymentLabel.setVisibility(View.GONE);
            }

            // Set debit note supplier data
            setDebitNoteSupplierData(jsonObject);
            // Set credit note supplier data
            setCreditNoteSupplierData(jsonObject);
            // Set credit note direct advance data
            setCreditNoteDirectAdvanceData(jsonObject);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void updateBasicDetailsUI(JSONObject jsonObject) {
        try {
            String vehicleNumber = "";
            if(jsonObject != null && jsonObject.has("vehicle_data")) {
                JSONObject vehicleData = jsonObject.getJSONObject("vehicle_data");
                if (vehicleData!=null && vehicleData.has("vehicle_number")) {
                    vehicleNumber = Utils.get(vehicleData,"vehicle_number");
                }
            }
            tvTripStatus.setText(vehicleNumber);
            // get from city
            String fromCity = "";
            if(jsonObject != null && jsonObject.has("from_city_fk_data")) {
                JSONObject vehicleData = jsonObject.getJSONObject("from_city_fk_data");
                if (vehicleData!=null && vehicleData.has("name")) {
                    fromCity = Utils.get(vehicleData,"name");
                }
            }
            tvPickUpCity.setText(fromCity);
            // get to city
            String toCity = "";
            if(jsonObject != null && jsonObject.has("to_city_fk_data")) {
                JSONObject vehicleData = jsonObject.getJSONObject("to_city_fk_data");
                if (vehicleData!=null && vehicleData.has("name")) {
                    toCity = Utils.get(vehicleData,"name");
                }
            }
            tvDropCity.setText(toCity);
            tvShipmentDate.setText(Utils.get(jsonObject,"shipment_date"));
            JSONArray jsonLRNumbers = jsonObject.getJSONArray("lr_numbers");
            String strLRList = "";
            for (int j = 0; j < jsonLRNumbers.length() ; j++) {
                if(TextUtils.isEmpty(strLRList)) {
                    strLRList = jsonLRNumbers.getJSONObject(j)
                            .getString("lr_number");
                } else {
                    strLRList = strLRList + "\n" + jsonLRNumbers.getJSONObject(j)
                            .getString("lr_number");
                }
            }
            tvLrNumber.setText(strLRList);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    void bindOutwardPaymentDataToRecycleView(List<OutwardPaymentData> outwardPaymentData) {
        recyclerViewOutwardPayments.setHasFixedSize(true);
        LinearLayoutManager layoutManager = new LinearLayoutManager(this);
        layoutManager.setOrientation(LinearLayoutManager.VERTICAL);
        recyclerViewOutwardPayments.setLayoutManager(layoutManager);
        outwardPaymentAdapter = new OutwardPaymentAdapter(outwardPaymentData);
        recyclerViewOutwardPayments.setAdapter(outwardPaymentAdapter);
//        recyclerViewOutwardPayments.setNestedScrollingEnabled(false);
    }

    void bindInwardPaymentDataToRecycleView(List<InwardPaymentData> inwardPaymentData) {
        recyclerViewInwardPayments.setHasFixedSize(true);
        LinearLayoutManager layoutManager = new LinearLayoutManager(this);
        layoutManager.setOrientation(LinearLayoutManager.VERTICAL);
        recyclerViewInwardPayments.setLayoutManager(layoutManager);
        inwardPaymentAdapter = new InwardPaymentAdapter(inwardPaymentData);
        recyclerViewInwardPayments.setAdapter(inwardPaymentAdapter);
    }

    void setupRecycleViewPaymentInfo(RecyclerView recList, List<BookingDetailsRateData> bookingDetailsRateDataList) {
        recList.setHasFixedSize(true);
        layoutManagerPayment = new LinearLayoutManager(this);
        layoutManagerPayment.setOrientation(LinearLayoutManager.VERTICAL);
        recList.setLayoutManager(layoutManagerPayment);
        mBookingDetailsRateAdapter = new BookingDetailsRateAdapter(bookingDetailsRateDataList);
        recList.setAdapter(mBookingDetailsRateAdapter);
    }

    /** Set the debit note supplier data */
    private void setDebitNoteSupplierData(JSONObject jsonObject) {
        try {
            if (jsonObject != null && jsonObject.has("debit_note_supplier")) {
                JSONArray jsonArray = null;
                jsonArray = jsonObject.getJSONArray("debit_note_supplier");

                if (jsonArray == null || jsonArray.length() == 0) {
                    setDebitNoteSupplierVisibility(false);
                } else {
                    setDebitNoteSupplierVisibility(true);
                    recyclerViewDebitNoteSupplier.setHasFixedSize(true);
                    layoutManagerPayment = new LinearLayoutManager(this);
                    layoutManagerPayment.setOrientation(LinearLayoutManager.VERTICAL);
                    recyclerViewDebitNoteSupplier.setLayoutManager(layoutManagerPayment);
                    mDebitNoteSupplierAdapter = new DebitNoteSupplierAdapter(
                            new DebitNoteSupplierParser(jsonArray).getDebitNoteSupplierList());
                    recyclerViewDebitNoteSupplier.setAdapter(mDebitNoteSupplierAdapter);
                }
            } else {
                setDebitNoteSupplierVisibility(false);
            }
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    /** Set the visibility of debit note supplier */
    private void setDebitNoteSupplierVisibility(boolean isVisible) {
        if (isVisible) {
            tvTitleDebitNoteSupplier.setVisibility(View.VISIBLE);
            recyclerViewDebitNoteSupplier.setVisibility(View.VISIBLE);
        } else {
            tvTitleDebitNoteSupplier.setVisibility(View.GONE);
            recyclerViewDebitNoteSupplier.setVisibility(View.GONE);
        }
    }

    /** Set the credit note supplier data */
    private void setCreditNoteSupplierData(JSONObject jsonObject) {
        try {
            if (jsonObject != null && jsonObject.has("credit_note_supplier")) {
                JSONArray jsonArray = null;
                jsonArray = jsonObject.getJSONArray("credit_note_supplier");

                if (jsonArray == null || jsonArray.length() == 0) {
                    setCreditNoteSupplierVisibility(false);
                } else {
                    setCreditNoteSupplierVisibility(true);
                    recyclerViewCreditNoteSupplier.setHasFixedSize(true);
                    layoutManagerPayment = new LinearLayoutManager(this);
                    layoutManagerPayment.setOrientation(LinearLayoutManager.VERTICAL);
                    recyclerViewCreditNoteSupplier.setLayoutManager(layoutManagerPayment);
                    mCreditNoteSupplierAdapter = new CreditNoteSupplierAdapter(
                            new CreditNoteSupplierParser(jsonArray).getCreditNoteSupplierList());
                    recyclerViewCreditNoteSupplier.setAdapter(mCreditNoteSupplierAdapter);
                }
            } else {
                setCreditNoteSupplierVisibility(false);
            }
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    /** Set the visibility of credit note supplier */
    private void setCreditNoteSupplierVisibility(boolean isVisible) {
        if (isVisible) {
            tvTitleCreditNoteSupplier.setVisibility(View.VISIBLE);
            recyclerViewCreditNoteSupplier.setVisibility(View.VISIBLE);
        } else {
            tvTitleCreditNoteSupplier.setVisibility(View.GONE);
            recyclerViewCreditNoteSupplier.setVisibility(View.GONE);
        }
    }

    /** Set the credit note direct advance data */
    private void setCreditNoteDirectAdvanceData(JSONObject jsonObject) {
        try {
            if (jsonObject != null && jsonObject.has("credit_note_for_direct_advance")) {
                JSONArray jsonArray = null;
                jsonArray = jsonObject.getJSONArray("credit_note_for_direct_advance");

                if (jsonArray == null || jsonArray.length() == 0) {
                    setCreditNoteDirectAdvanceVisibility(false);
                } else {
                    setCreditNoteDirectAdvanceVisibility(true);
                    recyclerViewCreditNoteForDirectAdvance.setHasFixedSize(true);
                    layoutManagerPayment = new LinearLayoutManager(this);
                    layoutManagerPayment.setOrientation(LinearLayoutManager.VERTICAL);
                    recyclerViewCreditNoteForDirectAdvance.setLayoutManager(layoutManagerPayment);
                    mCreditNoteDirectAdvanceAdapter = new CreditNoteDirectAdvanceAdapter(
                            new CreditNoteDirectAdvanceParser(jsonArray).getCreditNoteDirectAdvanceList());
                    recyclerViewCreditNoteForDirectAdvance.setAdapter(mCreditNoteDirectAdvanceAdapter);
                }
            } else {
                setCreditNoteDirectAdvanceVisibility(false);
            }
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    /** Set the visibility of credit note direct advance */
    private void setCreditNoteDirectAdvanceVisibility(boolean isVisible) {
        if (isVisible) {
            tvTitleCreditNoteForDirectAdvance.setVisibility(View.VISIBLE);
            recyclerViewCreditNoteForDirectAdvance.setVisibility(View.VISIBLE);
        } else {
            tvTitleCreditNoteForDirectAdvance.setVisibility(View.GONE);
            recyclerViewCreditNoteForDirectAdvance.setVisibility(View.GONE);
        }
    }

}
