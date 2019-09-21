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
import android.view.MenuItem;
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
import in.aaho.android.employee.adapter.DeliveredAdapter;
import in.aaho.android.employee.common.ApiResponseListener;
import in.aaho.android.employee.common.BaseActivity;
import in.aaho.android.employee.common.S3Util;
import in.aaho.android.employee.common.Utils;
import in.aaho.android.employee.docs.Document;
import in.aaho.android.employee.docs.DocumentEditFragment;
import in.aaho.android.employee.models.PODData;
import in.aaho.android.employee.other.DeliveredUpdateDialog;
import in.aaho.android.employee.other.ObjectFileUtil;
import in.aaho.android.employee.other.POD_DOCS;
import in.aaho.android.employee.parser.DeliveredParser;
import in.aaho.android.employee.requests.CommentUpdateRequest;
import in.aaho.android.employee.requests.GetDeliveredDataRequest;
import in.aaho.android.employee.requests.PODUploadRequest;
import in.aaho.android.employee.requests.StatusUpdateRequest;
import in.aaho.android.employee.requests.BookingStatusMappingUpdateRequest;

public class DeliveredActivity extends BaseActivity implements
        DeliveredAdapter.IOnDeliveredItemSelectionListener,
        DeliveredUpdateDialog.IOnDeliveredUpdateListener,
        DeliveredAdapter.IOnDeliveredUploadPODClickListener,
        DeliveredAdapter.IOnDeliveredViewPODClickListener,
        DeliveredAdapter.IOnDeliveredSetDueDateListener,
        View.OnClickListener{
    private final String TAG = getClass().getSimpleName();
    private List<DeliveredParser> dataList = new ArrayList<>();
    private ArrayList<String> statusList = new ArrayList<>();

    private ImageView imgMoveToTop;
    private RecyclerView recyclerView;
    private SwipeRefreshLayout refreshLayout;
    private Button btnClearFilterButton;
    private AppCompatEditText filterEditText;
    private ImageView imgSearchButton;
    private LinearLayout linearFilterSection;
    private TextView tvFilterLabel;

    private DeliveredAdapter adapter;
    private TextView emptyView;
    private boolean isDataLoading;
    private String url = null;
    private String roles = null;

    private DeliveredParser mDeliveredParser = null;
    private boolean hasInTransitDataChanged = false;

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
        setContentView(R.layout.activity_delivered);

        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        getSupportActionBar().setTitle("Delivered");

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
        data.putExtra("hasInTransitDataChanged", hasInTransitDataChanged);
        setResult(RESULT_OK,data);
        super.onBackPressed();
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        if (item.getItemId() == android.R.id.home) {
            onBackPressed();
            return true;
        }
        return false;
    }

    private void setDataFromPrevActivity() {
        Bundle bundle = getIntent().getExtras();
        if (bundle != null) {
            if (bundle.containsKey("roles")) {
                roles = bundle.getString("roles");
            }
        }
    }

    private void setupAdapters() {
        adapter = new DeliveredAdapter(this, dataList, roles,
                this,this,
                this, this);
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
                if (recyclerView != null && dataList.size() > 0) {
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
        GetDeliveredDataRequest dataRequest = new GetDeliveredDataRequest(url, params,
                new DeliveredListener(swiped));
        queue(dataRequest, !swiped);
    }

    private class DeliveredListener extends ApiResponseListener {

        private final boolean swiped;

        DeliveredListener(boolean swiped) {
            this.swiped = swiped;
        }

        @Override
        public void onResponse(JSONObject response) {
            Log.i("", response.toString());
            isDataLoading = false;
            if (swiped) {
                dataList.clear();
                refreshLayout.setRefreshing(false);
            } else {
                dismissProgress();
            }
            String resp = response.toString();
            try {
                if (response != null && response.getString("status")
                        .equalsIgnoreCase("success")) {
                    if (response.has("data")) {
                        String nextPageUrl = response.getString("next");
                        if (TextUtils.isEmpty(nextPageUrl) ||
                                nextPageUrl.equalsIgnoreCase("null")) {
                            url = "";
                        } else {
                            url = nextPageUrl;
                        }
                        JSONArray vehiclesData = response.getJSONArray("data");
                        /*dataList.clear();*/
                        dataList.addAll(DeliveredParser.fromJson(vehiclesData));
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
                    Utils.showInfoDialog(DeliveredActivity.this,
                            Utils.getRequestMessage(errorData), Utils.getRequestData(errorData));
                    Log.i(TAG, errorMsg);
                }
            } catch (UnsupportedEncodingException ex) {
                Log.e(TAG, "UnsupportedEncodingException = " + ex.getLocalizedMessage());
            } catch (Exception ex) {
                Log.e(TAG, "Exception = " + ex.getLocalizedMessage());
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

    private void updateBookingStatusMapping(Integer id, Integer chain_id, Integer booking_id, String date) {
        BookingStatusMappingUpdateRequest statusUpdateRequest = new BookingStatusMappingUpdateRequest(
                id, chain_id, booking_id, date, new DeliveredActivity.UpdateBookingStatusMappingResponseListener());
        queue(statusUpdateRequest);
    }

    private class UpdateBookingStatusMappingResponseListener extends ApiResponseListener {

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
                    }, 500);
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

    private void updateStatusRequest(Integer id, String bookingStatus, String comment) {
        StatusUpdateRequest statusUpdateRequest = new StatusUpdateRequest(
                id, bookingStatus, new DeliveredActivity.UpdateStatusResponseListener(comment));
        queue(statusUpdateRequest);
    }

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
                String msg = Utils.get(response, "msg");
                if (response != null && response.getString("status")
                        .equalsIgnoreCase("success")) {
                    hasInTransitDataChanged = true;
                    JSONObject data = response.getJSONObject("data");
                    if (data != null && data.has("id")) {
                        Utils.toast("Status updated successfully!");
                        int bookingStatusMappingId = Integer.valueOf(Utils.get(data, "id"));
                        if (!TextUtils.isEmpty(mComment)) {
                            updateCommentRequest(bookingStatusMappingId, mComment);
                        }

                        // Refresh List from here when status update, we are delaying list
                        // to be refreshed because we might be updating comment
                        new Handler().postDelayed(new Runnable() {
                            @Override
                            public void run() {
                                loadDataFromServer(true);
                            }
                        }, 1000);
                    } else {
                        Utils.toast("Status updated successfully!");
                    }
                } else {
                    Utils.toast(msg);
                }
            } catch (JSONException e) {
                e.printStackTrace();
                Utils.toast("Could not update status! Please try again later.");
                Log.e(TAG, "error reading response data:\n" + resp);
            }
        }

        @Override
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);
            dismissProgress();
            try {
                if (error != null && error.networkResponse != null
                        && error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    JSONObject errorData = new JSONObject(errorMsg);
                    Utils.showInfoDialog(DeliveredActivity.this,
                            Utils.getRequestMessage(errorData), Utils.getRequestData(errorData));
                    Log.i(TAG, errorMsg);
                }
            } catch (UnsupportedEncodingException e) {
                e.printStackTrace();
            } catch (Exception ex) {
                Log.e(TAG, "Exception = " + ex.getLocalizedMessage());
            }
        }
    }

    private void updateCommentRequest(Integer id, String comment) {
        CommentUpdateRequest statusUpdateRequest = new CommentUpdateRequest(
                id, comment, new DeliveredActivity.UpdateCommentResponseListener());
        queue(statusUpdateRequest);
    }

    private class UpdateCommentResponseListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            String resp = response.toString();
            try {
                String msg = Utils.get(response, "msg");
                if (response != null && response.getString("status")
                        .equalsIgnoreCase("success")) {
                    Utils.toast("Comment updated successfully!");
                } else {
                    Utils.toast(msg);
                }
            } catch (JSONException e) {
                e.printStackTrace();
                Utils.toast("Could not update comment! Please try again later.");
                Log.e(TAG, "error reading response data:\n" + resp);
            }
        }

        @Override
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);
            dismissProgress();
            try {
                if (error != null && error.networkResponse != null
                        && error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    JSONObject errorData = new JSONObject(errorMsg);
                    Utils.showInfoDialog(DeliveredActivity.this,
                            Utils.getRequestMessage(errorData), Utils.getRequestData(errorData));
                    Log.i(TAG, errorMsg);
                }
            } catch (UnsupportedEncodingException e) {
                e.printStackTrace();
            } catch (Exception ex) {
                Log.e(TAG, "Exception = " + ex.getLocalizedMessage());
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
                    if (isDataLoading)
                        return;
                    else {
                        if (!TextUtils.isEmpty(url)) {
                            isDataLoading = true;
                            loadDataFromServer(false);
                        }
                    }
                }
            }
        });
    }

    @Override
    public void onDeliveredItemSelected(DeliveredParser deliveredParser) {
        /*Show dialog from here open a dialogue box with fields
            1. Status - Options (booking_status_current and
                        primary_succeeded_booking_status)
            2. Comment - Text Field with suggestion icon on right side
                         On Click of suggestion icon, show comment suggestions (Previous
                         trip incomplete, On the way to loading point, Waiting as loading point,
                         Loading ongoing). The selected suggestion can be auto filled in Text Field.
                         User can enter text without referring suggestions
            3. Location - Text Field of city, district and country */
        mDeliveredParser = deliveredParser;
        statusList.clear(); // Reset status list first
        if (deliveredParser != null) {
            if(!TextUtils.isEmpty(deliveredParser.bookingStatusCurrent)) {
                statusList.add(deliveredParser.bookingStatusCurrent);
            }
            if(!TextUtils.isEmpty(deliveredParser.primarySucceededBookingStatus)
                    && !deliveredParser.bookingStatusCurrent.equalsIgnoreCase("complete")) {
                statusList.add(deliveredParser.primarySucceededBookingStatus);
            }
            // Show dialog only if status list has some data
            if(statusList.size() > 0)
                showUpdateStatusDialog();
        }
    }

    @Override
    public void onDeliveredSetDateClicked(DeliveredParser deliveredParser, String date){
        mDeliveredParser = deliveredParser;
        updateBookingStatusMapping(mDeliveredParser.bookingStatusMappingId, mDeliveredParser.bookingStatusMappingChainId,
                mDeliveredParser.id, date);
    }


    @Override
    public void onDeliveredUpdateClickedListener(String status, String comment) {
        if(!TextUtils.isEmpty(status) && status.equalsIgnoreCase(mDeliveredParser.bookingStatusCurrent)) {
//        if(TextUtils.isEmpty(status) || status.equalsIgnoreCase("loaded")) {
            // To update the status & comment if status succeed
            if(!TextUtils.isEmpty(comment)) {
                // Update comment from here
                updateCommentRequest(mDeliveredParser.bookingStatusMappingId,comment);
            }
        } else {
            updateStatusRequest(mDeliveredParser.id,status,comment);
        }
    }

    @Override
    public void onDeliveredUploadPODClicked(DeliveredParser deliveredParser) {
        launchUploadDialog(null,deliveredParser);
    }

    @Override
    public void onDeliveredViewPODClicked(DeliveredParser deliveredParser) {
        // launch view pod activity from here
        if(deliveredParser.getPod_docsArrayList() != null &&
                deliveredParser.getPod_docsArrayList().size() > 0) {
            ObjectFileUtil<ArrayList<POD_DOCS>> objectFileUtil = new ObjectFileUtil<>(
                    this,"PodDocList");
            objectFileUtil.put(deliveredParser.getPod_docsArrayList());
            startActivity(new Intent(this, ViewPODActivity.class));
        } else {
            Utils.toast("No POD available to display!");
        }
    }

    public static final String title = "Upload POD";

    private void launchUploadDialog(Document doc, final DeliveredParser deliveredParser) {
        DocumentEditFragment.ResultListenerForPOD listener = new DocumentEditFragment.ResultListenerForPOD() {
            @Override
            public void onResult(String lrNumber, String url, String thumbUrl, String bucketname,
                                 String foldername, String filename, String uuid,
                                 String displayUrl, ArrayList<PODData> podDataArrayList) {
                if(TextUtils.isEmpty(lrNumber)) {
                    toast("POD Not uploaded!");
                } else {
                    makePodUploadEntryRequest(lrNumber,url,thumbUrl,bucketname,foldername,filename,
                            uuid,displayUrl,podDataArrayList,deliveredParser);
                }
                Log.i(TAG,"onResult"+lrNumber);
            }
        };

        ArrayList<String> lrList = new ArrayList<>();
        if (!TextUtils.isEmpty(deliveredParser.lrNumber)) {
            String[] lrNumberList = deliveredParser.lrNumber.split("\n");
            // Add selection options only when there are more than two lr numbers
            if(lrNumberList.length > 2)
                lrList.add("Select");

            for (int i = 0; i < lrNumberList.length; i++) {
                lrList.add(lrNumberList[i]);
            }
        }

        DocumentEditFragment.Builder builder = new DocumentEditFragment
                .Builder(this, title, lrList, listener);


        //builder.setHints(idHint, null);
        builder.setValues(doc);
        builder.setEnabled(false, false, false,
                false, false, false);
        builder.setUploadId(S3Util.S3_UPLOAD_ID_FOR_POD_DIR);
        builder.build();
    }

    private void showUpdateStatusDialog() {
        // Prepare and show status update/location dialog
        DeliveredUpdateDialog deliveredUpdateDialog = new DeliveredUpdateDialog(this,
                statusList, this);
        deliveredUpdateDialog.show();
    }

    public void setMoveToTopVisibility(int scrollPosition) {
        if (scrollPosition < 6) {
            imgMoveToTop.setVisibility(View.GONE);
        } else {
            imgMoveToTop.setVisibility(View.VISIBLE);
        }
    }

    private void makePodUploadEntryRequest(String lr_number, String url, String thumbUrl,
                                           String bucketname, String foldername,
                                           String filename, String uuid, String displayUrl,
                                           ArrayList<PODData> podDataArrayList,
                                           DeliveredParser deliveredParser) {
        PODUploadRequest podUploadRequest = new PODUploadRequest(lr_number,url,thumbUrl,
                bucketname,foldername,filename,uuid,displayUrl,podDataArrayList,
                new PodUploadListener(deliveredParser));
        queue(podUploadRequest);
    }

    private class PodUploadListener extends ApiResponseListener {
        DeliveredParser deliveredParser;
        public PodUploadListener(DeliveredParser deliveredParser) {
            this.deliveredParser = deliveredParser;
        }

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            Utils.toast("POD is uploaded!");
            // Refresh List from here when status update, we are delaying list
            // to be refreshed because we might be updating comment
            new Handler().postDelayed(new Runnable() {
                @Override
                public void run() {
                    url = "";
                    loadDataFromServer(true);
                }
            }, 1000);

            /** NOTE: Update status is now disabled from app side handling from backend
             *  If want to enable again then uncomment below code */
            /*// Update status if pod doc size 0
            if(deliveredParser.getPod_docsArrayList() != null &&
                    deliveredParser.getPod_docsArrayList().size() == 0) {
                updateStatusRequest(deliveredParser.id,"pod_uploaded","");
            }*/
        }

        /*@Override
        public void onError() {
            dismissProgress();
            Utils.toast("POD is Not uploaded!");
        }*/

        @Override
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);
            dismissProgress();
            try {
                if (error != null && error.networkResponse != null
                        && error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    JSONObject errorData = new JSONObject(errorMsg);
                    Utils.showInfoDialog(DeliveredActivity.this,
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
