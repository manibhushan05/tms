package in.aaho.android.customer.transaction;

import android.app.ProgressDialog;
import android.os.Bundle;
import android.support.design.widget.TabLayout;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.FragmentPagerAdapter;
import android.support.v4.view.ViewPager;
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

import in.aaho.android.customer.common.BaseActivity;
import in.aaho.android.customer.R;
import in.aaho.android.customer.requests.Api;


public class TransactionActivity extends BaseActivity {

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

        getTransactionData();
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

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.POST, Api.TRANSACTION_DATA_URL, obj,
                new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        Log.e(TAG, String.valueOf(response));
                        Bundle bundle = new Bundle();
                        bundle.putString("transactionData", String.valueOf(response));
                        pendingFragment.setArguments(bundle);
                        confirmedFragment.setArguments(bundle);
                        inTransitFragment.setArguments(bundle);
                        deliveredFragment.setArguments(bundle);
                        cancelledFragment.setArguments(bundle);
                        viewPager = (ViewPager) findViewById(R.id.viewpager);
                        setupViewPager(viewPager);
                        tabLayout = (TabLayout) findViewById(R.id.tabs);
                        tabLayout.setupWithViewPager(viewPager);

                        pDialog.dismiss();
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
        ViewPagerAdapter adapter = new ViewPagerAdapter(getSupportFragmentManager());
        adapter.addFrag(pendingFragment, "PENDING");
        adapter.addFrag(confirmedFragment, "CONFIRMED");
        adapter.addFrag(inTransitFragment, "IN-TRANSIT");
        adapter.addFrag(deliveredFragment, "DELIVERED");
        adapter.addFrag(cancelledFragment, "CANCELLED");
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

}
