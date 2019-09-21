package in.aaho.android.ownr.vehicles;

import android.app.ProgressDialog;
import android.content.DialogInterface;
import android.support.design.widget.TabLayout;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.FragmentPagerAdapter;
import android.support.v4.view.ViewPager;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;

import com.android.volley.DefaultRetryPolicy;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.common.ApiResponseListener;
import in.aaho.android.ownr.common.BaseActivity;
import in.aaho.android.ownr.requests.Api;
import in.aaho.android.ownr.requests.TransactionDataRequests;
import in.aaho.android.ownr.requests.VehicleTripRequests;
import in.aaho.android.ownr.transaction.CancelledFragment;
import in.aaho.android.ownr.transaction.ConfirmedFragment;
import in.aaho.android.ownr.transaction.DeliveredFragment;
import in.aaho.android.ownr.transaction.InTransitFragment;
import in.aaho.android.ownr.transaction.PendingFragment;
import in.aaho.android.ownr.transaction.TransactionActivity;

public class VehicleTripActivity extends BaseActivity {
    private TabLayout tabLayout;
    private ViewPager viewPager;
    public final static String TAG = "AAHO_LOG";
    private Map<String, String> params;
    public JSONArray jsonArrayPending;
    public JSONArray jsonArrayConfirm;
    public JSONArray jsonArrayInTransit;
    public JSONArray jsonArrayDelivered;
    public JSONArray jsonArrayCancelled;
    private PendingFragment pendingFragment = new PendingFragment();
    private ConfirmedFragment confirmedFragment = new ConfirmedFragment();
    private InTransitFragment inTransitFragment = new InTransitFragment();
    private DeliveredFragment deliveredFragment = new DeliveredFragment();
    private CancelledFragment cancelledFragment = new CancelledFragment();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_transaction);
        setToolbarTitle("TRANSACTIONS");
        loadDataFromServer();
//        getTransactionData();

    }

    private void loadDataFromServer() {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put("vehicleId", VehicleDetailsActivity.vehicleId);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        Log.e(Api.TAG, String.valueOf(jsonObject));
        VehicleTripRequests appDataRequest = new VehicleTripRequests(jsonObject, new VehicleTripResponseListener());
        queue(appDataRequest);
    }

    private class VehicleTripResponseListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            String resp = response.toString();
            try {
                JSONArray jsonArray = response.getJSONArray("data");
                Log.e(TAG, String.valueOf(jsonArray));
                if (jsonArray.length() > 0) {
                    Bundle bundle = new Bundle();
                    bundle.putString("transactionData", String.valueOf(jsonArray));
                    pendingFragment.setArguments(bundle);
                    confirmedFragment.setArguments(bundle);
                    inTransitFragment.setArguments(bundle);
                    deliveredFragment.setArguments(bundle);
                    cancelledFragment.setArguments(bundle);
                    ViewPager viewPager = findViewById(R.id.viewpager);
                    setupViewPager(viewPager);
                    tabLayout = findViewById(R.id.tabs);
                    tabLayout.setTabMode(TabLayout.MODE_FIXED);
                    tabLayout.setTabGravity(TabLayout.GRAVITY_FILL);
                    tabLayout.setupWithViewPager(viewPager);
                } else {
                    AlertDialog.Builder alertDialogBuilder = new AlertDialog.Builder(VehicleTripActivity.this);
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

    private void getTransactionData() {
        final ProgressDialog pDialog = new ProgressDialog(this);
        pDialog.setMessage("Loading...");
        pDialog.show();
        JSONObject obj = new JSONObject();
        try {
            obj.put("username", "sme");
        } catch (JSONException e) {
            e.printStackTrace();
        }

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.POST, Api.VEHICLE_TRIP_DATA_URL, obj,
                new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        try {
                            JSONObject jsonObject = response.getJSONObject("data");

                            Log.e(TAG, String.valueOf(jsonObject));
                            Bundle bundle = new Bundle();
                            bundle.putString("transactionData", String.valueOf(jsonObject));
                            pendingFragment.setArguments(bundle);
                            confirmedFragment.setArguments(bundle);
                            inTransitFragment.setArguments(bundle);
                            deliveredFragment.setArguments(bundle);
                            cancelledFragment.setArguments(bundle);
                            viewPager = findViewById(R.id.viewpager);
                            setupViewPager(viewPager);
                            tabLayout = findViewById(R.id.tabs);
                            tabLayout.setupWithViewPager(viewPager);

                        } catch (JSONException e) {
                            e.printStackTrace();
                        }

                    }
                },
                new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        Log.e(TAG, error.toString());
                        pDialog.dismiss();
                    }
                });
        RequestQueue requestQueue = Volley.newRequestQueue(this);
        requestQueue.add(jsonObjectRequest);
        jsonObjectRequest.setRetryPolicy(new DefaultRetryPolicy(10000,
                DefaultRetryPolicy.DEFAULT_MAX_RETRIES,
                DefaultRetryPolicy.DEFAULT_BACKOFF_MULT));
    }

    private void setupViewPager(ViewPager viewPager) {
        VehicleTripActivity.ViewPagerAdapter adapter = new VehicleTripActivity.ViewPagerAdapter(getSupportFragmentManager());
//        adapter.addFrag(pendingFragment, "PENDING");
        adapter.addFrag(confirmedFragment, "PENDING");
        adapter.addFrag(inTransitFragment, "COMPLETED");
//        adapter.addFrag(deliveredFragment, "DELIVERED");
//        adapter.addFrag(cancelledFragment, "CANCELLED");
        viewPager.setAdapter(adapter);
    }

    private class ViewPagerAdapter extends FragmentPagerAdapter {
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

        void addFrag(Fragment fragment, String title) {
            mFragmentList.add(fragment);
            mFragmentTitleList.add(title);
        }

        @Override
        public CharSequence getPageTitle(int position) {
            return mFragmentTitleList.get(position);
        }
    }

}
