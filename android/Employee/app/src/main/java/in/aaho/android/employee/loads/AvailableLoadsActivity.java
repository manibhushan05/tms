package in.aaho.android.employee.loads;

import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.v4.widget.SwipeRefreshLayout;
import android.support.v7.widget.DefaultItemAnimator;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.text.TextUtils;
import android.util.Log;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;

import com.android.volley.VolleyError;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.UnsupportedEncodingException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;
import java.util.Locale;

import in.aaho.android.employee.R;
import in.aaho.android.employee.common.ApiResponseListener;
import in.aaho.android.employee.common.BaseActivity;
import in.aaho.android.employee.common.Utils;
import in.aaho.android.employee.other.Role;

/**
 * Created by mani on 10/10/16.
 */

public class AvailableLoadsActivity extends BaseActivity {
    private final String TAG = getClass().getSimpleName();
    private List<AvailableLoadRequest> dataList = new ArrayList<>();

    private ImageView imgMoveToTop;
    private RecyclerView recyclerView;
    private SwipeRefreshLayout refreshLayout;

    //private VehicleRequestAdapter vehicleRequestAdapter;
    private AvailbaleLoadsAdapter availbaleLoadsAdapter;
    private TextView emptyView;
    private FloatingActionButton fabCall;
    private int roleId;
    private int aahoOfficeId;

    public String getStatus() {
        return status;
    }

    private String status;

    private boolean isDataLoading;
    private String url = null;
    private String roles = null;
    private String toolbarName = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.vehicle_requests_activity);

        setViewVariables();
        setClickListeners();
        setupAdapters();
        setDataFromPrevActivity();
        if(roles.contains(Role.TECHNOLOGY) || roles.contains(Role.MANAGEMENT)
                || roles.contains(Role.CITY_HEAD)) {
            setToolbarTitle(toolbarName);
        } else {
            setDateSlabForLoads();
        }
    }

    private void setDateSlabForLoads() {
        //display current date for loads
        SimpleDateFormat sdf = new SimpleDateFormat("dd MMM", Locale.getDefault());
        Calendar c = Calendar.getInstance();
        c.setTime(new Date());
        c.add(Calendar.DATE, 3);
        Date currentDatePlusThree = c.getTime();
        setToolbarTitle(toolbarName+" "+ sdf.format(Calendar.getInstance().getTime()) +
                " - "+ sdf.format(currentDatePlusThree));
    }

    private void setDataFromPrevActivity() {
        Bundle bundle = getIntent().getExtras();
        if(bundle != null) {
            if(bundle.containsKey("roleId")) {
                roleId = bundle.getInt("roleId");
            }
            if(bundle.containsKey("aahoOfficeId")) {
                aahoOfficeId = bundle.getInt("aahoOfficeId");
            }
            if(bundle.containsKey("status")) {
                status = bundle.getString("status");
            }
            if(bundle.containsKey("roles")) {
                roles = bundle.getString("roles");
            }
            if(bundle.containsKey("toolbarName")) {
                toolbarName = bundle.getString("toolbarName");
            }
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        //App.setFromSharedPreferencesIfNeeded();
        if (dataList.isEmpty()) {
            loadDataFromServer(false);
        }
    }

    private void setupAdapters() {
        //vehicleRequestAdapter = new VehicleRequestAdapter(this);
        dataList = new ArrayList<>();
        availbaleLoadsAdapter = new AvailbaleLoadsAdapter(this,dataList);

        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getApplicationContext());
        recyclerView.setLayoutManager(mLayoutManager);
        recyclerView.setItemAnimator(new DefaultItemAnimator());
        recyclerView.setAdapter(availbaleLoadsAdapter);

        availbaleLoadsAdapter.notifyDataSetChanged();
        setRecyclerScroll();
    }

    private void setClickListeners() {
        refreshLayout.setOnRefreshListener(new SwipeRefreshLayout.OnRefreshListener() {
            @Override
            public void onRefresh() {
                url = "";
                loadDataFromServer(true);
            }
        });

        fabCall.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                //launchDialer("+91"+"8978937498");
                Utils.launchDialer(view.getContext(),"+91"+"8978937498");
            }
        });

        imgMoveToTop.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if(recyclerView != null && dataList.size() > 0) {
                    recyclerView.scrollToPosition(0);
                }
            }
        });
    }

    private void setViewVariables() {
        recyclerView = findViewById(R.id.recycler_view);
        refreshLayout = findViewById(R.id.swipe_refresh_layout);
        emptyView = findViewById(R.id.empty_view);
        imgMoveToTop = findViewById(R.id.imgMoveToTop);
        fabCall = findViewById(R.id.fabCall);
        // Hide for now
        fabCall.setVisibility(View.GONE);
    }

    private void loadDataFromServer(boolean swiped) {
        /*AvailableLoadsRequest appDataRequest = new AvailableLoadsRequest(new AvailableLoadsListener(swiped));
        queue(appDataRequest, !swiped);*/
        /*String status = "";
        if(roleId == 1) {
            status = "open";
        } else if(roleId == 2) {
            status = "unverified";
        } else {
            // Do nothing here
        }*/

        /*String url = GetAvlLoadDataRequest.makeUrl(aahoOfficeId,status,bIsSuperUser);*/
        GetAvlLoadDataRequest appDataRequest = new GetAvlLoadDataRequest(url,
                aahoOfficeId,status,roles,new AvailableLoadsListener(swiped));
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
            isDataLoading = false;
            if (swiped) {
                dataList.clear();
                refreshLayout.setRefreshing(false);
            } else {
                dismissProgress();
            }
            String resp = response.toString();
            try {
                /*JSONObject jsonObject = new JSONObject(resp).getJSONObject("data");*/
                if(response != null && response.has("data")) {
                    String nextPageUrl = response.getString("next");
                    if(TextUtils.isEmpty(nextPageUrl) ||
                            nextPageUrl.equalsIgnoreCase("null")) {
                        url = "";
                    } else {
                        url = nextPageUrl;
                    }
                    JSONArray vehiclesData = response.getJSONArray("data");
                    /*dataList.clear();*/
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
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);
            isDataLoading = false;
            if (swiped) {
                refreshLayout.setRefreshing(false);
            } else {
                dismissProgress();
            }
            dataList.clear();
            emptyView.setVisibility(View.VISIBLE);
            recyclerView.setVisibility(View.GONE);
            availbaleLoadsAdapter.notifyDataSetChanged();
            try {
                if (error != null && error.networkResponse != null
                        && error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    JSONObject errorData = new JSONObject(errorMsg);
                    Utils.showInfoDialog(AvailableLoadsActivity.this,
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

    private void setRecyclerScroll() {
        recyclerView.addOnScrollListener(new RecyclerView.OnScrollListener() {
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

    public void setMoveToTopVisibility(int scrollPosition) {
        if(scrollPosition < 6) {
            imgMoveToTop.setVisibility(View.GONE);
        } else {
            imgMoveToTop.setVisibility(View.VISIBLE);
        }
    }

}
