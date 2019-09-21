package in.aaho.android.ownr.transaction;

import android.content.Context;
import android.content.DialogInterface;
import android.os.Bundle;
import android.os.Handler;
import android.support.design.widget.TabLayout;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.FragmentStatePagerAdapter;
import android.support.v4.view.ViewPager;
import android.support.v7.app.AlertDialog;
import android.support.v7.widget.AppCompatEditText;
import android.text.Editable;
import android.text.TextUtils;
import android.text.TextWatcher;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import com.android.volley.VolleyError;

import org.greenrobot.eventbus.EventBus;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.UnsupportedEncodingException;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.common.ApiResponseListener;
import in.aaho.android.ownr.common.BaseActivity;
import in.aaho.android.ownr.common.DatePickerDialogFragment;
import in.aaho.android.ownr.common.Utils;
import in.aaho.android.ownr.requests.TransactionDataRequests;


public class TransactionNewActivity extends BaseActivity implements View.OnClickListener {

    private TabLayout tabLayout;
    public final static String TAG = "TransactionNewActivity";

    private TextView tvFilterLabel;
    private Button btnClearFilterButton;
    private AppCompatEditText filterEditText;
    private ImageView imgSearchButton;
    private ImageButton filterImageButton;
    private ViewPager viewPager;

    private LinearLayout linearFilterSection;

    public String getVehicleId() {
        return vehicleId;
    }

    public void setVehicleId(String vehicleId) {
        this.vehicleId = vehicleId;
    }

    public String getSearchQuery() {
        return searchQuery;
    }

    public void setSearchQuery(String searchQuery) {
        this.searchQuery = searchQuery;
    }

    public String getFromDate() {
        return fromDate;
    }

    public void setFromDate(String fromDate) {
        this.fromDate = fromDate;
    }

    public String getToDate() {
        return toDate;
    }

    public void setToDate(String toDate) {
        this.toDate = toDate;
    }

    public boolean isSummaryVisible() {
        return summaryVisible;
    }

    public void setSummaryVisible(boolean visibility) {
        summaryVisible = visibility;
        try {
            PODPendingFragmentNew.setSummaryVisibility(visibility);
            PODDeliveredFragmentNew.setSummaryVisibility(visibility);
            CompletedBookingFragmentNew.setSummaryVisibility(visibility);
        } catch (Exception e) {
            Log.e(TAG, "Unable to set summary visibility! ex = " + e.getLocalizedMessage());
        }
    }

    /**
     * To store vehicle Id
     */
    private String vehicleId = "";
    /**
     * To store search Query
     */
    private String searchQuery = "";
    /**
     * To store filter dates
     */
    private String fromDate = "", toDate = "";
    /**
     * To set the summary visibility
     */
    private boolean summaryVisible = true;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_transaction_new);
        setToolbarTitle("Transactions");
        setBundleData();
        findViews();

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

        new Handler().postDelayed(new Runnable() {
            @Override
            public void run() {
                if (!TextUtils.isEmpty(getVehicleId()))
                    loadTripDataFromServer();
            }
        }, 100);

    }

    private void setBundleData() {
        Bundle bundle = getIntent().getExtras();
        if (bundle != null && bundle.containsKey("VehicleId")) {
            setVehicleId(bundle.getString("VehicleId", ""));
        }
    }

    private void postDataViaBus() {
        try {
            EventBus.getDefault().post(new MessageEvent());
        } catch (Exception e) {
            Log.e(TAG, "Unable to send data via Bus, Ex=" + e.getLocalizedMessage());
        }
    }

    @Override
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.imgSearchButton:
                // Set search query
                String searchQuery = filterEditText.getText().toString();
                setSearchQuery(searchQuery);
                setFilterResultVisibility(searchQuery);
                postDataViaBus();
                break;
            case R.id.filterImageButton:
                showFilterDialog();
                break;
            case R.id.btnClearFilterButton:
                resetFilter();
                postDataViaBus();
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
        setFromDate("");
        setToDate("");
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
            setSummaryVisible(true);
        } else {
            linearFilterSection.setVisibility(View.VISIBLE);
            setSummaryVisible(false);
            tvFilterLabel.setText("Results for " + "'" + filterQuery.toString() + "'");
        }
    }

    /**
     * Show date filter dialog
     */
    private void showFilterDialog() {
        FragmentManager fm = getSupportFragmentManager();
        DatePickerDialogFragment editNameDialogFragment = new DatePickerDialogFragment(new DatePickerDialogFragment.FilterDialogListener() {
            @Override
            public void onFinishFilterDialog(String fromDate, String toDate) {
                Utils.fromDate = fromDate;
                Utils.toDate = toDate;
                try {
                    SimpleDateFormat sourceFormat = new SimpleDateFormat("dd-MMM-yyyy",
                            Locale.getDefault());
                    SimpleDateFormat targetFormat = new SimpleDateFormat("yyyy-MM-dd",
                            Locale.getDefault());

                    String filterFromDate = targetFormat.format(sourceFormat.parse(fromDate));
                    String filterToDate = targetFormat.format(sourceFormat.parse(toDate));
                    setFromDate(filterFromDate);
                    setToDate(filterToDate);
                    postDataViaBus();
                    tvFilterLabel.setText("Results for " + fromDate + " to " + toDate);
                    linearFilterSection.setVisibility(View.VISIBLE);
                    setSummaryVisible(false);
                } catch (ParseException e) {
                    e.printStackTrace();
                }
            }
        });
        editNameDialogFragment.show(fm, "fragment_pick_date");
    }

    /**
     * find/bind data to views
     */
    private void findViews() {
        linearFilterSection = findViewById(R.id.linear_filter_section);
        tvFilterLabel = findViewById(R.id.tvFilterLabel);
        btnClearFilterButton = findViewById(R.id.btnClearFilterButton);
        btnClearFilterButton.setOnClickListener(this);
        filterEditText = findViewById(R.id.filterEditText);
        filterImageButton = findViewById(R.id.filterImageButton);
        filterImageButton.setOnClickListener(this);
        imgSearchButton = findViewById(R.id.imgSearchButton);
        imgSearchButton.setOnClickListener(this);
        viewPager = findViewById(R.id.viewpager);
        tabLayout = findViewById(R.id.tabs);

        tabLayout.setTabMode(TabLayout.MODE_FIXED);
        tabLayout.setTabGravity(TabLayout.GRAVITY_FILL);

        TransactionFragmentPagerAdapter adapter =
                new TransactionFragmentPagerAdapter(this, getSupportFragmentManager());
        // Set the adapter onto the view pager
        viewPager.setAdapter(adapter);
        // Give the TabLayout the ViewPager
        tabLayout.setupWithViewPager(viewPager);
    }

    public class TransactionFragmentPagerAdapter extends FragmentStatePagerAdapter {

        private Context mContext;

        public TransactionFragmentPagerAdapter(Context context, FragmentManager fm) {
            super(fm);
            mContext = context;
        }

        // This determines the fragment for each tab
        @Override
        public Fragment getItem(int position) {
            if (position == 0) {
                return new PODPendingFragmentNew();
            } else if (position == 1) {
                return new PODDeliveredFragmentNew();
            } else {
                return new CompletedBookingFragmentNew();
            }
        }

        @Override
        public int getItemPosition(Object object) {
            // Causes adapter to reload all Fragments when
            // notifyDataSetChanged is called
            return POSITION_NONE;
        }

        // This determines the number of tabs
        @Override
        public int getCount() {
            return 3;
        }

        // This determines the title for each tab
        @Override
        public CharSequence getPageTitle(int position) {
            // Generate title based on item position
            switch (position) {
                case 0:
                    return "POD PENDING";
                case 1:
                    return "POD DELIVERED";
                case 2:
                    return "COMPLETED";
                default:
                    return null;
            }
        }

    }

    /**
     * This api is only used to check if we are looking for particular
     * vehicle trip only
     */
    private void loadTripDataFromServer() {
        Map<String, String> params = new HashMap<String, String>();
        if (!TextUtils.isEmpty(getVehicleId())) {
            params.put("vehicle_id", getVehicleId());
        }

        TransactionDataRequests appDataRequest = new TransactionDataRequests("", params,
                new TransactionDetailsResponseListener());
        queue(appDataRequest, true);
    }

    private class TransactionDetailsResponseListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            try {
                if (response != null && response.getString("status")
                        .equalsIgnoreCase("success")) {
                    if (response.has("data")) {
                        JSONArray data = response.getJSONArray("data");
                        if (data == null || data.length() == 0) {
                            showNoTripDialog();
                        }
                    } else {
                        showNoTripDialog();
                    }
                } else {
                    Utils.toast("Error while getting Trip data!");
                }
            } catch (JSONException e) {
                e.printStackTrace();
                Utils.toast("error reading response data:\n" + e.getLocalizedMessage());
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
                    Utils.showInfoDialog(TransactionNewActivity.this, Utils.getRequestMessage(errorData),
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

    /**
     * Show No trip available dialog
     */
    private void showNoTripDialog() {
        AlertDialog.Builder alertDialogBuilder = new AlertDialog.Builder(TransactionNewActivity.this);
        alertDialogBuilder.setMessage(R.string.no_trip_detail);
        alertDialogBuilder.setPositiveButton("OK",
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

}
