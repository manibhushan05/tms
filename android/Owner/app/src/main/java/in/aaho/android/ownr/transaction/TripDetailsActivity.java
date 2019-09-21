package in.aaho.android.ownr.transaction;

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

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.adapter.CreditNoteDirectAdvanceAdapter;
import in.aaho.android.ownr.adapter.CreditNoteSupplierAdapter;
import in.aaho.android.ownr.adapter.DebitNoteSupplierAdapter;
import in.aaho.android.ownr.adapter.TripDetailsRateAdapter;
import in.aaho.android.ownr.adapter.TripPaymentInfoAdapter;
import in.aaho.android.ownr.common.ApiResponseListener;
import in.aaho.android.ownr.common.BaseActivity;
import in.aaho.android.ownr.data.PaymentData;
import in.aaho.android.ownr.data.TripDetailsPaymentData;
import in.aaho.android.ownr.parser.CreditNoteDirectAdvanceParser;
import in.aaho.android.ownr.parser.CreditNoteSupplierParser;
import in.aaho.android.ownr.parser.DebitNoteSupplierParser;
import in.aaho.android.ownr.parser.PaymentDataParser;
import in.aaho.android.ownr.parser.TripDetailsPaymentParser;
import in.aaho.android.ownr.requests.CompleteTripDetailsRequest;

public class TripDetailsActivity extends BaseActivity {
    private final String TAG = getClass().getSimpleName();
    private TextView tvTripStatus;
    private TextView tvPickUpCity;
    private TextView tvDropCity;
    private TextView tvLrNumber;
    private TextView tvShipmentDate;
    private TextView tvTitleDebitNoteSupplier, tvTitleCreditNoteSupplier,
            tvTitleCreditNoteForDirectAdvance;
    public TripPaymentInfoAdapter mAllocatedVehicleAdapter;
    public TripDetailsRateAdapter mPaymentAdapter;
    public DebitNoteSupplierAdapter mDebitNoteSupplierAdapter;
    public CreditNoteSupplierAdapter mCreditNoteSupplierAdapter;
    public CreditNoteDirectAdvanceAdapter mCreditNoteDirectAdvanceAdapter;

    public LinearLayoutManager layoutManagerPayment;
    private RecyclerView recyclerViewAlloctedVehicleInfo;
    private RecyclerView recyclerViewPaymentInfo;
    private RecyclerView recyclerViewDebitNoteSupplier;
    private RecyclerView recyclerViewCreditNoteSupplier;
    private RecyclerView recyclerViewCreditNoteForDirectAdvance;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_trip_details);
        setToolbarTitle("Trip Details");
        setViewVariables();
        loadDataFromServer();
    }

    private void setViewVariables() {
        recyclerViewAlloctedVehicleInfo = findViewById(R.id.rv_trip_details_allocted_vehicle);
        recyclerViewPaymentInfo = findViewById(R.id.rv_trip_details_payments);
        recyclerViewDebitNoteSupplier = findViewById(R.id.recycler_view_debit_note_supplier);
        recyclerViewCreditNoteSupplier = findViewById(R.id.recycler_view_credit_note_supplier);
        recyclerViewCreditNoteForDirectAdvance = findViewById(R.id.recycler_view_credit_note_for_direct_advance);
        tvTripStatus = findViewById(R.id.tvTripDetailsStatus);
        tvPickUpCity = findViewById(R.id.tvNumberOfBookingsValue);
        tvDropCity = findViewById(R.id.tvTotalAmountValue);
        tvLrNumber = findViewById(R.id.tvTripDetailsLrNumber);
        tvShipmentDate = findViewById(R.id.tvTripDetailsShipmentDate);

        tvTitleDebitNoteSupplier = findViewById(R.id.tvTitleDebitNoteSupplier);
        tvTitleCreditNoteSupplier = findViewById(R.id.tvTitleCreditNoteSupplier);
        tvTitleCreditNoteForDirectAdvance = findViewById(R.id.tvTitleCreditNoteForDirectAdvance);
    }

    private void loadDataFromServer() {
        long bookingID = Integer.parseInt(getIntent().getStringExtra("trans_id"));

        CompleteTripDetailsRequest appDataRequest = new CompleteTripDetailsRequest(bookingID, new TripDetailsResponseListener());
        queue(appDataRequest);
    }

    private class TripDetailsResponseListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            String resp = response.toString();
            try {
                JSONObject jsonObject = new JSONObject(resp);
                /*JSONObject bookingData = jsonObject.getJSONObject("booking");*/
                JSONObject bookingData = jsonObject.getJSONObject("data");
                updateUI(bookingData);
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
                    toast(errorMsg);
                    Log.i(TAG, errorMsg);
                }
            } catch (UnsupportedEncodingException e) {
                e.printStackTrace();
            } catch (Exception ex) {
                Log.e(TAG, "Exception = " + ex.getLocalizedMessage());
            }
        }

        /*@Override
        public void onError() {
            dismissProgress();
        }*/
    }

    private void updateUI(JSONObject jsonObject) {
        try {
            /*updateBasicDetailsUI(jsonObject.getJSONObject("basic_details"));*/
            updateBasicDetailsUI(jsonObject);

            TripDetailsPaymentParser tripDetailsPaymentParser = new TripDetailsPaymentParser(jsonObject);
            setupRecycleViewPaymentInfo(recyclerViewPaymentInfo, tripDetailsPaymentParser.getTripDetailsPaymentDataArrayList());

            PaymentDataParser paymentDataParser = new PaymentDataParser(jsonObject.getJSONArray("outward_payments"));
            setupRecycleViewAllocatedVehicleInfo(recyclerViewAlloctedVehicleInfo, paymentDataParser.getPaymentDataArrayList());

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
            /*tvTripStatus.setText(jsonObject.getString("vehicle_number"));*/
            tvTripStatus.setText(jsonObject.getString("lorry_number"));
            /*tvPickUpCity.setText(jsonObject.getString("source_city"));*/
            tvPickUpCity.setText(jsonObject.getString("from_city"));
            /*tvDropCity.setText(jsonObject.getString("destination_city"));*/
            tvDropCity.setText(jsonObject.getString("to_city"));
            /*tvLrNumber.setText(jsonObject.getString("lr_numbers"));*/
            JSONArray jsonLRNumbers = jsonObject.getJSONArray("lr_numbers");
            String strLRList = "";
            for (int j = 0; j < jsonLRNumbers.length(); j++) {
                if (TextUtils.isEmpty(strLRList)) {
                    strLRList = jsonLRNumbers.getJSONObject(j)
                            .getString("lr_number");
                } else {
                    strLRList = strLRList + "\n" + jsonLRNumbers.getJSONObject(j)
                            .getString("lr_number");
                }
            }
            tvLrNumber.setText(strLRList);
            tvShipmentDate.setText(jsonObject.getString("shipment_date"));
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    void setupRecycleViewAllocatedVehicleInfo(RecyclerView recyclerView, List<PaymentData> paymentDatas) {
        recyclerView.setHasFixedSize(true);
        LinearLayoutManager layoutManager = new LinearLayoutManager(this);
        layoutManager.setOrientation(LinearLayoutManager.VERTICAL);
        recyclerView.setLayoutManager(layoutManager);
        mAllocatedVehicleAdapter = new TripPaymentInfoAdapter(paymentDatas);
        recyclerView.setAdapter(mAllocatedVehicleAdapter);
    }

    void setupRecycleViewPaymentInfo(RecyclerView recList, List<TripDetailsPaymentData> tripDetailsPaymentDataList) {
        recList.setHasFixedSize(true);
        layoutManagerPayment = new LinearLayoutManager(this);
        layoutManagerPayment.setOrientation(LinearLayoutManager.VERTICAL);
        recList.setLayoutManager(layoutManagerPayment);
        mPaymentAdapter = new TripDetailsRateAdapter(tripDetailsPaymentDataList);
        recList.setAdapter(mPaymentAdapter);
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
