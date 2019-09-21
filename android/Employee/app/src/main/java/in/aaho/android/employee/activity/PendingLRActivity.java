package in.aaho.android.employee.activity;

import android.os.Bundle;
import android.support.v4.widget.SwipeRefreshLayout;
import android.support.v7.widget.DefaultItemAnimator;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.support.v7.widget.Toolbar;
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
import java.util.ArrayList;
import java.util.List;

import in.aaho.android.employee.R;
import in.aaho.android.employee.adapter.PendingLRAdapter;
import in.aaho.android.employee.common.ApiResponseListener;
import in.aaho.android.employee.common.BaseActivity;
import in.aaho.android.employee.common.Utils;
import in.aaho.android.employee.other.StatusUpdateDialog;
import in.aaho.android.employee.parser.PendingLRParser;
import in.aaho.android.employee.requests.CommentUpdateRequest;
import in.aaho.android.employee.requests.GetPendingLRDataRequest;
import in.aaho.android.employee.requests.StatusUpdateRequest;

public class PendingLRActivity extends BaseActivity implements
        PendingLRAdapter.IOnPendingLRItemSelectionListener,
        StatusUpdateDialog.IOnStatusUpdateListener {
    private final String TAG = getClass().getSimpleName();
    private List<PendingLRParser> dataList = new ArrayList<>();
    private ArrayList<String> statusList = new ArrayList<>();

    private ImageView imgMoveToTop;
    private RecyclerView recyclerView;
    private SwipeRefreshLayout refreshLayout;

    private PendingLRAdapter adapter;
    private TextView emptyView;
    private boolean isDataLoading;
    private String url = null;
    private String roles = null;

    private PendingLRParser mPendingLRParser = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_pending_lr);

        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        getSupportActionBar().setTitle("Pending LR");

        setViewVariables();
        setClickListeners();
        setDataFromPrevActivity();
        setupAdapters();
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (dataList.isEmpty()) {
            loadDataFromServer(false);
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
        adapter = new PendingLRAdapter(this,dataList,roles,this);
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
    }

    private void loadDataFromServer(boolean swiped) {
        GetPendingLRDataRequest dataRequest = new GetPendingLRDataRequest(url,
                new PendingLRListener(swiped));
        queue(dataRequest, !swiped);
    }

    private class PendingLRListener extends ApiResponseListener {

        private final boolean swiped;

        PendingLRListener(boolean swiped) {
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
                        dataList.addAll(PendingLRParser.fromJson(vehiclesData));
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
                    Utils.showInfoDialog(PendingLRActivity.this,
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

    private void updateStatusRequest(Integer id, String bookingStatus, String comment) {
        StatusUpdateRequest statusUpdateRequest = new StatusUpdateRequest(
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
                        if(data != null && data.has("id")) {
                            int bookingStatusMappingId = Integer.valueOf(Utils.get(data, "id"));
                            updateCommentRequest(bookingStatusMappingId, mComment);
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
                    Utils.showInfoDialog(PendingLRActivity.this,
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

    private void updateCommentRequest(Integer id, String comment) {
        CommentUpdateRequest statusUpdateRequest = new CommentUpdateRequest(
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
                    Utils.showInfoDialog(PendingLRActivity.this,
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
    public void onPendingLRItemSelected(PendingLRParser pendingLRParser) {
        /*Show dialog from here open a dialogue box with fields
            1. Status - Options (booking_status_current and
                        primary_succeeded_booking_status)
            2. Comment - Text Field with suggestion icon on right side
                         On Click of suggestion icon, show comment suggestions (Previous
                         trip incomplete, On the way to loading point, Waiting as loading point,
                         Loading ongoing). The selected suggestion can be auto filled in Text Field.
                         User can enter text without referring suggestions*/
        mPendingLRParser = pendingLRParser;
        statusList.clear(); // Reset status list first
        if(pendingLRParser != null) {
            // NOTE: if bookingCurrentStatus is not equal to loaded then only show confirmed
            // option in drop down list

            if(!TextUtils.isEmpty(pendingLRParser.bookingStatusCurrent)) {
                statusList.add(pendingLRParser.bookingStatusCurrent);
            }
            if(!TextUtils.isEmpty(pendingLRParser.primarySucceededBookingStatus)
                    && !pendingLRParser.bookingStatusCurrent.equalsIgnoreCase("loaded")) {
                statusList.add(pendingLRParser.primarySucceededBookingStatus);
            }


            /*if(!TextUtils.isEmpty(pendingLRParser.bookingStatusCurrent)
                    && !pendingLRParser.bookingStatusCurrent.equalsIgnoreCase("loaded")) {
                statusList.add(pendingLRParser.bookingStatusCurrent);
            }
            if(!TextUtils.isEmpty(pendingLRParser.primarySucceededBookingStatus)
                && pendingLRParser.bookingStatusCurrent.equalsIgnoreCase("loaded")) {
                statusList.add(pendingLRParser.primarySucceededBookingStatus);
            }*/
            // Show dialog only if status list has some data
            if(statusList.size() > 0)
                showUpdateStatusDialog();
        }
    }

    @Override
    public void onStatusUpdateListener(String status, String comment) {
        if(!TextUtils.isEmpty(status) && status.equalsIgnoreCase(mPendingLRParser.bookingStatusCurrent)) {
//        if(TextUtils.isEmpty(status) || status.equalsIgnoreCase("loaded")) {
            // To update the status & comment if status succeed
            if(!TextUtils.isEmpty(comment)) {
                // Update comment from here
                updateCommentRequest(mPendingLRParser.bookingStatusMappingId,comment);
            }
        } else {
            updateStatusRequest(mPendingLRParser.id,status,comment);
        }
    }

    private void showUpdateStatusDialog() {
        // prepare and show status update dialog
        StatusUpdateDialog statusUpdateDialog = new StatusUpdateDialog(this,
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

}
