package in.aaho.android.loads.loads;

import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.v4.widget.SwipeRefreshLayout;
import android.support.v7.widget.DefaultItemAnimator;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.util.Log;
import android.view.View;
import android.widget.TextView;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;
import java.util.Locale;

import in.aaho.android.loads.R;
import in.aaho.android.loads.common.ApiResponseListener;
import in.aaho.android.loads.common.BaseActivity;
import in.aaho.android.loads.common.Prefs;

/**
 * Created by mani on 10/10/16.
 */

public class AvailableLoadsActivity extends BaseActivity {

    private static final List<AvailableLoadRequest> dataList = new ArrayList<>();

    private RecyclerView recyclerView;
    private SwipeRefreshLayout refreshLayout;

    //private VehicleRequestAdapter vehicleRequestAdapter;
    private AvailbaleLoadsAdapter availbaleLoadsAdapter;
    private TextView emptyView;
    private FloatingActionButton fabCall;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.vehicle_requests_activity);
        //display current date for loads
        SimpleDateFormat sdf = new SimpleDateFormat("dd MMM", Locale.getDefault());
        Calendar c = Calendar.getInstance();
        c.setTime(new Date());
        c.add(Calendar.DATE, 3);
        Date currentDatePlusThree = c.getTime();
        setToolbarTitle("Loads "+ sdf.format(Calendar.getInstance().getTime()) +
                " - "+ sdf.format(currentDatePlusThree));

        setViewVariables();
        setClickListeners();
        setupAdapters();
    }

    @Override
    protected void onResume() {
        super.onResume();
        //App.setFromSharedPreferencesIfNeeded();
        //if (dataList.isEmpty()) {
            loadDataFromServer(false);
        //}
    }

    private void setupAdapters() {
        //vehicleRequestAdapter = new VehicleRequestAdapter(this);
        availbaleLoadsAdapter = new AvailbaleLoadsAdapter(this,dataList);

        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getApplicationContext());
        recyclerView.setLayoutManager(mLayoutManager);
        recyclerView.setItemAnimator(new DefaultItemAnimator());
        recyclerView.setAdapter(availbaleLoadsAdapter);

        availbaleLoadsAdapter.notifyDataSetChanged();
    }

    private void setClickListeners() {
        refreshLayout.setOnRefreshListener(new SwipeRefreshLayout.OnRefreshListener() {
            @Override
            public void onRefresh() {
                loadDataFromServer(true);
            }
        });

        fabCall.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                launchDialer("+91"+"8978937498");
            }
        });
    }

    private void setViewVariables() {
        recyclerView = findViewById(R.id.recycler_view);
        refreshLayout = findViewById(R.id.swipe_refresh_layout);
        emptyView = findViewById(R.id.empty_view);
        fabCall = findViewById(R.id.fabCall);
        // Hide for now
        fabCall.setVisibility(View.GONE);
    }

    private void loadDataFromServer(boolean swiped) {
        /*AvailableLoadsRequest appDataRequest = new AvailableLoadsRequest(new AvailableLoadsListener(swiped));
        queue(appDataRequest, !swiped);*/
        String officeId = Prefs.get("aaho_office_id");
        String url = GetAvlLoadDataRequest.makeUrl(officeId,"unverified");
        GetAvlLoadDataRequest appDataRequest = new GetAvlLoadDataRequest(url,
                new AvailableLoadsListener(swiped));
        queue(appDataRequest, !swiped);
    }

    private class AvailableLoadsListener extends ApiResponseListener {

        private final boolean swiped;

        AvailableLoadsListener(boolean swiped) {
            this.swiped = swiped;
        }

        @Override
        public void onResponse(JSONObject response) {
            Log.i("",response.toString());
            if (swiped) {
                refreshLayout.setRefreshing(false);
            } else {
                dismissProgress();
            }
            String resp = response.toString();
            try {
                JSONObject jsonObject = new JSONObject(resp).getJSONObject("data");
                if(jsonObject != null && jsonObject.has("requirements")) {
                    JSONArray vehiclesData = jsonObject.getJSONArray("requirements");
                    dataList.clear();
                    dataList.addAll(AvailableLoadRequest.fromJson(vehiclesData));
                    availbaleLoadsAdapter.notifyDataSetChanged();
                    if (dataList.size() == 0) {
                        emptyView.setVisibility(View.VISIBLE);
                        recyclerView.setVisibility(View.GONE);
                    } else {
                        emptyView.setVisibility(View.GONE);
                        recyclerView.setVisibility(View.VISIBLE);
                    }
                } else {
                    dataList.clear();
                    if (dataList.size() == 0) {
                        emptyView.setVisibility(View.VISIBLE);
                        recyclerView.setVisibility(View.GONE);
                    } else {
                        emptyView.setVisibility(View.GONE);
                        recyclerView.setVisibility(View.VISIBLE);
                    }
                }
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


//    private class AvailableLoadsListener extends ApiResponseListener {
//
//        private final boolean swiped;
//
//        public AvailableLoadsListener(boolean swiped) {
//            this.swiped = swiped;
//        }
//
//        @Override
//        public void onResponse(JSONObject response) {
//            Log.i("",response.toString());
//            if (swiped) {
//                refreshLayout.setRefreshing(false);
//            } else {
//                dismissProgress();
//            }
//            String resp = response.toString();
//            try {
//                JSONObject jsonObject = new JSONObject(resp);
//                JSONArray vehiclesData = jsonObject.getJSONArray("data");
//                requestList.clear();
//                requestList.addAll(VehicleRequest.fromJson(vehiclesData));
//                vehicleRequestAdapter.notifyDataSetChanged();
//                if (requestList.size() == 0) {
//                    emptyView.setVisibility(View.VISIBLE);
//                    recyclerView.setVisibility(View.GONE);
//                } else {
//                    emptyView.setVisibility(View.GONE);
//                    recyclerView.setVisibility(View.VISIBLE);
//                }
//            } catch (JSONException e) {
//                e.printStackTrace();
//                toast("error reading response data:\n" + resp);
//            }
//        }
//
//        @Override
//        public void onError() {
//            if (swiped) {
//                refreshLayout.setRefreshing(false);
//            } else {
//                dismissProgress();
//            }
//        }
//    }

}
