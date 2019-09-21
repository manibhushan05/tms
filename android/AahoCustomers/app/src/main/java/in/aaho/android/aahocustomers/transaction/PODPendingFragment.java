package in.aaho.android.aahocustomers.transaction;

import android.app.ProgressDialog;
import android.content.Context;
import android.os.Bundle;
import android.os.SystemClock;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v7.widget.AppCompatEditText;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.text.Editable;
import android.text.TextUtils;
import android.text.TextWatcher;
import android.util.Log;
import android.view.GestureDetector;
import android.view.LayoutInflater;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.TextView;

import org.json.JSONArray;
import org.json.JSONException;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import in.aaho.android.aahocustomers.R;
import in.aaho.android.aahocustomers.adapter.ConfirmedTransactionAdapter;
import in.aaho.android.aahocustomers.common.DatePickerDialogFragment;
import in.aaho.android.aahocustomers.common.MainApplication;
import in.aaho.android.aahocustomers.common.Utils;
import in.aaho.android.aahocustomers.data.ConfirmedTransactionData;
import in.aaho.android.aahocustomers.parser.BookingDataParser;
import in.aaho.android.aahocustomers.requests.VehiclePathDataRequest;


public class PODPendingFragment extends Fragment implements View.OnClickListener,
        DatePickerDialogFragment.FilterDialogListener {

    ImageButton filterImageButton;
    AppCompatEditText filterEditText;
    AppCompatEditText parentFilterEditTextField;
    ConfirmedTransactionAdapter mAdapter;
    List<ConfirmedTransactionData> mDataList;
    RecyclerView recyclerView;
    IOnUploadPodClickedListener iOnUploadPodClickedListener;
    View rootView;
    Button clearFilter;
    Boolean filterApplied = false;
    String dateRangeText = null;

    public interface IOnUploadPodClickedListener {
        void onUploadPodClicked(ConfirmedTransactionData confirmedTransactionData);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View root_view = inflater.inflate(R.layout.fragment_confirmed, container, false);
        //setHasOptionsMenu(true);
        rootView = root_view;
        findViews(root_view);
        SetupRecycleView(root_view);
        filter(Utils.searchText, null);
        filterWithDateRange(Utils.fromDate,Utils.toDate, null);
        return root_view;
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        filterEditText.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {

            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                //mTaskManagerAdapter.getFilter().filter(s);
                if(dateRangeText == null || !dateRangeText.equals(s.toString())) {
                    if (mAdapter != null) {
                        mAdapter.filter(s.toString());
                        if (mAdapter.filteredList.size() < mDataList.size()) {
                            filterApplied = true;
                        }
                        if (filterApplied) {
                            TextView textViewNumberOfBooking = rootView.findViewById(R.id.tvNumberOfBookingsValue);
                            String filteredBookingsNo = String.valueOf(mAdapter.filteredList.size()) + " of " + String.valueOf(mDataList.size());
                            textViewNumberOfBooking.setText(filteredBookingsNo);
                            clearFilter.setVisibility(View.VISIBLE);

                        }
                    }
                }
            }

            @Override
            public void afterTextChanged(Editable s) {

            }
        });
        clearFilter = view.findViewById(R.id.tvClearFilters);
        clearFilter.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if(parentFilterEditTextField != null){
                    parentFilterEditTextField.getText().clear();
                }
                filterApplied = false;
                dateRangeText= null;
            }
        });

    }

    @Override
    public void onAttach(Context context) {
        super.onAttach(context);
        if(context instanceof IOnUploadPodClickedListener) {
            iOnUploadPodClickedListener = (IOnUploadPodClickedListener) context;
        }
    }

    @Override
    public void onDetach() {
        super.onDetach();
        if(iOnUploadPodClickedListener != null) {
            iOnUploadPodClickedListener = null;
        }
    }

    /** find/bind data to views */
    void findViews(View view) {
        filterImageButton = view.findViewById(R.id.filterImageButton);
        filterImageButton.setOnClickListener(this);
        filterEditText = view.findViewById(R.id.filterEditText);
    }

    void SetupRecycleView(View view) {

        recyclerView = view.findViewById(R.id.recycler_view_confirmed_transaction);
        recyclerView.setHasFixedSize(true);
        LinearLayoutManager layoutManager = new LinearLayoutManager(getActivity());
        layoutManager.setOrientation(LinearLayoutManager.VERTICAL);
        recyclerView.setLayoutManager(layoutManager);

//        String transactionData = getArguments().getString("transactionData");
        String transactionData = ((TransactionActivity)getActivity()).getJsonArrayTransaction();
        try {
            JSONArray jsonArray = new JSONArray(transactionData);
            BookingDataParser bookingDataParser = new BookingDataParser(jsonArray);
            mDataList = bookingDataParser.getPODPendingDataArrayList();
            mAdapter = new ConfirmedTransactionAdapter(getActivity(),mDataList, iOnUploadPodClickedListener);
            recyclerView.setAdapter(mAdapter);
            TextView textViewNumberOfBooking = view.findViewById(R.id.tvNumberOfBookingsValue);
            TextView textViewTotalAmount = view.findViewById(R.id.tvTotalAmountValue);
            TextView textViewPaidAmount = view.findViewById(R.id.tvPaidValue);
            TextView textViewBalanceAmount = view.findViewById(R.id.tvBalanceValue);
//            textViewNumberOfBooking.setText(String.valueOf(bookingDataParser.getNumberOfBooking()));
            textViewNumberOfBooking.setText(String.valueOf(mDataList.size()));
            textViewTotalAmount.setText(String.valueOf(bookingDataParser.getTotalAmount()));
            textViewBalanceAmount.setText(String.valueOf(bookingDataParser.getBalanceAmount()));
            textViewPaidAmount.setText(String.valueOf(bookingDataParser.getPaidAmount()));
            // Disabling for Customer User
            textViewTotalAmount.setVisibility(View.GONE);
            textViewBalanceAmount.setVisibility(View.GONE);
            textViewPaidAmount.setVisibility(View.GONE);
            TextView textViewTotalAmountLabel = view.findViewById(R.id.tvTotalAmountLabel);
            TextView textViewPaidAmountLabel = view.findViewById(R.id.tvPaidAmountLabel);
            TextView textViewBalanceAmountLabel = view.findViewById(R.id.tvBalanceLabel);
            textViewTotalAmountLabel.setVisibility(View.GONE);
            textViewPaidAmountLabel.setVisibility(View.GONE);
            textViewBalanceAmountLabel.setVisibility(View.GONE);
            Button clear_filter = view.findViewById(R.id.tvClearFilters);
            clear_filter.setVisibility(View.GONE);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    @Override
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.filterImageButton:
                showFilterDialog();
                break;
            default:
                break;
        }
    }

    @Override
    public void onFinishFilterDialog(String fromDate, String toDate) {
        /*List<ConfirmedTransactionData> dataList = filterListWithDateRange(mDataList,
                "01-Dec-2017","01-Jan-2018");*/

        List<ConfirmedTransactionData> dataList = filterListWithDateRange(mDataList,
                fromDate,toDate);

        // refresh the adapter with new filtered list
        mAdapter = new ConfirmedTransactionAdapter(getActivity(),dataList, iOnUploadPodClickedListener);
        recyclerView.setAdapter(mAdapter);
        mAdapter.notifyDataSetChanged();
    }

    public interface ClickListener {
        void onClick(View view, int position);

        void onLongClick(View view, int position);
    }

    public static class RecyclerTouchListener implements RecyclerView.OnItemTouchListener {

        private GestureDetector gestureDetector;
        private PODPendingFragment.ClickListener clickListener;

        public RecyclerTouchListener(Context context, final RecyclerView recyclerView, final PODPendingFragment.ClickListener clickListener) {
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
    private List<ConfirmedTransactionData> filterListWithDateRange(List<ConfirmedTransactionData> listToFilter,
                                                                   String fromDate, String toDate) {
        List<ConfirmedTransactionData> confirmedTransactionDataArrayList = new ArrayList<>();
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
                        confirmedTransactionDataArrayList.add(listToFilter.get(iCount));
                    }
                }
            }

        } catch (Exception ex) {
            Log.e("filterListWithDateRange","Exception while filtering with date range!"+ex.getLocalizedMessage());
        }

        return confirmedTransactionDataArrayList;
    }

    private void showFilterDialog() {
        FragmentManager fm = getChildFragmentManager();
        //DatePickerDialogFragment editNameDialogFragment = DatePickerDialogFragment.newInstance("Some Title");
        DatePickerDialogFragment editNameDialogFragment = new DatePickerDialogFragment(new DatePickerDialogFragment.FilterDialogListener() {
            @Override
            public void onFinishFilterDialog(String fromDate, String toDate) {
                /*List<ConfirmedTransactionData> dataList = filterListWithDateRange(mDataList,
                        fromDate,toDate);

                // refresh the adapter with new filtered list
                mAdapter = new ConfirmedTransactionAdapter(getActivity(),dataList);
                recyclerView.setAdapter(mAdapter);
                mAdapter.notifyDataSetChanged();*/
            }
        });
        editNameDialogFragment.show(fm, "fragment_pick_date");
    }

    public void filter(String query, AppCompatEditText parentEditTextField) {
        if(dateRangeText == null || !dateRangeText.equals(query)){
            Boolean clearDate = false;
            if(dateRangeText != null && query.equals("")){
                clearDate = true;
            }
            dateRangeText = null;
            if(mAdapter != null) {
                mAdapter = mAdapter.filterQ(query);
                if ((mAdapter.filteredList.size() < mDataList.size()) && !clearDate) {
                    filterApplied = true;
                }else{
                    filterApplied = false;
                    SetupRecycleView(rootView);
                }
                if(filterApplied){
                    TextView textViewNumberOfBooking = rootView.findViewById(R.id.tvNumberOfBookingsValue);
                    String filteredBookingsNo = String.valueOf(mAdapter.filteredList.size()) + " of " + String.valueOf(mDataList.size());
                    textViewNumberOfBooking.setText(filteredBookingsNo);
                    clearFilter.setVisibility(View.VISIBLE);
                    if(parentEditTextField != null)
                        parentFilterEditTextField = parentEditTextField;
                }
            }
        }
    }

    public void filterWithDateRange(String fromDate, String toDate, AppCompatEditText parentEditTextField) {
        if(!TextUtils.isEmpty(fromDate) && !TextUtils.isEmpty(toDate)) {
            List<ConfirmedTransactionData> dataList = filterListWithDateRange(mDataList,
                    fromDate, toDate);

            // refresh the adapter with new filtered list
            mAdapter = new ConfirmedTransactionAdapter(getActivity(), dataList, iOnUploadPodClickedListener);
            if(recyclerView != null) {
                recyclerView.setAdapter(mAdapter);
                TextView textViewNumberOfBooking = rootView.findViewById(R.id.tvNumberOfBookingsValue);
                String filteredBookingsNo = String.valueOf(dataList.size()) + " of " + String.valueOf(mDataList.size());
                textViewNumberOfBooking.setText(filteredBookingsNo);
                clearFilter.setVisibility(View.VISIBLE);
                filterApplied = true;
                dateRangeText= fromDate +" - "+toDate;
                if(parentEditTextField != null)
                    parentFilterEditTextField = parentEditTextField;
            }
            if(mAdapter != null)
                mAdapter.notifyDataSetChanged();
        }
    }
}
