package in.aaho.android.employee.activity;

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
import android.net.Uri;

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
import in.aaho.android.employee.adapter.PendingPaymentsAdapter;
import in.aaho.android.employee.common.ApiResponseListener;
import in.aaho.android.employee.common.BaseActivity;
import in.aaho.android.employee.common.Utils;
import in.aaho.android.employee.other.PendingPaymentUpdateDialog;
import in.aaho.android.employee.parser.PendingPaymentsParser;
import in.aaho.android.employee.requests.BulkCommentUpdateRequest;
import in.aaho.android.employee.requests.BulkStatusUpdateRequest;
import in.aaho.android.employee.requests.GetPendingPaymentDataRequest;

public class PendingPaymentsActivity extends BaseActivity implements
        PendingPaymentsAdapter.IOnPendingPaymentsUpdateListener,
        PendingPaymentsAdapter.IOnPendingPaymentsViewInvoiceListener,
        PendingPaymentUpdateDialog.IOnStatusUpdateListener,
        View.OnClickListener{
    private final String TAG = getClass().getSimpleName();
    private List<PendingPaymentsParser> dataList = new ArrayList<>();
    private ArrayList<String> statusList = new ArrayList<>();

    private ImageView imgMoveToTop;
    private RecyclerView recyclerView;
    private SwipeRefreshLayout refreshLayout;

    private Button btnClearFilterButton;
    private AppCompatEditText filterEditText;
    private ImageView imgSearchButton;
    private LinearLayout linearFilterSection;
    private TextView tvFilterLabel;

    private PendingPaymentsAdapter adapter;
    private TextView emptyView;
    private boolean isDataLoading;
    private String url = null;
    private Integer id = null;

    private PendingPaymentsParser mPendingPaymentsParser = null;
    /** Has data changed */
    private boolean hasDataChanged = false;

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
        setContentView(R.layout.activity_pending_payments);

        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        getSupportActionBar().setTitle("Pending Payments");

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
    public void onBackPressed() {
        Intent data = new Intent();
        data.putExtra("hasDataChanged", hasDataChanged);
        setResult(RESULT_OK,data);
        super.onBackPressed();
    }

    private void setDataFromPrevActivity() {
        Bundle bundle = getIntent().getExtras();
        if(bundle != null) {
            if(bundle.containsKey("id")) {
                id = bundle.getInt("id");
            }
        }
    }

    private void setupAdapters() {
        adapter = new PendingPaymentsAdapter(this,dataList,
                this,this);
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
        params.put("customer_id", String.valueOf(id));
        String searchQuery = this.getSearchQuery();
        if (!TextUtils.isEmpty(searchQuery)) {
            searchQuery = searchQuery.replace(" ", "+");
            params.put("search", searchQuery);
        }

        GetPendingPaymentDataRequest dataRequest = new GetPendingPaymentDataRequest(url,
                params, new PendingPaymentsListener(swiped));
        queue(dataRequest, !swiped);
    }

    private class PendingPaymentsListener extends ApiResponseListener {

        private final boolean swiped;

        PendingPaymentsListener(boolean swiped) {
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
                        dataList.addAll(PendingPaymentsParser.fromJson(vehiclesData));
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
                    Utils.showInfoDialog(PendingPaymentsActivity.this,
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

    private void updateStatusRequest(String id, String bookingStatus, String comment) {
        BulkStatusUpdateRequest statusUpdateRequest = new BulkStatusUpdateRequest(
                id, bookingStatus, new UpdateStatusResponseListener(comment));
        queue(statusUpdateRequest);
    }

    private String mStatusCommentMsg = "";
    private class UpdateStatusResponseListener extends ApiResponseListener {
        private String mComment;
        public UpdateStatusResponseListener(String comment) {
            this.mComment = comment;
        }

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            String resp = response.toString();
            try {
                String msg = Utils.get(response,"msg");
                if(response != null && response.getString("status")
                        .equalsIgnoreCase("success")) {
                    if(TextUtils.isEmpty(mComment)) {
                        Utils.toast("Status updated successfully!");
                    }
                    else {
                        mStatusCommentMsg = "Status ";
                        JSONObject data = response.getJSONObject("data");
                        String bookingStatusMappingId = "";
                        if(data != null && data.has("id")) {
                            JSONArray jsonArray = data.getJSONArray("id");
                            if(jsonArray != null && jsonArray.length() > 0) {
                                for (int count = 0; count < jsonArray.length(); count++) {
                                    if(TextUtils.isEmpty(bookingStatusMappingId)) {
                                        bookingStatusMappingId = String.valueOf(jsonArray.getInt(count));
                                    } else {
                                        bookingStatusMappingId = bookingStatusMappingId + ","
                                                +String.valueOf(jsonArray.getInt(count));
                                    }
                                }
                            }

                            if(!TextUtils.isEmpty(mComment)) {
                                // Update comment
                                updateCommentRequest(bookingStatusMappingId, mComment);
                            }

                            // Refresh List from here when status update, we are delaying list
                            // to be refreshed because we may be updating comment
                            new Handler().postDelayed(new Runnable() {
                                @Override
                                public void run() {
                                    hasDataChanged = true;
                                    loadDataFromServer(true);
                                }
                            }, 1000);
                        } else {
                            Utils.toast("Status updated successfully!");
                        }
                    }
                } else {
                    Utils.toast(msg);
                }
            } catch (JSONException e) {
                e.printStackTrace();
                Utils.toast("Could not update status! Please try again later.");
                Log.e(TAG,"error reading response data:\n" + resp);
            }
        }

        @Override
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);
            dismissProgress();
            try {
                mStatusCommentMsg = "";
                if (error != null && error.networkResponse != null
                        && error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    JSONObject errorData = new JSONObject(errorMsg);
                    Utils.showInfoDialog(PendingPaymentsActivity.this,
                            Utils.getRequestMessage(errorData),Utils.getRequestData(errorData));
                    Log.i(TAG, errorMsg);
                }
            } catch (UnsupportedEncodingException e) {
                e.printStackTrace();
            } catch (Exception ex) {
                Log.e(TAG,"Exception = "+ex.getLocalizedMessage());
            }
        }
    }

    private void updateCommentRequest(String id, String comment) {
        BulkCommentUpdateRequest statusUpdateRequest = new BulkCommentUpdateRequest(
                id, comment, new UpdateCommentResponseListener());
        queue(statusUpdateRequest);
    }

    private class UpdateCommentResponseListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            String resp = response.toString();
            try {
                String msg = Utils.get(response,"msg");
                if(response != null && response.getString("status")
                        .equalsIgnoreCase("success")) {
                    if(TextUtils.isEmpty(mStatusCommentMsg)) {
                        mStatusCommentMsg = "Comment updated successfully!";
                    } else {
                        mStatusCommentMsg = mStatusCommentMsg + "& comment updated successfully!";
                    }
                    Utils.toast(mStatusCommentMsg);
                } else {
                    Utils.toast(msg);
                }
                mStatusCommentMsg = ""; // Reset msg
            } catch (JSONException e) {
                e.printStackTrace();
                Utils.toast("Could not update comment! Please try again later.");
                Log.e(TAG,"error reading response data:\n" + resp);
            }
        }

        @Override
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);
            dismissProgress();
            try {
                mStatusCommentMsg = "";
                if (error != null && error.networkResponse != null
                        && error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    JSONObject errorData = new JSONObject(errorMsg);
                    Utils.showInfoDialog(PendingPaymentsActivity.this,
                            Utils.getRequestMessage(errorData),Utils.getRequestData(errorData));
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

    @Override
    public void onPendingPaymentsUpdateClicked(PendingPaymentsParser pendingPaymentsParser) {
        /*Show dialog from here open a dialogue box with fields
            1. Status - Options (booking_status_current and
                        primary_succeeded_booking_status)
            2. Comment - Text Field with suggestion icon on right side
                         On Click of suggestion icon, show comment suggestions (Previous
                         trip incomplete, On the way to loading point, Waiting as loading point,
                         Loading ongoing). The selected suggestion can be auto filled in Text Field.
                         User can enter text without referring suggestions*/
        mPendingPaymentsParser = pendingPaymentsParser;
        statusList.clear(); // Reset status list first
        if(pendingPaymentsParser != null) {
            // NOTE: if secondarySucceededBookingStatus is not equal to inward_followup_completed then only show
            // bookinStatusCurrent option in drop down list

            if(!TextUtils.isEmpty(pendingPaymentsParser.bookingStatusCurrent)) {
                statusList.add(pendingPaymentsParser.bookingStatusCurrent);
            }
            if(!TextUtils.isEmpty(pendingPaymentsParser.secondarySucceededBookingStatus)
                    && !pendingPaymentsParser.bookingStatusCurrent.equalsIgnoreCase("inward_followup_completed")) {
                statusList.add(pendingPaymentsParser.secondarySucceededBookingStatus);
            }

            // Show dialog only if status list has some data
            if(statusList.size() > 0)
                showUpdateStatusDialog();
        }
    }

    private void showUpdateStatusDialog() {
        // prepare and show status update dialog
        PendingPaymentUpdateDialog statusUpdateDialog = new PendingPaymentUpdateDialog(this,
                statusList,this);
        statusUpdateDialog.show();
    }

    public void setMoveToTopVisibility(int scrollPosition) {
        if(scrollPosition < 6) {
            imgMoveToTop.setVisibility(View.GONE);
        } else {
            imgMoveToTop.setVisibility(View.VISIBLE);
        }
    }

    @Override
    public void onStatusUpdateListener(String status, String comment) {
        if(!TextUtils.isEmpty(status) && status.equalsIgnoreCase(mPendingPaymentsParser.bookingStatusCurrent)) {
            if(!TextUtils.isEmpty(comment)) {
                // Update comment from here
                updateCommentRequest(mPendingPaymentsParser.bookingStatusMappingIds,comment);
            }
        } else {
            updateStatusRequest(mPendingPaymentsParser.manualBookingIds,status,comment);
        }
    }

    @Override
    public void onPendingPaymentsViewInvoiceClicked(PendingPaymentsParser pendingPaymentsParser) {
        // Open pdf file to view
        /*String pdfFileUrl = "http://www.pdfpdf.com/samples/Sample1.PDF";*/ // Test pdf sample
        String pdfFileUrl = pendingPaymentsParser.pdfFileUrl;
        /* For Using In App PDF viewer */
//        Intent pdfIntent = new Intent(this,PDFViewerActivity.class);
//        pdfIntent.putExtra("pdfFileUrl",pdfFileUrl);
//        startActivity(pdfIntent);
        /* For using browser PDF Viewer */
        Intent browserIntent = new Intent(Intent.ACTION_VIEW, Uri.parse(pdfFileUrl));
        startActivity(browserIntent);
    }
}
