package in.aaho.android.aahocustomers.vehicles;

import android.content.Intent;
import android.os.Bundle;
import android.support.v4.widget.SwipeRefreshLayout;
import android.support.v7.widget.DefaultItemAnimator;
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

import in.aaho.android.aahocustomers.R;
import in.aaho.android.aahocustomers.booking.App;
import in.aaho.android.aahocustomers.common.ApiResponseListener;
import in.aaho.android.aahocustomers.common.BaseActivity;
import in.aaho.android.aahocustomers.requests.VehicleListRequest;

/**
 * Created by shobhit on 10/10/16.
 */

public class VehicleListActivity extends BaseActivity {

    private static final List<BrokerVehicle> vehicleList = new ArrayList<>();

    private RecyclerView vehicleRecyclerView;
    private Button addVehicleButton;
    private SwipeRefreshLayout refreshLayout;

    private VehicleListAdapter vehicleListAdapter;
    private TextView emptyView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.vehicles_activity);
        setToolbarTitle("My Vehicles");

        setViewVariables();
        setClickListeners();
        setupAdapters();
    }

    @Override
    protected void onResume() {
        super.onResume();
        App.setFromSharedPreferencesIfNeeded();
        if (vehicleList.isEmpty()) {
            loadDataFromServer(false);
        }
    }

    public static List<BrokerVehicle> getVehicleList() {
        return vehicleList;
    }

    private void setupAdapters() {
        vehicleListAdapter = new VehicleListAdapter(this);

        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getApplicationContext());
        vehicleRecyclerView.setLayoutManager(mLayoutManager);
        vehicleRecyclerView.setItemAnimator(new DefaultItemAnimator());
        vehicleRecyclerView.setAdapter(vehicleListAdapter);

        vehicleListAdapter.notifyDataSetChanged();
    }

    private void setClickListeners() {
        addVehicleButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showVehicleAddDialog();
            }
        });
        refreshLayout.setOnRefreshListener(new SwipeRefreshLayout.OnRefreshListener() {
            @Override
            public void onRefresh() {
                loadDataFromServer(true);
            }
        });
    }

    private void showVehicleAddDialog() {
        VehicleAddEditDialogFragment.VehicleAddEditListener listener;
        listener = new VehicleAddEditDialogFragment.VehicleAddEditListener() {
            @Override
            public void onVehicleAddEdit(BrokerVehicleDetails vehicle, boolean newVehicle) {
                startVehicleDetailsActivity(vehicle);
            }
        };
        VehicleAddEditDialogFragment.showNewDialog(this, null, listener);
    }

    private void startVehicleDetailsActivity(BrokerVehicleDetails vehicle) {
        if (vehicle == null || vehicle.id == null) {
            return;
        }
        int index = -1;
        for (int i = 0; i < vehicleList.size(); i++) {
            BrokerVehicle brokerVehicle = vehicleList.get(i);
            if (brokerVehicle.getId() == vehicle.id) {
                index = i;
                break;
            }
        }

        if (index == -1) {
            Long categoryId = vehicle.category == null ? null : vehicle.category.id;
            vehicleList.add(new BrokerVehicle(vehicle.id, vehicle.getNumber(), vehicle.model, categoryId));
            index = vehicleList.size() - 1;
            vehicleListAdapter.notifyItemInserted(index);
        }
        VehicleDetailsActivity.position = index;
        Intent intent = new Intent(this, VehicleDetailsActivity.class);
        startActivity(intent);
    }

    private void setViewVariables() {
        vehicleRecyclerView = findViewById(R.id.my_vehicles_recycler_view);
        refreshLayout = findViewById(R.id.swipe_refresh_layout);
        addVehicleButton = findViewById(R.id.vehicle_list_add_btn);
        emptyView = findViewById(R.id.empty_view);
        // For the time being we don't allow to add vehicle, hide now
        addVehicleButton.setVisibility(View.GONE);
    }

    private void loadDataFromServer(boolean swiped) {
        VehicleListRequest appDataRequest = new VehicleListRequest(new VehicleListResponseListener(swiped));
        queue(appDataRequest, !swiped);
    }


    private class VehicleListResponseListener extends ApiResponseListener {

        private final boolean swiped;

        public VehicleListResponseListener(boolean swiped) {
            this.swiped = swiped;
        }

        @Override
        public void onResponse(JSONObject response) {
            if (swiped) {
                refreshLayout.setRefreshing(false);
            } else {
                dismissProgress();
            }
            String resp = response.toString();
            try {
                JSONObject jsonObject = new JSONObject(resp);
                JSONArray vehiclesData = jsonObject.getJSONArray("data");
                vehicleList.clear();
                vehicleList.addAll(BrokerVehicle.fromJson(vehiclesData));
                vehicleListAdapter.notifyDataSetChanged();
                if (vehicleList.size() == 0) {
                    emptyView.setVisibility(View.VISIBLE);
                } else {
                    emptyView.setVisibility(View.GONE);
                }
                JSONArray ownersData = jsonObject.getJSONArray("owners_data");
                JSONArray driversData = jsonObject.getJSONArray("drivers_data");
                JSONArray accountsData = jsonObject.getJSONArray("accounts_data");
                VehicleOwner.setData(ownersData);
                VehicleDriver.setData(driversData);
                BankAccount.setData(accountsData);
            } catch (JSONException e) {
                e.printStackTrace();
                toast("error reading response data:\n" + resp);
            }
        }

        @Override
        public void onError() {
            if (swiped) {
                refreshLayout.setRefreshing(false);
            } else {
                dismissProgress();
            }
        }
    }

}
