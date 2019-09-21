package in.aaho.android.ownr.transaction;

import android.app.Activity;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.support.design.widget.TabLayout;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.FragmentPagerAdapter;
import android.support.v4.app.FragmentStatePagerAdapter;
import android.support.v4.view.ViewPager;
import android.support.v7.app.ActionBar;
import android.support.v7.app.AlertDialog;
import android.support.v7.widget.AppCompatEditText;
import android.support.v7.widget.RecyclerView;
import android.text.Editable;
import android.text.TextUtils;
import android.text.TextWatcher;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.LinearLayout;
import android.widget.RelativeLayout;
import android.widget.TextView;

import com.android.volley.VolleyError;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.UnsupportedEncodingException;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.UploadActivity;
import in.aaho.android.ownr.common.ApiResponseListener;
import in.aaho.android.ownr.common.BaseActivity;
import in.aaho.android.ownr.common.DatePickerDialogFragment;
import in.aaho.android.ownr.common.Utils;
import in.aaho.android.ownr.data.ConfirmedTransactionData;
import in.aaho.android.ownr.requests.TransactionDataRequests;


public class TransactionActivity extends BaseActivity implements View.OnClickListener,
        PODPendingFragment.IOnUploadPodClickedListener {

    private TabLayout tabLayout;
    public final static String TAG = "AAHO_LOG";
    private Map<String, String> params;
    public JSONArray jsonArrayPending;
    public JSONArray jsonArrayConfirm;
    public JSONArray jsonArrayInTransit;
    public JSONArray jsonArrayDelivered;
    public JSONArray jsonArrayCancelled;
    //    private PendingFragment pendingFragment = new PendingFragment();
    private PODPendingFragment podPendingFragment = new PODPendingFragment();
    private ConfirmedFragment podDeliveredFragment = new ConfirmedFragment();
    private InTransitFragment inTransitFragment = new InTransitFragment();
//    private DeliveredFragment deliveredFragment = new DeliveredFragment();
//    private CancelledFragment cancelledFragment = new CancelledFragment();

    private TextView tvFilterLabel;
    private Button btnClearFilterButton;
    AppCompatEditText filterEditText;
    ImageButton filterImageButton;
    ViewPager viewPager;
    ViewPagerAdapter adapter;

    String jsonArrayTransaction = "";
    String jsonSummary = "";
    private boolean isFilterEnabled = false;
    private LinearLayout linearFilterSection;

    private boolean isDataLoading;
    private String url = null;

    private final int MI_REQUEST_CODE_FOR_POD_UPLOAD = 101;

    public String getJsonArrayTransaction() {
        return jsonArrayTransaction;
    }

    public void setJsonArrayTransaction(String jsonArrayTransaction) {
        this.jsonArrayTransaction = jsonArrayTransaction;
    }

    public String getJsonSummary() {
        return jsonSummary;
    }

    public void setJsonSummary(String jsonSummary) {
        this.jsonSummary = jsonSummary;
    }


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
//        setContentView(R.layout.activity_transaction);
        setContentView(R.layout.activity_transaction_new);
        ActionBar toolbar = getSupportActionBar();
        setToolbarTitle("Transactions");
        findViews();
        loadDataFromServer(false, "");
//        getTransactionData();

        filterEditText.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {

            }

            @Override
            public void onTextChanged(CharSequence filterQuery, int start, int before, int count) {
                //mTaskManagerAdapter.getFilter().filter(s);

                if (TextUtils.isEmpty(filterQuery)) {
                    linearFilterSection.setVisibility(View.GONE);
                    setSummaryVisibility(true);
                } else {
                    linearFilterSection.setVisibility(View.VISIBLE);
                    setSummaryVisibility(false);
                    tvFilterLabel.setText("Results for " + "'" + filterQuery.toString() + "'");
                }

                loadDataFromServer(true, filterQuery.toString());
                /*doFilter(filterQuery.toString());*/

                /*Utils.searchText = filterQuery.toString();
                podPendingFragment.filter(filterQuery.toString());
                podDeliveredFragment.filter(filterQuery.toString());
                inTransitFragment.filter(filterQuery.toString());*/


                /*if(currentPageIndex == 0) {
                    if(!TextUtils.isEmpty(filterQuery)) {
                        podPendingFragment.filter(filterQuery.toString());
                    }
                } else if(currentPageIndex == 1) {
                    podDeliveredFragment.filter(filterQuery.toString());
                } else if(currentPageIndex == 2) {
                    //inTransitFragment.fiter(filterQuery.toString());
                } else {
                    // do nothing
                }*/
            }

            @Override
            public void afterTextChanged(Editable s) {

            }
        });

        btnClearFilterButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                loadDataFromServer(false, "");
                resetFilter();
            }
        });

    }

    private void doFilter(String filterQuery) {
        Utils.searchText = filterQuery.toString();
        podPendingFragment.filter(filterQuery.toString());
        podDeliveredFragment.filter(filterQuery.toString());
        inTransitFragment.filter(filterQuery.toString());
    }

    private void doFilterWithRange(String fromDate, String toDate) {
        podPendingFragment.filterWithDateRange(fromDate, toDate);
        podDeliveredFragment.filterWithDateRange(fromDate, toDate);
        inTransitFragment.filterWithDateRange(fromDate, toDate);
    }

    private void resetFilter() {
        filterEditText.setText("");
        linearFilterSection.setVisibility(View.GONE);
        // doFilter("");
        // doFilterWithRange("","");
    }

    private void loadDataFromServer(boolean isSearch, String filterQuery) {
        try {
            Bundle bundle = getIntent().getExtras();
            Map<String, String> params = new HashMap<String, String>();
            if (isSearch) {
                resetTransactionData();
                filterQuery = filterQuery.replace(" ", "+");
                params.put("search", filterQuery);
            }
            if (bundle != null && bundle.containsKey("VehicleId")) {
                String vehicleId = bundle.getString("VehicleId", "");
                params.put("vehicle_id", vehicleId);
            }

            TransactionDataRequests appDataRequest = new TransactionDataRequests("", params,
                    new TransactionDetailsResponseListener());
            queue(appDataRequest, true);
        } catch (Exception ex) {
            Log.e(TAG, "Exception = " + ex.getLocalizedMessage());
        }
    }

    private void loadDataFromServer(String fromDate, String toDate) {
        try {
            Map<String, String> params = new HashMap<>();
            params.put("shipment_date_between_0", fromDate);
            params.put("shipment_date_between_1", toDate);
            url = "";
            resetTransactionData();
            TransactionDataRequests appDataRequest = new TransactionDataRequests(url, params,
                    new TransactionDetailsResponseListener());
            queue(appDataRequest, true);
        } catch (Exception ex) {
            Log.e(TAG, "Exception = " + ex.getLocalizedMessage());
        }
    }

    private class TransactionDetailsResponseListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            isDataLoading = false;
            dismissProgress();
            String resp = response.toString();
            try {
                /*JSONObject results = response.getJSONObject("results");*/
                JSONArray data = response.getJSONArray("data");
                JSONObject summary = response.getJSONObject("summary");
                setJsonSummary(String.valueOf(summary));
                String nextPageUrl = response.getString("next");
                if (TextUtils.isEmpty(nextPageUrl)) {
                    url = "";
                } else {
                    url = nextPageUrl;
                }
                /*JSONArray jsonArray = response.getJSONArray("results");*/
                Log.e(TAG, String.valueOf(data));
                if (data.length() > 0) {
                    Bundle bundle = new Bundle();
                    //bundle.putString("transactionData", String.valueOf(jsonArray));
                    /** NOTE: Need to change because android N give TransactionTooLargeException
                     we don't send list in bundle now **/
                    setJsonArrayTransaction(String.valueOf(data));

//                    pendingFragment.setArguments(bundle);
//                    deliveredFragment.setArguments(bundle);
//                    cancelledFragment.setArguments(bundle);
                    podPendingFragment.setArguments(bundle);
                    podDeliveredFragment.setArguments(bundle);
                    inTransitFragment.setArguments(bundle);

                    /*setupViewPager(viewPager);
                    tabLayout = findViewById(R.id.tabs);
                    tabLayout.setTabMode(TabLayout.MODE_FIXED);
                    tabLayout.setTabGravity(TabLayout.GRAVITY_FILL);
                    addViewPagerListener();
                    tabLayout.setupWithViewPager(viewPager);*/

                    podPendingFragment.setData();
                    podDeliveredFragment.setData();
                    inTransitFragment.setData();


                } else if (getIntent().getExtras() != null) {

                    AlertDialog.Builder alertDialogBuilder = new AlertDialog.Builder(TransactionActivity.this);
                    alertDialogBuilder.setMessage("There is no trip");
                    alertDialogBuilder.setPositiveButton("Ok",
                            new DialogInterface.OnClickListener() {
                                @Override
                                public void onClick(DialogInterface arg0, int arg1) {
                                    finish();
                                }
                            });
                    alertDialogBuilder.setOnDismissListener(new DialogInterface.OnDismissListener() {
                        @Override
                        public void onDismiss(DialogInterface dialogInterface) {
                            finish();
                        }
                    });
                    alertDialogBuilder.setOnCancelListener(new DialogInterface.OnCancelListener() {
                        @Override
                        public void onCancel(DialogInterface dialogInterface) {
                            finish();
                        }
                    });
                    AlertDialog alertDialog = alertDialogBuilder.create();
                    alertDialog.show();

                } else {
                    toast("No Data available!");
                    setJsonArrayTransaction("");
                    setJsonSummary("");
                    setupViewPager(viewPager);
                }
            } catch (JSONException e) {
                e.printStackTrace();
                toast("error reading response data:\n" + resp);
            } catch (Exception e) {
                e.printStackTrace();
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
                    setJsonArrayTransaction("");
                    setJsonSummary("");
                    setupViewPager(viewPager);
                    toast(errorMsg);
                    Log.i(TAG, errorMsg);
                }
            } catch (UnsupportedEncodingException e) {
                e.printStackTrace();
            } catch (Exception ex) {
                Log.e(TAG, "Exception = " + ex.getLocalizedMessage());
            }
        }

    }

    private void setupViewPager(ViewPager viewPager) {
        adapter = new ViewPagerAdapter(getSupportFragmentManager());
//        adapter.addFrag(pendingFragment, "PENDING");
        adapter.addFrag(podPendingFragment, "POD PENDING");
        adapter.addFrag(podDeliveredFragment, "POD DELIVERED");
        adapter.addFrag(inTransitFragment, "COMPLETED");
//        adapter.addFrag(deliveredFragment, "DELIVERED");
//        adapter.addFrag(cancelledFragment, "CANCELLED");
        viewPager.setAdapter(adapter);
    }

    class ViewPagerAdapter extends FragmentStatePagerAdapter {
        private final List<Fragment> mFragmentList = new ArrayList<>();
        private final List<String> mFragmentTitleList = new ArrayList<>();

        public ViewPagerAdapter(FragmentManager manager) {
            super(manager);
        }

        @Override
        public Fragment getItem(int position) {
            return mFragmentList.get(position);
        }

        @Override
        public int getCount() {
            return mFragmentList.size();
        }

        public void addFrag(Fragment fragment, String title) {
            mFragmentList.add(fragment);
            mFragmentTitleList.add(title);
        }

        @Override
        public CharSequence getPageTitle(int position) {
            return mFragmentTitleList.get(position);
        }
    }

    /**
     * find/bind data to views
     */
    void findViews() {
        linearFilterSection = findViewById(R.id.linear_filter_section);
        tvFilterLabel = findViewById(R.id.tvFilterLabel);
        btnClearFilterButton = findViewById(R.id.btnClearFilterButton);
        filterEditText = findViewById(R.id.filterEditText);
        filterImageButton = findViewById(R.id.filterImageButton);
        filterImageButton.setOnClickListener(this);
        viewPager = findViewById(R.id.viewpager);

        setupViewPager(viewPager);
        tabLayout = findViewById(R.id.tabs);
        tabLayout.setTabMode(TabLayout.MODE_FIXED);
        tabLayout.setTabGravity(TabLayout.GRAVITY_FILL);
        addViewPagerListener();
        tabLayout.setupWithViewPager(viewPager);
    }

    int currentPageIndex = 0;

    private void addViewPagerListener() {
        tabLayout.addOnTabSelectedListener(new TabLayout.OnTabSelectedListener() {
            @Override
            public void onTabSelected(TabLayout.Tab tab) {
                currentPageIndex = tab.getPosition();
                String filterQuery = filterEditText.getText().toString();
                if (currentPageIndex == 0) {
                    if (!TextUtils.isEmpty(filterQuery)) {
                        podPendingFragment.filter(filterQuery);
                    }
                } else if (currentPageIndex == 1) {
                    podDeliveredFragment.filter(filterQuery);
                } else if (currentPageIndex == 2) {
                    //inTransitFragment.fiter(filterQuery);
                } else {
                    // do nothing
                }
            }

            @Override
            public void onTabUnselected(TabLayout.Tab tab) {

            }

            @Override
            public void onTabReselected(TabLayout.Tab tab) {

            }
        });
    }

    private void showFilterDialog() {
        FragmentManager fm = getSupportFragmentManager();
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
                Utils.fromDate = fromDate;
                Utils.toDate = toDate;
                try {
                    SimpleDateFormat sourceFormat = new SimpleDateFormat("dd-MMM-yyyy",
                            Locale.getDefault());
                    SimpleDateFormat targetFormat = new SimpleDateFormat("yyyy-MM-dd",
                            Locale.getDefault());

                    String filterFromDate = targetFormat.format(sourceFormat.parse(fromDate));
                    String filterToDate = targetFormat.format(sourceFormat.parse(toDate));
                    loadDataFromServer(filterFromDate, filterToDate);
                    tvFilterLabel.setText("Results for " + fromDate + " to " + toDate);
                    linearFilterSection.setVisibility(View.VISIBLE);
                    setSummaryVisibility(false);
                } catch (ParseException e) {
                    e.printStackTrace();
                }

                /*doFilterWithRange(fromDate,toDate);*/
                /*podPendingFragment.filterWithDateRange(fromDate,toDate);
                podDeliveredFragment.filterWithDateRange(fromDate,toDate);
                inTransitFragment.filterWithDateRange(fromDate,toDate);*/
            }
        });
        editNameDialogFragment.show(fm, "fragment_pick_date");
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
    protected void onDestroy() {
        super.onDestroy();
        Utils.searchText = "";
        Utils.fromDate = "";
        Utils.toDate = "";
    }

    @Override
    public void onUploadPodClicked(ConfirmedTransactionData confirmedTransactionData) {
        // code to view uploaded POD
        Intent intent = new Intent(this, UploadActivity.class);
        Bundle bundle = new Bundle();
        String lrNumber = confirmedTransactionData.getLrNumber();
        if (TextUtils.isEmpty(lrNumber)) {
            lrNumber = confirmedTransactionData.getBookingId();
        }
        bundle.putString("LR_LIST", lrNumber);
        bundle.putString("vehicle_no", confirmedTransactionData.getVehicleNumber());
        bundle.putString("booking_id", confirmedTransactionData.getBookingId());
        intent.putExtras(bundle);
        startActivityForResult(intent, MI_REQUEST_CODE_FOR_POD_UPLOAD);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == MI_REQUEST_CODE_FOR_POD_UPLOAD) {
            if (resultCode == Activity.RESULT_OK) {
                new Handler().postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        // means pod upload success
                        loadDataFromServer(false, "");
                    }
                }, 1000);
            } else {
                // means pod upload not success
            }
        }
    }

    public void setSummaryVisibility(boolean visibility) {
        podPendingFragment.setSummaryVisibility(visibility);
        podDeliveredFragment.setSummaryVisibility(visibility);
        inTransitFragment.setSummaryVisibility(visibility);
    }

    /**
     * Load more data for pagination purpose
     */
    public void loadMoreData() {
        if (tvFilterLabel.getText().toString().contains(" to ")) {
            // means we are filtering by date range
        } else {
            linearFilterSection.setVisibility(View.GONE);
            String filterQuery = filterEditText.getText().toString();
            isDataLoading = true;
            if (TextUtils.isEmpty(filterQuery)) {
                loadDataFromServer(false, "");
            } else {
                filterQuery = filterQuery.replace(" ", "+");
                loadDataFromServer(true, filterQuery);
            }
        }
    }

    private void resetTransactionData() {
        jsonSummary = "";
        jsonArrayTransaction = "";
        podPendingFragment.resetData();
        podDeliveredFragment.resetData();
        inTransitFragment.resetData();
    }

}
