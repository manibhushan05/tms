package in.aaho.android.employee.loads;

import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.v4.widget.SwipeRefreshLayout;
import android.support.v7.widget.AppCompatEditText;
import android.support.v7.widget.DefaultItemAnimator;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.text.Editable;
import android.text.TextUtils;
import android.text.TextWatcher;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
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
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

import in.aaho.android.employee.LoginActivity;
import in.aaho.android.employee.R;
import in.aaho.android.employee.common.ApiResponseListener;
import in.aaho.android.employee.common.BaseActivity;
import in.aaho.android.employee.common.Utils;

/**
 * Created by aaho on 20/05/18.
 */

public class MyLoadsActivity extends BaseActivity implements View.OnClickListener{
    private final String TAG = getClass().getSimpleName();
    private List<MyLoadRequest> dataList = new ArrayList<>();

    private ImageView imgMoveToTop;
    private RecyclerView recyclerView;
    private SwipeRefreshLayout refreshLayout;

    private Button btnClearFilterButton;
    private AppCompatEditText filterEditText;
    private ImageView imgSearchButton;
    private LinearLayout linearFilterSection;
    private TextView tvFilterLabel;

    private MyLoadsAdapter myLoadsAdapter;
    private TextView emptyView;
    private FloatingActionButton fabCall;
    private boolean isDataLoading;
    private String url = null;

    private int aahoOfficeId;
    private String roles = null;

    public String getSearchQuery() {
        return searchQuery;
    }
    public void setSearchQuery(String searchQuery) {
        this.searchQuery = searchQuery;
    }
    private String searchQuery = "";


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_my_loads);
        setToolbarTitle("My Inquiries");

        setViewVariables();
        setClickListeners();
        setupAdapters();
        setDataFromPrevActivity();

        filterEditText.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {
            }

            @Override
            public void onTextChanged(CharSequence filterQuery, int start, int before, int count) {
                // search button visibility
                if (start == 0) {
                    imgSearchButton.setVisibility(View.INVISIBLE);
                }
                if (count > 0) {
                    imgSearchButton.setVisibility(View.VISIBLE);
                }
            }

            @Override
            public void afterTextChanged(Editable s) {
            }
        });
    }

    private void loadSearchData() {
        url = "";
        dataList.clear();
        loadDataFromServer(false);
        showProgress();
        Utils.hideKeyboard(this);
    }

    @Override
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.imgSearchButton:
                // Set search query
                String searchQuery = filterEditText.getText().toString();
                setSearchQuery(searchQuery);
                setFilterResultVisibility(searchQuery);
                loadSearchData();
                break;
            case R.id.btnClearFilterButton:
                resetFilter();
                loadSearchData();
                break;
            default:
                break;
        }
    }

    /**
     * Reset filter dialog
     */
    private void resetFilter() {
        // NOTE: do not change the sequence of code
        setSearchQuery("");
        setFilterResultVisibility("");
        filterEditText.setText("");
        linearFilterSection.setVisibility(View.GONE);
    }


    /**
     * Set visibility of search result
     */
    private void setFilterResultVisibility(String filterQuery) {
        if (TextUtils.isEmpty(filterQuery)) {
            linearFilterSection.setVisibility(View.GONE);
        } else {
            linearFilterSection.setVisibility(View.VISIBLE);
            tvFilterLabel.setText("Results for " + "'" + filterQuery.toString() + "'");
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

    private void setDataFromPrevActivity() {
        Bundle bundle = getIntent().getExtras();
        if(bundle != null) {
            if(bundle.containsKey("aahoOfficeId")) {
                aahoOfficeId = bundle.getInt("aahoOfficeId");
            }
            if(bundle.containsKey("roles")) {
                roles = bundle.getString("roles");
            }
        }
    }

    private void setupAdapters() {
        //vehicleRequestAdapter = new VehicleRequestAdapter(this);
        myLoadsAdapter = new MyLoadsAdapter(this,dataList);

        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getApplicationContext());
        recyclerView.setLayoutManager(mLayoutManager);
        recyclerView.setItemAnimator(new DefaultItemAnimator());
        recyclerView.setAdapter(myLoadsAdapter);

        myLoadsAdapter.notifyDataSetChanged();
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
                launchDialer("+91"+"8978937498");
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

        linearFilterSection = findViewById(R.id.linear_filter_section);
        tvFilterLabel = findViewById(R.id.tvFilterLabel);
        btnClearFilterButton = findViewById(R.id.btnClearFilterButton);
        btnClearFilterButton.setOnClickListener(this);
        filterEditText = findViewById(R.id.filterEditText);
        imgSearchButton = findViewById(R.id.imgSearchButton);
        imgSearchButton.setOnClickListener(this);
    }

    private void loadDataFromServer(boolean swiped) {
        /*String url = GetMyLoadDataRequest.makeUrl();*/
        Map<String, String> params = new HashMap<String, String>();
        String searchQuery = this.getSearchQuery();
        if (!TextUtils.isEmpty(searchQuery)) {
            searchQuery = searchQuery.replace(" ", "+");
            params.put("search", searchQuery);
        }
        GetMyLoadDataRequest appDataRequest = new GetMyLoadDataRequest(url, params,
                aahoOfficeId,roles,new MyLoadsListener(swiped));
        queue(appDataRequest, !swiped);
    }

    private class MyLoadsListener extends ApiResponseListener {

        private final boolean swiped;

        MyLoadsListener(boolean swiped) {
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
                if(response != null && response.getString("status")
                        .equalsIgnoreCase("success")) {
                    if (response != null && response.has("data")) {
                        String nextPageUrl = response.getString("next");
                        if(TextUtils.isEmpty(nextPageUrl) ||
                                nextPageUrl.equalsIgnoreCase("null")) {
                            url = "";
                        } else {
                            url = nextPageUrl;
                        }
                        JSONArray vehiclesData = response.getJSONArray("data");
                        /*dataList.clear();*/
                        dataList.addAll(MyLoadRequest.fromJson(vehiclesData));
                        myLoadsAdapter.notifyDataSetChanged();
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
            isDataLoading = false;
            if (swiped) {
                refreshLayout.setRefreshing(false);
            } else {
                dismissProgress();
            }
            dataList.clear();
            if (dataList.size() == 0) {
                emptyView.setVisibility(View.VISIBLE);
                recyclerView.setVisibility(View.GONE);
            } else {
                emptyView.setVisibility(View.GONE);
                recyclerView.setVisibility(View.VISIBLE);
            }
            try {
                if (error != null && error.networkResponse != null
                        && error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    JSONObject errorData = new JSONObject(errorMsg);
                    Utils.showInfoDialog(MyLoadsActivity.this,
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
