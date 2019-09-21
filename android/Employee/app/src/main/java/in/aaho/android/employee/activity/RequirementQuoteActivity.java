package in.aaho.android.employee.activity;

import android.support.v4.widget.SwipeRefreshLayout;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.support.v7.widget.DefaultItemAnimator;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.util.Log;
import android.view.View;
import android.widget.TextView;

import com.android.volley.VolleyError;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import in.aaho.android.employee.Aaho;
import in.aaho.android.employee.AvailableQuoteData;
import in.aaho.android.employee.R;
import in.aaho.android.employee.RequirementActivity;
import in.aaho.android.employee.adapter.AvailableQuotesAdapter;
import in.aaho.android.employee.common.ApiResponseListener;
import in.aaho.android.employee.common.BaseActivity;
import in.aaho.android.employee.common.Utils;
import in.aaho.android.employee.loads.AvailableLoadRequest;
import in.aaho.android.employee.loads.AvailableLoadsActivity;
import in.aaho.android.employee.loads.AvailbaleLoadsAdapter;
import in.aaho.android.employee.loads.GetAvlLoadDataRequest;
import in.aaho.android.employee.requests.GetAvlReqQuoteRequest;

public class RequirementQuoteActivity extends BaseActivity {
    private final String TAG = getClass().getSimpleName();
    private static final List<AvailableQuoteData> dataList = new ArrayList<>();

    private RecyclerView recyclerView;
    private SwipeRefreshLayout refreshLayout;

    //private VehicleRequestAdapter vehicleRequestAdapter;
    private AvailableQuotesAdapter availbaleLoadsAdapter;
    private TextView emptyView;
    private String requirement_id;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_requirement_quote);
        setToolbarTitle("Available Bids");

        setViewVariables();
        setClickListeners();
        setupAdapters();
        setReqId();
    }

    @Override
    protected void onResume() {
        super.onResume();
        loadDataFromServer(false);
    }

    private void setReqId() {
        Bundle bundle = getIntent().getExtras();
        if(bundle!=null) {
            if(bundle.containsKey("reqId")) {
                requirement_id = bundle.getString("reqId");
            }
        }
    }

    private void setupAdapters() {
        //vehicleRequestAdapter = new VehicleRequestAdapter(this);
        availbaleLoadsAdapter = new AvailableQuotesAdapter(this,dataList);

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
    }

    private void setViewVariables() {
        recyclerView = findViewById(R.id.recycler_view);
        refreshLayout = findViewById(R.id.swipe_refresh_layout);
        emptyView = findViewById(R.id.empty_view);
    }

    private void loadDataFromServer(boolean swiped) {
        Map<String, String> params = new HashMap<String, String>();
        params.put("requirement_id", requirement_id+"");
        GetAvlReqQuoteRequest appDataRequest = new GetAvlReqQuoteRequest(params,
                new AvailableQuoteListener(swiped));
        queue(appDataRequest, !swiped);
    }

    private class AvailableQuoteListener extends ApiResponseListener {

        private final boolean swiped;

        AvailableQuoteListener(boolean swiped) {
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
                /*JSONObject jsonObject = new JSONObject(resp).getJSONObject("data");*/
                if(response != null && response.has("data")) {
                    JSONObject data = response.getJSONObject("data");
                    if(data != null) {
                        JSONArray vehiclesData = data.getJSONArray("requirement_quotes");
                        dataList.clear();
                        dataList.addAll(AvailableQuoteData.fromJson(vehiclesData));
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
            if (swiped) {
                refreshLayout.setRefreshing(false);
            } else {
                dismissProgress();
            }
            dataList.clear();
            emptyView.setVisibility(View.VISIBLE);
            recyclerView.setVisibility(View.GONE);
            try {
                if (error != null && error.networkResponse != null
                        && error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    JSONObject errorData = new JSONObject(errorMsg);
                    Utils.showInfoDialog(RequirementQuoteActivity.this,
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
}
