package in.aaho.android.ownr.drivers;

import android.content.Intent;
import android.os.Bundle;
import android.support.v4.widget.SwipeRefreshLayout;
import android.support.v7.widget.DefaultItemAnimator;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.text.TextUtils;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import com.android.volley.VolleyError;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.List;

import in.aaho.android.ownr.common.ApiResponseListener;
import in.aaho.android.ownr.common.BaseActivity;
import in.aaho.android.ownr.R;
import in.aaho.android.ownr.booking.App;
import in.aaho.android.ownr.requests.DriverListRequest;

/**
 * Created by mani on 10/10/16.
 */

public class ListDriversActivity extends BaseActivity {
    private final String TAG = getClass().getSimpleName();

    private static List<BrokerDriver> driverList = new ArrayList<>();

    private RecyclerView driverRecyclerView;
    private Button addDriverButton;
    private SwipeRefreshLayout refreshLayout;
    private TextView emptyView;

    private DriverListAdapter driverListAdapter;
    private boolean isDataLoading;
    private String url = "";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.drivers_activity);
        setToolbarTitle("My Drivers");

        setViewVariables();
        setClickListeners();
        setupAdapters();
    }

    @Override
    protected void onResume() {
        super.onResume();
        App.setFromSharedPreferencesIfNeeded();
        /*if (driverList.isEmpty()) {
            loadDataFromServer(false);
        }*/
        /*driverList = new ArrayList<>();*/
        /*driverList.clear();*/
        loadDataFromServer(false);
    }

    public static List<BrokerDriver> getDriverList() {
        return driverList;
    }

    private void setupAdapters() {
        driverList = new ArrayList<>();
        driverListAdapter = new DriverListAdapter(this);

        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getApplicationContext());
        driverRecyclerView.setLayoutManager(mLayoutManager);
        driverRecyclerView.setItemAnimator(new DefaultItemAnimator());
        driverRecyclerView.setAdapter(driverListAdapter);

        driverListAdapter.notifyDataSetChanged();
        setRecyclerScroll();
    }

    private void setClickListeners() {
        addDriverButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                launchNewDriverActivity();
            }
        });
        refreshLayout.setOnRefreshListener(new SwipeRefreshLayout.OnRefreshListener() {
            @Override
            public void onRefresh() {
                url = "";
                loadDataFromServer(true);
            }
        });
    }

    private void launchNewDriverActivity() {
        DriverDetailsActivity.position = -1;  // means new driver
        Intent intent = new Intent(this, DriverDetailsActivity.class);
        startActivity(intent);
    }

    private void addToDriverList(BrokerDriverDetails driverDetails) {
        if (driverDetails == null || driverDetails.id == null) {
            return;
        }
        int index = -1;
        for (int i = 0; i < driverList.size(); i++) {
            BrokerDriver brokerDriver = driverList.get(i);
            if (brokerDriver.getId() == driverDetails.id) {
                index = i;
                break;
            }
        }

        if (index == -1) {
            driverList.add(new BrokerDriver(driverDetails.id, driverDetails.name, driverDetails.phone));
            index = driverList.size() - 1;
            if (driverListAdapter != null) {
                driverListAdapter.notifyItemInserted(index);
            }
        }
    }

    private void setViewVariables() {
        driverRecyclerView = findViewById(R.id.my_drivers_recycler_view);
        addDriverButton = findViewById(R.id.drivers_list_add_btn);
        refreshLayout = findViewById(R.id.swipe_refresh_layout);
        emptyView = findViewById(R.id.empty_view);
    }

    private void loadDataFromServer(boolean swiped) {
        DriverListRequest appDataRequest = new DriverListRequest(url,new DriverListResponseListener(swiped));
        queue(appDataRequest, !swiped);
    }

    private class DriverListResponseListener extends ApiResponseListener {

        private final boolean swiped;

        public DriverListResponseListener(boolean swiped) {
            this.swiped = swiped;
        }

        @Override
        public void onResponse(JSONObject response) {
            isDataLoading = false;
            if (swiped) {
                driverList.clear();
                refreshLayout.setRefreshing(false);
            } else {
                dismissProgress();
            }
            String resp = response.toString();
            try {
                JSONObject jsonObject = new JSONObject(resp);
                JSONArray driversData = jsonObject.getJSONArray("data");
                /*JSONArray driversData = jsonObject.getJSONArray("results");*/
                String nextPageUrl = jsonObject.getString("next");
                if(TextUtils.isEmpty(nextPageUrl)) {
                    url = "";
                } else {
                    url = nextPageUrl;
                }
                /*driverList.clear();*/
                driverList.addAll(BrokerDriver.fromJson(driversData));
                driverListAdapter.notifyDataSetChanged();
                if (driverList.size() == 0) {
                    emptyView.setVisibility(View.VISIBLE);
                } else {
                    emptyView.setVisibility(View.GONE);
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
            if (swiped) {
                refreshLayout.setRefreshing(false);
            } else {
                dismissProgress();
            }
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
                Log.e(TAG,"Exception = "+ex.getLocalizedMessage());
            }
        }

    }

    private void setRecyclerScroll() {
        driverRecyclerView.addOnScrollListener(new RecyclerView.OnScrollListener() {
            @Override
            public void onScrollStateChanged(RecyclerView recyclerView, int newState) {
                super.onScrollStateChanged(recyclerView, newState);

                if (!recyclerView.canScrollVertically(1)) {
                    // Toast.makeText(getActivity(),"LAst",Toast.LENGTH_LONG).show();
                    if(isDataLoading)
                        return;
                    else {
                        if(!TextUtils.isEmpty(url)) {
                            isDataLoading = true;
                            loadDataFromServer(false);
                        }
                    }
                }
            }
        });
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        driverList.clear();
    }

}
