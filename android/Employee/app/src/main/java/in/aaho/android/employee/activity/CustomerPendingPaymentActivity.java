package in.aaho.android.employee.activity;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.support.v4.widget.SwipeRefreshLayout;
import android.support.v7.widget.AppCompatEditText;
import android.support.v7.widget.DefaultItemAnimator;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.support.v7.widget.Toolbar;
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
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import in.aaho.android.employee.R;
import in.aaho.android.employee.adapter.CustomerPendingPaymentsAdapter;
import in.aaho.android.employee.common.ApiResponseListener;
import in.aaho.android.employee.common.BaseActivity;
import in.aaho.android.employee.common.Utils;
import in.aaho.android.employee.other.CustomerPendingPaymentCommentsDialog;
import in.aaho.android.employee.parser.CustomerPendingPaymentsParser;
import in.aaho.android.employee.parser.DeliveredParser;
import in.aaho.android.employee.requests.BookingStatusMappingUpdateRequest;
import in.aaho.android.employee.requests.CreateCustomerCommentRequest;
import in.aaho.android.employee.requests.GetCustomerPendingPaymentDataRequest;
import in.aaho.android.employee.requests.PendingPaymentCommentsRequest;
import in.aaho.android.employee.requests.PendingPaymentUpdateDueDateRequest;

public class CustomerPendingPaymentActivity extends BaseActivity implements
        CustomerPendingPaymentsAdapter.IOnCustPendingPaymentsRowListener,
        CustomerPendingPaymentsAdapter.IOnCustPendingPaymentsSetDueDateListener,
        CustomerPendingPaymentsAdapter.IOnCustPendingPaymentsCommentsListener,
        CustomerPendingPaymentCommentsDialog.IOnCustomerPendingPaymentCommentUpdateListener,
        View.OnClickListener {
    private final String TAG = getClass().getSimpleName();
    private List<CustomerPendingPaymentsParser> dataList = new ArrayList<>();

    private ImageView imgMoveToTop;
    private RecyclerView recyclerView;
    private SwipeRefreshLayout refreshLayout;

    private Button btnClearFilterButton;
    private AppCompatEditText filterEditText;
    private ImageView imgSearchButton;
    private LinearLayout linearFilterSection;
    private TextView tvFilterLabel;

    private CustomerPendingPaymentsAdapter adapter;
    private TextView emptyView;
    private boolean isDataLoading;
    private String url = null;
    private String roles = null;

    private final int MI_REQ_CODE_FOR_PENDING_PAYMENTS= 101;

    public String getSearchQuery() {
        return searchQuery;
    }
    public void setSearchQuery(String searchQuery) {
        this.searchQuery = searchQuery;
    }
    private String searchQuery = "";

    private CustomerPendingPaymentCommentsDialog customerPendingPaymentCommentsDialog;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_customer_pending_payments);

        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        getSupportActionBar().setTitle("Customer Pending Payments");

        setViewVariables();
        setClickListeners();
        setDataFromPrevActivity();
        setupAdapters();

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
        if (dataList.isEmpty()) {
            loadDataFromServer(false);
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if(requestCode == MI_REQ_CODE_FOR_PENDING_PAYMENTS) {
            if(resultCode == Activity.RESULT_OK) {
                // Update customer pending payments data list
                // get the flag from data to know if we need to refresh data
                if(data != null) {
                    if(data.getBooleanExtra("hasDataChanged",false))
                        loadDataFromServer(true);
                }
            }
        }
    }

    private void setDataFromPrevActivity() {
        Bundle bundle = getIntent().getExtras();
        if(bundle != null) {
            if(bundle.containsKey("roles")) {
                roles = bundle.getString("roles");
            }
        }
    }

    private void setupAdapters() {
        adapter = new CustomerPendingPaymentsAdapter(this,dataList,
                this, this, this);
        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getApplicationContext());
        recyclerView.setLayoutManager(mLayoutManager);
        recyclerView.setItemAnimator(new DefaultItemAnimator());
        recyclerView.setAdapter(adapter);
        adapter.notifyDataSetChanged();
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

        linearFilterSection = findViewById(R.id.linear_filter_section);
        tvFilterLabel = findViewById(R.id.tvFilterLabel);
        btnClearFilterButton = findViewById(R.id.btnClearFilterButton);
        btnClearFilterButton.setOnClickListener(this);
        filterEditText = findViewById(R.id.filterEditText);
        imgSearchButton = findViewById(R.id.imgSearchButton);
        imgSearchButton.setOnClickListener(this);
    }

    private void loadDataFromServer(boolean swiped) {
        Map<String, String> params = new HashMap<String, String>();
        String searchQuery = this.getSearchQuery();
        if (!TextUtils.isEmpty(searchQuery)) {
            searchQuery = searchQuery.replace(" ", "+");
            params.put("search", searchQuery);
        }

        GetCustomerPendingPaymentDataRequest dataRequest = new GetCustomerPendingPaymentDataRequest(url, params,
                new CustomerPendingPaymentsListener(swiped));
        queue(dataRequest, !swiped);
    }

    private class CustomerPendingPaymentsListener extends ApiResponseListener {

        private final boolean swiped;

        CustomerPendingPaymentsListener(boolean swiped) {
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
                if(response != null && response.getString("status")
                        .equalsIgnoreCase("success")) {
                    if (response.has("data")) {
                        String nextPageUrl = response.getString("next");
                        if(TextUtils.isEmpty(nextPageUrl) ||
                                nextPageUrl.equalsIgnoreCase("null")) {
                            url = "";
                        } else {
                            url = nextPageUrl;
                        }
                        JSONArray vehiclesData = response.getJSONArray("data");
                        /*dataList.clear();*/
                        dataList.addAll(CustomerPendingPaymentsParser.fromJson(vehiclesData));
                        adapter.notifyDataSetChanged();
                        setEmptyViewVisibility();
                    } else {
                        dataList.clear();
                        setEmptyViewVisibility();
                    }
                } else {
                    dataList.clear();
                    setEmptyViewVisibility();
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
            setEmptyViewVisibility();
            try {
                if (error != null && error.networkResponse != null
                        && error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    JSONObject errorData = new JSONObject(errorMsg);
                    Utils.showInfoDialog(CustomerPendingPaymentActivity.this,
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

    private void setEmptyViewVisibility() {
        if (dataList.size() == 0) {
            emptyView.setVisibility(View.VISIBLE);
            recyclerView.setVisibility(View.GONE);
        } else {
            emptyView.setVisibility(View.GONE);
            recyclerView.setVisibility(View.VISIBLE);
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

    @Override
    public void onPendingPaymentsItemClicked(CustomerPendingPaymentsParser pendingPaymentsParser) {
        // Open list of invoices activity
        Bundle bundle = new Bundle();
        bundle.putInt("id", pendingPaymentsParser.id);
        Intent intent = new Intent(CustomerPendingPaymentActivity.this,
                PendingPaymentsActivity.class);
        intent.putExtras(bundle);
        startActivityForResult(intent,MI_REQ_CODE_FOR_PENDING_PAYMENTS);
    }

    private void updatePendingPaymentDueDate(Integer id, String date) {
        PendingPaymentUpdateDueDateRequest pendingPaymentUpdateDueDateRequest = new PendingPaymentUpdateDueDateRequest(
                id, date, new UpdatePendingPaymentUpdateDueDateResponseListener());
        queue(pendingPaymentUpdateDueDateRequest);
    }


    private class UpdatePendingPaymentUpdateDueDateResponseListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            String resp = response.toString();
            try {
                String msg = Utils.get(response, "msg");
                if (response != null && response.getString("status")
                        .equalsIgnoreCase("success")) {
                    new Handler().postDelayed(new Runnable() {
                        @Override
                        public void run() {
                            url = "";
                            loadDataFromServer(true);
                        }
                    }, 100);
                    Utils.toast("Due Date updated successfully!");
                } else {
                    Utils.toast(msg);
                }

            } catch (JSONException e) {
                e.printStackTrace();
                Utils.toast("Could not update status! Please try again later.");
                Log.e(TAG, "error reading response data:\n" + resp);
            }
        }
    }

    private void getPendingPaymentComments(Integer id) {
        PendingPaymentCommentsRequest pendingPaymentCommentsRequest = new PendingPaymentCommentsRequest(
                id, new PendingPaymentCommentsResponseListener(id));
        queue(pendingPaymentCommentsRequest);
    }

    private class PendingPaymentCommentsResponseListener extends ApiResponseListener {

        private Integer sme_id;

        private PendingPaymentCommentsResponseListener(Integer id){
            sme_id = id;
        }

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            String resp = response.toString();
            try {
                String msg = Utils.get(response, "msg");
                if (response != null && response.getString("status")
                        .equalsIgnoreCase("success")) {
//                    new Handler().postDelayed(new Runnable() {
//                        @Override
//                        public void run() {
//                            url = "";
//                            loadDataFromServer(true);
//                        }
//                    }, 100);
                    JSONArray commentsData = response.getJSONArray("data");
                    StringBuilder comment = new StringBuilder(100);
                    for (int i = 0; i < commentsData.length(); i++) {
                        JSONObject obj = commentsData.getJSONObject(i);
                        comment.append(i+1 +". "+ Utils.get(obj, "comment") + "\n");
                    }
                    showCommentsUpdateDialog(comment.toString(), this.sme_id);
//                    Utils.toast("Due Date updated successfully!");
                } else {
                    Utils.toast(msg);
                }

            } catch (JSONException e) {
                e.printStackTrace();
                Utils.toast("Could not update status! Please try again later.");
                Log.e(TAG, "error reading response data:\n" + resp);
            }
        }
    }


    @Override
    public void onPendingPaymentsCommentsItemClicked(CustomerPendingPaymentsParser customerPendingPaymentsParser){
        getPendingPaymentComments(customerPendingPaymentsParser.id);
//        showCommentsUpdateDialog();
    }

    @Override
    public void onPendingPaymentsSetDueDateItemClicked(CustomerPendingPaymentsParser customerPendingPaymentsParser, String date){
        updatePendingPaymentDueDate(customerPendingPaymentsParser.id, date);
    }

    private void showCommentsUpdateDialog(String comments, Integer sme_id) {
        // Prepare and show status update/location dialog
        customerPendingPaymentCommentsDialog = new CustomerPendingPaymentCommentsDialog(this, comments, sme_id, this);
        customerPendingPaymentCommentsDialog.show();
    }

    private void updateCustomerComment(Integer sme_id, String comment) {
        CreateCustomerCommentRequest createCustomerCommentRequest = new CreateCustomerCommentRequest(
                sme_id, comment, new CreateCustomerCommentResponseListener());
        queue(createCustomerCommentRequest);
    }

    private class CreateCustomerCommentResponseListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
//            customerPendingPaymentCommentsDialog.dismiss();
            String resp = response.toString();
            try {
                String msg = Utils.get(response, "msg");
                if (response != null && response.getString("status")
                        .equalsIgnoreCase("success")) {
                    new Handler().postDelayed(new Runnable() {
                        @Override
                        public void run() {
                            url = "";
                            loadDataFromServer(true);
                        }
                    }, 100);
                    Utils.toast("Comment updated successfully!");
                } else {
                    Utils.toast(msg);
                }

            } catch (JSONException e) {
                e.printStackTrace();
                Utils.toast("Could not update status! Please try again later.");
                Log.e(TAG, "error reading response data:\n" + resp);
            }
        }
    }

    @Override
    public void onCustomerPendingPaymentCommentUpdateClicked(Integer sme_id, String comment){
        updateCustomerComment(sme_id, comment);
    }
}
