package in.aaho.android.ownr.transaction;

import android.app.ProgressDialog;
import android.content.Context;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.v4.app.Fragment;
import android.support.v4.widget.SwipeRefreshLayout;
import android.support.v7.widget.DefaultItemAnimator;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.text.TextUtils;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.RelativeLayout;
import android.widget.TextView;

import com.android.volley.Request;
import com.android.volley.VolleyError;

import org.greenrobot.eventbus.EventBus;
import org.greenrobot.eventbus.Subscribe;
import org.greenrobot.eventbus.ThreadMode;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.adapter.PODPendingAdapter;
import in.aaho.android.ownr.common.ApiResponseListener;
import in.aaho.android.ownr.common.MainApplication;
import in.aaho.android.ownr.common.Utils;
import in.aaho.android.ownr.data.ConfirmedTransactionData;
import in.aaho.android.ownr.parser.BookingDataParser;
import in.aaho.android.ownr.requests.GetPODDeliveredDataRequests;


public class PODDeliveredFragmentNew extends Fragment {
    private String TAG = getClass().getSimpleName();
    private TextView textViewNumberOfBooking, textViewTotalAmount, textViewPaidAmount,
            textViewBalanceAmount;
    private ImageView imgMoveToTop;
    private static RelativeLayout rlTripDetailsMainContent;
    private RecyclerView recyclerView;
    private SwipeRefreshLayout refreshLayout;
    private PODPendingAdapter mAdapter;
    private ProgressDialog progress;

    private TextView emptyView;
    private boolean isDataLoading;
    private String url = null;

    private List<ConfirmedTransactionData> dataList = new ArrayList<>();

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View rootView = inflater.inflate(R.layout.fragment_confirmed, container,
                false);
        setViewVariables(rootView);
        setupAdapters();

        return rootView;
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
    }

    @Override
    public void onAttach(Context context) {
        super.onAttach(context);
    }

    @Override
    public void onResume() {
        super.onResume();
        Log.e(TAG, "PODDelivered");
        boolean isSummaryVisible = ((TransactionNewActivity)getActivity()).isSummaryVisible();
        setSummaryVisibility(isSummaryVisible);
        if (dataList.isEmpty()) {
            loadDataFromServer();
        }
    }

    @Override
    public void onStart() {
        super.onStart();
        EventBus.getDefault().register(this);
    }

    @Override
    public void onStop() {
        super.onStop();
        EventBus.getDefault().unregister(this);
    }

    @Override
    public void onPause() {
        super.onPause();
    }

    @Override
    public void onDetach() {
        super.onDetach();
    }

    private void setupAdapters() {
        mAdapter = new PODPendingAdapter(getActivity(), dataList);
        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getActivity());
        recyclerView.setLayoutManager(mLayoutManager);
        recyclerView.setItemAnimator(new DefaultItemAnimator());
        recyclerView.setAdapter(mAdapter);
        mAdapter.notifyDataSetChanged();
        setRecyclerScroll();
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
                            loadDataFromServer();
                        }
                    }
                }
            }
        });
    }

    private void setClickListeners() {
        refreshLayout.setOnRefreshListener(new SwipeRefreshLayout.OnRefreshListener() {
            @Override
            public void onRefresh() {
                url = "";
                loadDataFromServer();
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

    public static void setSummaryVisibility(boolean visibility) {
        if(rlTripDetailsMainContent != null) {
            if (visibility) {
                rlTripDetailsMainContent.setVisibility(View.VISIBLE);
            } else {
                rlTripDetailsMainContent.setVisibility(View.GONE);
            }
        }
    }

    private void setViewVariables(View view) {
        rlTripDetailsMainContent = view.findViewById(R.id.rlTripDetailsMainContent);
        textViewNumberOfBooking = view.findViewById(R.id.tvNumberOfBookingsValue);
        textViewTotalAmount = view.findViewById(R.id.tvTotalAmountValue);
        textViewPaidAmount = view.findViewById(R.id.tvPaidValue);
        textViewBalanceAmount = view.findViewById(R.id.tvBalanceValue);
        recyclerView = view.findViewById(R.id.recycler_view_confirmed_transaction);
        refreshLayout = view.findViewById(R.id.swipe_refresh_layout);
        emptyView = view.findViewById(R.id.empty_view);
        /*imgMoveToTop = view.findViewById(R.id.imgMoveToTop);*/
    }

    private void loadDataFromServer() {
        Map<String, String> params = new HashMap<String, String>();
        String searchQuery = ((TransactionNewActivity)getActivity()).getSearchQuery();
        if (!TextUtils.isEmpty(searchQuery)) {
            searchQuery = searchQuery.replace(" ", "+");
            params.put("search", searchQuery);
        }
        String vehicleId = ((TransactionNewActivity)getActivity()).getVehicleId();
        if (!TextUtils.isEmpty(vehicleId)) {
            params.put("vehicle_id", vehicleId);
        }
        String fromDate = ((TransactionNewActivity)getActivity()).getFromDate();
        if (!TextUtils.isEmpty(fromDate)) {
            params.put("shipment_date_between_0", fromDate);
        }
        String toDate = ((TransactionNewActivity)getActivity()).getToDate();
        if (!TextUtils.isEmpty(toDate)) {
            params.put("shipment_date_between_1", toDate);
        }
        GetPODDeliveredDataRequests dataRequest = new GetPODDeliveredDataRequests(url, params,
                new PODDeliveredListener());
        queue(dataRequest, true);
    }

    private class PODDeliveredListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            Log.i("", response.toString());
            isDataLoading = false;
            dismissProgress();
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
                        JSONArray data = response.getJSONArray("data");
                        /*dataList.clear();*/
                        if (data != null && data.length() > 0) {
                            BookingDataParser bookingDataParser = new BookingDataParser(data);
                            int position = 0;
                            if(dataList.size() == 0) {
                                dataList.addAll(bookingDataParser.getConfirmedTransactionDataArrayList());
                            } else {
                                position = dataList.size();
                                dataList.addAll(dataList.size(),bookingDataParser.getConfirmedTransactionDataArrayList());
                            }
                            mAdapter = new PODPendingAdapter(getActivity(), dataList);
                            recyclerView.setAdapter(mAdapter);
                            mAdapter.notifyDataSetChanged();
                            recyclerView.scrollToPosition(position);
                        }

                        if (response.has("summary")) {
                            // retrieve & set summary data
                            JSONObject summary = response.getJSONObject("summary");
                            setSummaryData(summary);
                        }

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
                Utils.toast("error reading response data:\n" + resp);
            }
        }

        @Override
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);
            isDataLoading = false;
            dismissProgress();
            dataList.clear();
            setEmptyViewVisibility();
            try {
                if (error != null && error.networkResponse != null
                        && error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    JSONObject errorData = new JSONObject(errorMsg);
                    Utils.showInfoDialog(getActivity(), Utils.getRequestMessage(errorData),
                            Utils.getRequestData(errorData));
                    Log.i(TAG, errorMsg);
                }
            } catch (UnsupportedEncodingException ex) {
                Log.e(TAG, "UnsupportedEncodingException = " + ex.getLocalizedMessage());
            } catch (Exception ex) {
                Log.e(TAG, "Exception = " + ex.getLocalizedMessage());
            }
        }
    }

    /** set summary data */
    private void setSummaryData(JSONObject summary) {
        try {
            if (summary != null && summary.has("completed_booking")) {
                JSONObject podPendingData = summary.getJSONObject("delivered_pod");
                if (podPendingData != null) {
                    textViewNumberOfBooking.setText(Utils.get(podPendingData, "number_of_booking"));
                    textViewTotalAmount.setText(Utils.get(podPendingData, "total_amount"));
                    textViewBalanceAmount.setText(Utils.get(podPendingData, "balance"));
                    textViewPaidAmount.setText(Utils.get(podPendingData, "amount_paid"));
                }
            }
        } catch (JSONException e) {
            e.printStackTrace();
            Utils.toast("error reading summary data:\n" + e.getLocalizedMessage());
        } catch (Exception e) {
            e.printStackTrace();
            Utils.toast("error reading summary data:\n" + e.getLocalizedMessage());
        }
    }

    /** set empty view visibility */
    private void setEmptyViewVisibility() {
        if (dataList.size() == 0) {
            /*emptyView.setVisibility(View.VISIBLE);*/
            recyclerView.setVisibility(View.GONE);
        } else {
            /*emptyView.setVisibility(View.GONE);*/
            recyclerView.setVisibility(View.VISIBLE);
        }
    }

    public void queue(Request<?> request) {
        queue(request, true);
    }

    public void queue(Request<?> request, boolean progress) {
        MainApplication.queueRequest(request);
        if (progress) {
            if (!getActivity().isFinishing())
                showProgress();
        }
    }

    private void showProgress() {
        progress = new ProgressDialog(getActivity());
        progress.setTitle(R.string.progress_title);
        progress.setMessage(getActivity().getString(R.string.progress_msg));
        progress.setCanceledOnTouchOutside(false);
        progress.show();
    }

    private void dismissProgress() {
        if (progress != null) {
            progress.dismiss();
        }
    }

    @Subscribe(threadMode = ThreadMode.MAIN)
    public void onMessageEvent(MessageEvent event) {
        final String dataReceived = "onBusDataReceived, searchQuery = "+event.searchQuery;
        Log.i(TAG,dataReceived);
        getActivity().runOnUiThread(new Runnable() {
            @Override
            public void run() {
                url = "";
                dataList.clear();
                loadDataFromServer();
            }
        });
    }

}
