package in.aaho.android.aahocustomers;

import android.os.Bundle;
import android.support.design.widget.TabLayout;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentActivity;
import android.support.v4.view.ViewPager;
import android.support.v7.app.ActionBar;
import android.text.TextUtils;
import android.view.ViewGroup;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.TextView;

import in.aaho.android.aahocustomers.common.BaseActivity;
import in.aaho.android.aahocustomers.login_options.LoginOptionsPagerAdapter;
import in.aaho.android.aahocustomers.login_options.LoginPasswordFragment;
import in.aaho.android.aahocustomers.login_options.LoginPinFragment;

/**
 * Created by aaho on 09/05/18.
 */

public class LoginOptionsActivity extends BaseActivity{

    ViewPager mViewPager;
    private TabLayout tabLayout;

    private LoginPasswordFragment loginPasswordFragment = new LoginPasswordFragment();
    private LoginPinFragment loginPinFragment = new LoginPinFragment();

    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login_options);
        ActionBar toolbar = getSupportActionBar();
        setToolbarTitle("Login");
        // ViewPager and its adapters use support library
        // fragments, so use getSupportFragmentManager.
//        mLoginOptionsPagerAdapter =
//                new LoginOptionsPagerAdapter(
//                        getSupportFragmentManager());
        mViewPager = (ViewPager) findViewById(R.id.viewpager);
        setupViewPager(mViewPager);
        tabLayout = findViewById(R.id.tabs);
        tabLayout.setTabMode(TabLayout.MODE_FIXED);
        tabLayout.setTabGravity(TabLayout.GRAVITY_FILL);
        addViewPagerListener();
        tabLayout.setupWithViewPager(mViewPager);
    }


    private void setupViewPager(ViewPager viewPager) {
        LoginOptionsPagerAdapter adapter = new LoginOptionsPagerAdapter(getSupportFragmentManager());
        adapter.addFrag(loginPasswordFragment, "Password");
        adapter.addFrag(loginPinFragment, "PIN");
        viewPager.setAdapter(adapter);
    }
    private void addViewPagerListener() {
        tabLayout.addOnTabSelectedListener(new TabLayout.OnTabSelectedListener() {
            @Override
            public void onTabSelected(TabLayout.Tab tab) {
                mViewPager.setCurrentItem(tab.getPosition());
            }

            @Override
            public void onTabUnselected(TabLayout.Tab tab) {

            }

            @Override
            public void onTabReselected(TabLayout.Tab tab) {

            }
        });
    }



}


