package in.aaho.android.ownr.transaction;

import android.content.Context;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.v4.app.Fragment;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.text.TextUtils;
import android.util.Log;
import android.view.GestureDetector;
import android.view.LayoutInflater;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.widget.RelativeLayout;
import android.widget.TextView;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.adapter.InTransitTransactionAdapter;
import in.aaho.android.ownr.common.Utils;
import in.aaho.android.ownr.data.InTransitTransactionData;
import in.aaho.android.ownr.parser.BookingDataParser;


public class InTransitFragment extends Fragment {

    TextView textViewNumberOfBooking,textViewTotalAmount,
            textViewPaidAmount,textViewBalanceAmount;
    InTransitTransactionAdapter mAdapter;
    ArrayList<InTransitTransactionData> mDataList;
    RecyclerView recyclerView;
    RelativeLayout rlTripDetailsMainContent;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View rootView = inflater.inflate(R.layout.fragment_in_transit, container, false);
        findViews(rootView);
        SetupRecycleView();
        /*filter(Utils.searchText);
        filterWithDateRange(Utils.fromDate,Utils.toDate);*/

        return rootView;
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        setData();
    }

    /** find/bind data to views */
    void findViews(View view) {
        rlTripDetailsMainContent = view.findViewById(R.id.rlTripDetailsMainContent);
        textViewNumberOfBooking = view.findViewById(R.id.tvNumberOfBookingsValue);
        textViewTotalAmount = view.findViewById(R.id.tvTotalAmountValue);
        textViewPaidAmount = view.findViewById(R.id.tvPaidValue);
        textViewBalanceAmount = view.findViewById(R.id.tvBalanceValue);
        textViewNumberOfBooking = view.findViewById(R.id.tvNumberOfBookingsValue);
        textViewTotalAmount = view.findViewById(R.id.tvTotalAmountValue);
        recyclerView = view.findViewById(R.id.recycler_view_in_transit_transaction);
    }

    void SetupRecycleView() {
        recyclerView.setHasFixedSize(true);
        LinearLayoutManager layoutManager = new LinearLayoutManager(getActivity());
        layoutManager.setOrientation(LinearLayoutManager.VERTICAL);
        recyclerView.setLayoutManager(layoutManager);
        setRecyclerScroll();
    }

    public interface ClickListener {
        void onClick(View view, int position);

        void onLongClick(View view, int position);
    }

    public static class RecyclerTouchListener implements RecyclerView.OnItemTouchListener {

        private GestureDetector gestureDetector;
        private ClickListener clickListener;

        public RecyclerTouchListener(Context context, final RecyclerView recyclerView, final ClickListener clickListener) {
            this.clickListener = clickListener;
            gestureDetector = new GestureDetector(context, new GestureDetector.SimpleOnGestureListener() {
                @Override
                public boolean onSingleTapUp(MotionEvent e) {
                    return true;
                }

                @Override
                public void onLongPress(MotionEvent e) {
                    View child = recyclerView.findChildViewUnder(e.getX(), e.getY());
                    if (child != null && clickListener != null) {
                        clickListener.onLongClick(child, recyclerView.getChildPosition(child));
                    }
                }
            });
        }

        @Override
        public boolean onInterceptTouchEvent(RecyclerView rv, MotionEvent e) {

            View child = rv.findChildViewUnder(e.getX(), e.getY());
            if (child != null && clickListener != null && gestureDetector.onTouchEvent(e)) {
                clickListener.onClick(child, rv.getChildPosition(child));
            }
            return false;
        }

        @Override
        public void onTouchEvent(RecyclerView rv, MotionEvent e) {
        }

        @Override
        public void onRequestDisallowInterceptTouchEvent(boolean disallowIntercept) {

        }
    }

    /** filter the given list with given date range and return the filtered list
     * @param fromDate from date
     * @param toDate to date
     */
    private List<InTransitTransactionData> filterListWithDateRange(List<InTransitTransactionData> listToFilter,
                                                                   String fromDate, String toDate) {
        List<InTransitTransactionData> inTransitTransactionData = new ArrayList<>();
        try {
            Date dtFromDate = Utils.parseShipmentDate(fromDate);
            Date dtToDate = Utils.parseShipmentDate(toDate);
            if(listToFilter != null && listToFilter.size() > 0) {
                for (int iCount = 0; iCount < listToFilter.size() ; iCount++) {
                    String shipmentDate = listToFilter.get(iCount).getShipmentDate();
                    Date dtShipmentDate = Utils.parseShipmentDate(shipmentDate);
                    if( (dtShipmentDate.compareTo(dtFromDate) < 0)
                            || (dtShipmentDate.compareTo(dtToDate) > 0)) {
                        // not within range
                    } else {
                        // within range
                        inTransitTransactionData.add(listToFilter.get(iCount));
                    }
                }
            }

        } catch (Exception ex) {
            Log.e("filterListWithDateRange","Exception while filtering with date range!"+ex.getLocalizedMessage());
        }

        return inTransitTransactionData;
    }

    public void filter(String query) {
        if(mAdapter != null)
            mAdapter.filter(query);
    }

    public void filterWithDateRange(String fromDate, String toDate) {
        if(!TextUtils.isEmpty(fromDate) && !TextUtils.isEmpty(toDate)) {
            List<InTransitTransactionData> dataList = filterListWithDateRange(mDataList,
                    fromDate, toDate);

            // refresh the adapter with new filtered list
            mAdapter = new InTransitTransactionAdapter(getActivity(), dataList);
            if(recyclerView != null)
                recyclerView.setAdapter(mAdapter);
            if(mAdapter != null)
                mAdapter.notifyDataSetChanged();
        }
    }

    public void setSummaryVisibility(boolean visibility) {
        if(rlTripDetailsMainContent != null) {
            if (visibility) {
                rlTripDetailsMainContent.setVisibility(View.VISIBLE);
            } else {
                rlTripDetailsMainContent.setVisibility(View.GONE);
            }
        }
    }

    public void setData() {
        Log.i("","setData");
        String transactionData = ((TransactionActivity)getActivity()).getJsonArrayTransaction();
        try {
            if(!TextUtils.isEmpty(transactionData)) {
                JSONArray jsonArray = new JSONArray(transactionData);
                if (jsonArray != null && jsonArray.length() > 0) {
                    BookingDataParser bookingDataParser = new BookingDataParser(jsonArray);
                    mDataList = bookingDataParser.getCompleteBookingDataArrayList();
                    mAdapter = new InTransitTransactionAdapter(getActivity(), mDataList);
                    recyclerView.setAdapter(mAdapter);
                }
            }

            // Set summary data
            String summaryData = ((TransactionActivity)getActivity()).getJsonSummary();
            if(!TextUtils.isEmpty(summaryData)) {
                JSONObject summary = new JSONObject(summaryData);
                if (summary != null) {
                    JSONObject podPendingData = summary.getJSONObject("completed_booking");
                    if (podPendingData != null) {
                        textViewNumberOfBooking.setText(Utils.get(podPendingData, "number_of_booking"));
                        textViewTotalAmount.setText(Utils.get(podPendingData, "total_amount"));
                    }
                }
            }
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    private void setRecyclerScroll() {
        recyclerView.addOnScrollListener(new RecyclerView.OnScrollListener() {
            @Override
            public void onScrollStateChanged(RecyclerView recyclerView, int newState) {
                super.onScrollStateChanged(recyclerView, newState);

                if (!recyclerView.canScrollVertically(1)) {
                    ((TransactionActivity)getActivity()).loadMoreData();
                }
            }
        });
    }

    public void resetData() {
        try {
            mDataList = new ArrayList<>();
            mAdapter = new InTransitTransactionAdapter(getActivity(), mDataList);
            recyclerView.setAdapter(mAdapter);
        } catch (Exception ex) {

        }
    }
}
