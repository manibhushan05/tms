package in.aaho.android.customer.transaction;

import android.os.Bundle;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

import in.aaho.android.customer.common.BaseActivity;
import in.aaho.android.customer.R;
import in.aaho.android.customer.adapter.AllocatedVehicleAdapter;
import in.aaho.android.customer.adapter.LoadingAddressAdapter;
import in.aaho.android.customer.adapter.RequestedVehicleAdapter;
import in.aaho.android.customer.adapter.UnloadingAddressAdapter;
import in.aaho.android.customer.data.AddressData;
import in.aaho.android.customer.data.AllocatedVehicleData;
import in.aaho.android.customer.data.RequestedVehicleData;
import in.aaho.android.customer.parser.AddressParser;
import in.aaho.android.customer.parser.AllocatedVehicleParser;
import in.aaho.android.customer.requests.CancelTransactionRequest;

public class CompleteTripDetailsActivity extends BaseActivity {
    private RecyclerView recyclerViewAlloctedVehicleInfo;
    private RecyclerView recyclerViewLoadingLocations;
    private RecyclerView recyclerViewUnloadingLocations;
    private RecyclerView recyclerViewRequestedVehicle;
    private LinearLayoutManager layoutManagerVehicle;
    private LinearLayoutManager layoutManagerAddress;
    private LinearLayoutManager layoutManagerRequestedVehicle;
    private AllocatedVehicleAdapter mAllocatedVehicleAdapter;
    private LoadingAddressAdapter mLoadingLoadingAddressAdapter;
    private UnloadingAddressAdapter mUnloadingAddressAdapter;
    private RequestedVehicleAdapter mRequestedVehicleAdapter;
    private List<RequestedVehicleData> requestedVehicleDataList;


    private TextView tvPickupFrom;
    private TextView tvDropAt;
    private TextView tvTransactionID;
    private TextView tvStatus;
    private TextView tvShipmentDate;
    private TextView tvBookingDate;
    private TextView tvTotalAmount;
    private TextView tvPaidAmount;
    private TextView tvBalanceAmount;

    private TextView tvMaterial;
    private Button btnCancelTransaction;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_complete_trip_details);
        setToolbarTitle("Transaction Details");

        getID();
        setAdapter();
        btnCancelTransaction.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                CancelTransactionRequest.cancelTransaction(v, tvTransactionID.getText().toString());
            }
        });
    }

    private void setAdapter() {
        String data = getIntent().getStringExtra("value");
        try {
            JSONObject jsonObject = new JSONObject(data);
            setText(jsonObject.getJSONObject("basic_details"));
            AddressParser addressParserLoading = new AddressParser(jsonObject.getJSONObject("locations").getJSONArray("loading"));
            AddressParser addressParserUnLoading = new AddressParser(jsonObject.getJSONObject("locations").getJSONArray("unloading"));
            SetupRecycleViewLoadingAddress(recyclerViewLoadingLocations, addressParserLoading.getAddressDataArrayList());
            SetupRecycleViewUnloadingAddress(recyclerViewUnloadingLocations, addressParserUnLoading.getAddressDataArrayList());
            AllocatedVehicleParser allocatedVehicleParser = new AllocatedVehicleParser(jsonObject.getJSONArray("allocated_vehicle"));
            JSONArray jsonArrayAllocatedVehicle = jsonObject.getJSONArray("allocated_vehicle");
            if (jsonArrayAllocatedVehicle.length() > 0) {
                setupRecycleViewAllocatedVehicleInfo(recyclerViewAlloctedVehicleInfo, allocatedVehicleParser.getAllocatedVehicleDataArrayList());
            }
            requestedVehicleDataList = new ArrayList<>();
            requestedVehicleDataList.add(new RequestedVehicleData("32 Feet", "4"));
            requestedVehicleDataList.add(new RequestedVehicleData("Multi Axle", "2"));
            SetupRecycleViewRequestedVehicle(recyclerViewRequestedVehicle);
            String material = jsonObject.getJSONObject("locations").getString("material");
            if (material.isEmpty()) {
                tvMaterial.setText("Not Filled");
            } else {
                tvMaterial.setText(material);
            }

        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    private void getID() {
        recyclerViewAlloctedVehicleInfo = (RecyclerView) findViewById(R.id.recycler_view_pending_transaction_details_allocted_vehicle);
        recyclerViewLoadingLocations = (RecyclerView) findViewById(R.id.recycler_view_pending_transaction_details_loading_points);
        recyclerViewUnloadingLocations = (RecyclerView) findViewById(R.id.recycler_view_pending_transaction_details_unloading_points);
        recyclerViewRequestedVehicle = (RecyclerView) findViewById(R.id.recycler_view_pending_transaction_details_requested_vehicle);
        tvPickupFrom = (TextView) findViewById(R.id.btdPickupFrom);
        tvDropAt = (TextView) findViewById(R.id.btdDropAt);
        tvTransactionID = (TextView) findViewById(R.id.btdTransactionID);
        tvStatus = (TextView) findViewById(R.id.btdStatus);
        tvShipmentDate = (TextView) findViewById(R.id.btdShipmentDate);
        tvBookingDate = (TextView) findViewById(R.id.btdBookingDate);
        tvTotalAmount = (TextView) findViewById(R.id.bdtTotalAmount);
        tvPaidAmount = (TextView) findViewById(R.id.bdtPaidAmount);
        tvBalanceAmount = (TextView) findViewById(R.id.bdtBalanceAmount);
        tvMaterial = (TextView) findViewById(R.id.tvCDTMaterial);
        btnCancelTransaction = (Button) findViewById(R.id.btnCTDCancel);
    }

    private void setText(JSONObject jsonObject) {
        try {
            tvPickupFrom.setText(jsonObject.getString("pickup_city"));
            tvDropAt.setText(jsonObject.getString("drop_at"));
            tvTransactionID.setText(jsonObject.getString("transaction_id"));
            tvStatus.setText(jsonObject.getString("status"));
            tvShipmentDate.setText(jsonObject.getString("shipment_date"));
            tvBookingDate.setText(jsonObject.getString("booking_date"));
            tvTotalAmount.setText(jsonObject.getString("total_amount"));
            tvPaidAmount.setText(jsonObject.getString("paid_amount"));
            tvBalanceAmount.setText(jsonObject.getString("balance_amount"));
        } catch (JSONException e) {
            e.printStackTrace();
        }

    }

    void setupRecycleViewAllocatedVehicleInfo(RecyclerView recList, List<AllocatedVehicleData> allocatedVehicleDatas) {
        recList.setHasFixedSize(true);
        layoutManagerVehicle = new LinearLayoutManager(this);
        layoutManagerVehicle.setOrientation(LinearLayoutManager.VERTICAL);
        recList.setLayoutManager(layoutManagerVehicle);
        mAllocatedVehicleAdapter = new AllocatedVehicleAdapter(allocatedVehicleDatas);
        recList.setAdapter(mAllocatedVehicleAdapter);
    }

    void SetupRecycleViewRequestedVehicle(RecyclerView recList) {
        recList.setHasFixedSize(true);
        layoutManagerRequestedVehicle = new LinearLayoutManager(this);
        layoutManagerRequestedVehicle.setOrientation(LinearLayoutManager.VERTICAL);
        recList.setLayoutManager(layoutManagerRequestedVehicle);
        requestedVehicleDataList = new ArrayList<>();
        requestedVehicleDataList.add(new RequestedVehicleData("30 feet", "5"));
        requestedVehicleDataList.add(new RequestedVehicleData("32 feet", "2"));
        mRequestedVehicleAdapter = new RequestedVehicleAdapter(requestedVehicleDataList);
        recList.setAdapter(mRequestedVehicleAdapter);
    }

    void SetupRecycleViewLoadingAddress(RecyclerView recyclerView, List<AddressData> addressList) {
        recyclerView.setHasFixedSize(true);
        layoutManagerAddress = new LinearLayoutManager(this);
        layoutManagerAddress.setOrientation(LinearLayoutManager.VERTICAL);
        recyclerView.setLayoutManager(layoutManagerAddress);


        mLoadingLoadingAddressAdapter = new LoadingAddressAdapter(addressList);
        recyclerView.setAdapter(mLoadingLoadingAddressAdapter);
    }

    void SetupRecycleViewUnloadingAddress(RecyclerView recyclerView, List<AddressData> addressList) {
        recyclerView.setHasFixedSize(true);
        layoutManagerAddress = new LinearLayoutManager(this);
        layoutManagerAddress.setOrientation(LinearLayoutManager.VERTICAL);
        recyclerView.setLayoutManager(layoutManagerAddress);


        mUnloadingAddressAdapter = new UnloadingAddressAdapter(addressList);
        recyclerView.setAdapter(mUnloadingAddressAdapter);
    }

}
