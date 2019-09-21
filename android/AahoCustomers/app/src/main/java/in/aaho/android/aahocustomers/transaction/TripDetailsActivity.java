package in.aaho.android.aahocustomers.transaction;

import android.os.Bundle;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.util.Log;
import android.view.View;
import android.widget.TextView;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.List;

import in.aaho.android.aahocustomers.R;
import in.aaho.android.aahocustomers.adapter.TripDetailsRateAdapter;
import in.aaho.android.aahocustomers.adapter.TripPaymentInfoAdapter;
import in.aaho.android.aahocustomers.common.ApiResponseListener;
import in.aaho.android.aahocustomers.common.BaseActivity;
import in.aaho.android.aahocustomers.data.PaymentData;
import in.aaho.android.aahocustomers.data.TripDetailsPaymentData;
import in.aaho.android.aahocustomers.parser.PaymentDataParser;
import in.aaho.android.aahocustomers.parser.TripDetailsPaymentParser;
import in.aaho.android.aahocustomers.requests.CompleteTripDetailsRequest;

public class TripDetailsActivity extends BaseActivity {

    private TextView tvTripStatus;
    private TextView tvPickUpCity;
    private TextView tvDropCity;
    private TextView tvLrNumber;
    private TextView tvShipmentDate;
    public TripPaymentInfoAdapter mAllocatedVehicleAdapter;
    public TripDetailsRateAdapter mPaymentAdapter;
    public LinearLayoutManager layoutManagerPayment;
//    private RecyclerView recyclerViewAlloctedVehicleInfo;
//    private TextView recyclerViewAlloctedVehicleInfoLabel;
    private RecyclerView recyclerViewPaymentInfo;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_trip_details);
        setToolbarTitle("Trip Details");
        setViewVariables();
        loadDataFromServer();
    }

    private void setViewVariables() {
//        recyclerViewAlloctedVehicleInfo = findViewById(R.id.rv_trip_details_allocted_vehicle);
//        recyclerViewAlloctedVehicleInfoLabel = findViewById(R.id.rv_trip_details_allocted_vehicle_label);
        recyclerViewPaymentInfo = findViewById(R.id.rv_trip_details_payments);
        tvTripStatus = findViewById(R.id.tvTripDetailsStatus);
        tvPickUpCity = findViewById(R.id.tvNumberOfBookingsValue);
        tvDropCity = findViewById(R.id.tvTotalAmountValue);
        tvLrNumber = findViewById(R.id.tvTripDetailsLrNumber);
        tvShipmentDate = findViewById(R.id.tvTripDetailsShipmentDate);
//        recyclerViewAlloctedVehicleInfo.setVisibility(View.GONE);
//        recyclerViewAlloctedVehicleInfoLabel.setVisibility(View.GONE);
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
                updateUI(jsonObject);
            } catch (JSONException e) {
                e.printStackTrace();
                toast("error reading response data:\n" + resp);
            }
        }

        @Override
        public void onError() {
            dismissProgress();
        }
    }

    private void updateUI(JSONObject jsonObject) {
        try {
            updateBasicDetailsUI(jsonObject.getJSONObject("basic_details"));
            PaymentDataParser paymentDataParser = new PaymentDataParser(jsonObject.getJSONArray("payments"));
            Log.e("DATA", String.valueOf(jsonObject.getJSONArray("payments")));
//            if (jsonObject.getJSONArray("payments").length() > 0) {
//                setupRecycleViewAllocatedVehicleInfo(recyclerViewAlloctedVehicleInfo, paymentDataParser.getPaymentDataArrayList());
//            }
            TripDetailsPaymentParser tripDetailsPaymentParser = new TripDetailsPaymentParser(jsonObject.getJSONObject("rates"));
            setupRecycleViewPaymentInfo(recyclerViewPaymentInfo, tripDetailsPaymentParser.getTripDetailsPaymentDataArrayList());
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    private void updateBasicDetailsUI(JSONObject jsonObject) {
        try {
            tvTripStatus.setText(jsonObject.getString("vehicle_number"));
            tvPickUpCity.setText(jsonObject.getString("source_city"));
            tvDropCity.setText(jsonObject.getString("destination_city"));
            tvLrNumber.setText(jsonObject.getString("lr_number"));
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

}
