package in.aaho.android.aahocustomers.transaction;

import android.content.DialogInterface;
import android.os.Bundle;
import android.support.design.widget.TabLayout;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.FragmentPagerAdapter;
import android.support.v4.view.ViewPager;
import android.support.v7.app.AlertDialog;
import android.text.TextUtils;
import android.util.Log;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

import in.aaho.android.aahocustomers.R;
import in.aaho.android.aahocustomers.common.ApiResponseListener;
import in.aaho.android.aahocustomers.common.BaseActivity;
import in.aaho.android.aahocustomers.requests.FinancialDataRequests;

/**
 * Created by aaho on 11/07/18.
 */

public class FinancialsActivity extends BaseActivity {
    public final static String TAG = "AAHO_LOG";
    private TabLayout tabLayout;
    ViewPager viewPager;

    private FinancialPaidFragment fPaidFragment = new FinancialPaidFragment();
    private FinancialToBePaidFragment fToBePaidFragment = new FinancialToBePaidFragment();

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
        setContentView(R.layout.activity_financials);
        setToolbarTitle("Financials");

        loadDataFromServer();
    }

    private void loadDataFromServer() {
        FinancialDataRequests appDataRequest = new FinancialDataRequests(
                new FinancialsActivity.FinancialDetailsResponseListener());
        queue(appDataRequest);
    }

    private class FinancialDetailsResponseListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            String resp = response.toString();
            try {
                JSONArray jsonArray = response.getJSONArray("data");
                Log.e(TAG, String.valueOf(jsonArray));
                if (jsonArray.length() > 0) {
                    Bundle bundle = new Bundle();

                    setJsonArrayTransaction(String.valueOf(jsonArray));
                    fPaidFragment.setArguments(bundle);
                    fToBePaidFragment.setArguments(bundle);

                    viewPager = findViewById(R.id.viewpager);
                    setupViewPager(viewPager);
                    tabLayout = findViewById(R.id.tabs);
                    tabLayout.setTabMode(TabLayout.MODE_FIXED);
                    tabLayout.setTabGravity(TabLayout.GRAVITY_FILL);
                    addViewPagerListener();
                    tabLayout.setupWithViewPager(viewPager);
                } else {
                    AlertDialog.Builder alertDialogBuilder = new AlertDialog.Builder(FinancialsActivity.this);
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
    int currentPageIndex = 0;
    private void addViewPagerListener() {
        tabLayout.addOnTabSelectedListener(new TabLayout.OnTabSelectedListener() {
            @Override
            public void onTabSelected(TabLayout.Tab tab) {
                currentPageIndex = tab.getPosition();
                if(currentPageIndex == 0) {
//                    fPaidFragment.filter(filterQuery, filterEditText);
                } else if(currentPageIndex == 1) {
//                    fToBePaidFragment.filter(filterQuery, filterEditText);
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

    private void setupViewPager(ViewPager viewPager) {
        FinancialsActivity.ViewPagerAdapter adapter = new FinancialsActivity.ViewPagerAdapter(getSupportFragmentManager());
        adapter.addFrag(fToBePaidFragment, "TO BE PAID");
        adapter.addFrag(fPaidFragment, "PAID");
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
