package in.aaho.android.aahocustomers.transaction;

import android.app.Activity;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.Bundle;
import android.support.design.widget.TabLayout;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.FragmentPagerAdapter;
import android.support.v4.view.ViewPager;
import android.support.v7.app.ActionBar;
import android.support.v7.app.AlertDialog;
import android.support.v7.widget.AppCompatEditText;
import android.text.Editable;
import android.text.TextUtils;
import android.text.TextWatcher;
import android.util.Log;
import android.view.View;
import android.widget.ImageButton;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import in.aaho.android.aahocustomers.Aaho;
import in.aaho.android.aahocustomers.POD_DOCS;
import in.aaho.android.aahocustomers.R;
import in.aaho.android.aahocustomers.UploadActivity;
import in.aaho.android.aahocustomers.ViewPODActivity;
import in.aaho.android.aahocustomers.common.ApiResponseListener;
import in.aaho.android.aahocustomers.common.BaseActivity;
import in.aaho.android.aahocustomers.common.DatePickerDialogFragment;
import in.aaho.android.aahocustomers.common.Utils;
import in.aaho.android.aahocustomers.data.ConfirmedTransactionData;
import in.aaho.android.aahocustomers.requests.TransactionDataRequests;

/**
 * Created by aaho on 14/06/18.
 */

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
    private ConfirmedFragment podDeliveredFragment = new ConfirmedFragment();
    private PODPendingFragment podPendingFragment = new PODPendingFragment();
//    private InTransitFragment inTransitFragment = new InTransitFragment();
    //    private DeliveredFragment deliveredFragment = new DeliveredFragment();
//    private CancelledFragment cancelledFragment = new CancelledFragment();
    AppCompatEditText filterEditText;
    ImageButton filterImageButton;
    ViewPager viewPager;
    private final int MI_REQUEST_CODE_FOR_POD_UPLOAD = 101;

    public String getJsonArrayTransaction() {
        return jsonArrayTransaction;
    }

    public void setJsonArrayTransaction(String jsonArrayTransaction) {
        this.jsonArrayTransaction = jsonArrayTransaction;
    }

    String jsonArrayTransaction = "";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
//        setContentView(R.layout.activity_transaction);
        setContentView(R.layout.activity_transaction_new);
        ActionBar toolbar = getSupportActionBar();
        setToolbarTitle("Transactions");
        findViews();
        loadDataFromServer();
//        getTransactionData();

        filterEditText.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {

            }

            @Override
            public void onTextChanged(CharSequence filterQuery, int start, int before, int count) {
                //mTaskManagerAdapter.getFilter().filter(s);

                Utils.searchText = filterQuery.toString();
                podPendingFragment.filter(filterQuery.toString(), filterEditText);
                podDeliveredFragment.filter(filterQuery.toString(), filterEditText);
//                inTransitFragment.filter(filterQuery.toString());

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

    }

    private void loadDataFromServer() {
        /*JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put("username", Aaho.getUsername());
        } catch (JSONException e) {
            e.printStackTrace();
        }
        Log.e("HIS", String.valueOf(Aaho.getUsername()));*/
//        String vehicleId = getIntent().getExtras().getString("VehicleId","");
        TransactionDataRequests appDataRequest = new TransactionDataRequests(
                new TransactionDetailsResponseListener());
        queue(appDataRequest);
    }

    private class TransactionDetailsResponseListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            String resp = response.toString();
            try {
                JSONArray jsonArray = response.getJSONArray("data");
                Log.e(TAG, String.valueOf(jsonArray));
                if (jsonArray.length() > 0) {
                    Bundle bundle = new Bundle();
                    //bundle.putString("transactionData", String.valueOf(jsonArray));
                    /** NOTE: Need to change because android N give TransactionTooLargeException
                     we don't send list in bundle now **/
                    setJsonArrayTransaction(String.valueOf(jsonArray));

//                    pendingFragment.setArguments(bundle);
                    podDeliveredFragment.setArguments(bundle);
                    podPendingFragment.setArguments(bundle);
//                    inTransitFragment.setArguments(bundle);
//                    deliveredFragment.setArguments(bundle);
//                    cancelledFragment.setArguments(bundle);
                    viewPager = findViewById(R.id.viewpager);
                    setupViewPager(viewPager);
                    tabLayout = findViewById(R.id.tabs);
                    tabLayout.setTabMode(TabLayout.MODE_FIXED);
                    tabLayout.setTabGravity(TabLayout.GRAVITY_FILL);
                    addViewPagerListener();
                    tabLayout.setupWithViewPager(viewPager);
                } else {
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
                }
            } catch (JSONException e) {
                e.printStackTrace();
                toast("error reading response data:\n" + resp);
            }
        }

        @Override
        public void onError() {
            dismissProgress();
        }
    }

    private void setupViewPager(ViewPager viewPager) {
        ViewPagerAdapter adapter = new ViewPagerAdapter(getSupportFragmentManager());
//        adapter.addFrag(pendingFragment, "PENDING");
        adapter.addFrag(podPendingFragment, "POD PENDING");
        adapter.addFrag(podDeliveredFragment, "POD RECEIVED");
//        adapter.addFrag(inTransitFragment, "COMPLETED");
//        adapter.addFrag(deliveredFragment, "DELIVERED");
//        adapter.addFrag(cancelledFragment, "CANCELLED");
        viewPager.setAdapter(adapter);
    }

    class ViewPagerAdapter extends FragmentPagerAdapter {
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

    /*boolean isFirstTime = true;
    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.search_menu, menu);
        //super.onCreateOptionsMenu(menu);

        SearchManager manager = (SearchManager) getSystemService(Context.SEARCH_SERVICE);

        SearchView search = (SearchView) menu.findItem(R.id.action_search).getActionView();

        search.setSearchableInfo(manager.getSearchableInfo(getComponentName()));

        //search.setIconifiedByDefault(false);

        search.setOnQueryTextListener(new SearchView.OnQueryTextListener() {

            @Override
            public boolean onQueryTextSubmit(String query) {
                Utils.toast("onQueryTextSubmit from Transaction Activity");
                searchText = query;
                return false;
            }

            @Override
            public boolean onQueryTextChange(String query) {

                //loadHistory(query);
                //toast("onQueryTextChange");
                //searchText = query;
                return true;
            }
        });

        return false;
    }*/

    /** find/bind data to views */
    void findViews() {
        filterEditText = findViewById(R.id.filterEditText);
        filterImageButton = findViewById(R.id.filterImageButton);
        filterImageButton.setOnClickListener(this);
    }

    int currentPageIndex = 0;
    private void addViewPagerListener() {
        tabLayout.addOnTabSelectedListener(new TabLayout.OnTabSelectedListener() {
            @Override
            public void onTabSelected(TabLayout.Tab tab) {
                currentPageIndex = tab.getPosition();
                String filterQuery = filterEditText.getText().toString();
                if(currentPageIndex == 0) {
                    if(!TextUtils.isEmpty(filterQuery)) {
                        podPendingFragment.filter(filterQuery, filterEditText);
                    }
                } else if(currentPageIndex == 1) {
                    podDeliveredFragment.filter(filterQuery, filterEditText);
                } else if(currentPageIndex == 2) {
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
                filterEditText.setText(fromDate +" - "+toDate);
                podPendingFragment.filterWithDateRange(fromDate,toDate, filterEditText);
                podDeliveredFragment.filterWithDateRange(fromDate,toDate, filterEditText);
//                inTransitFragment.filterWithDateRange(fromDate,toDate);
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
        bundle.putString("LR_LIST",confirmedTransactionData.getLrNumber());
        bundle.putString("vehicle_no",confirmedTransactionData.getVehicleNumber());
        bundle.putString("booking_id",confirmedTransactionData.getBookingId());
        intent.putExtras(bundle);
        startActivityForResult(intent,MI_REQUEST_CODE_FOR_POD_UPLOAD);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if(requestCode == MI_REQUEST_CODE_FOR_POD_UPLOAD) {
            if(resultCode == Activity.RESULT_OK) {
                // means pod upload success
                loadDataFromServer();
            } else {
                // means pod upload not success
            }
        }
    }
}
