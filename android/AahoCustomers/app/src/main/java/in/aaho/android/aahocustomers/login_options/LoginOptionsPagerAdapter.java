package in.aaho.android.aahocustomers.login_options;

import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.FragmentStatePagerAdapter;

import java.util.ArrayList;
import java.util.List;

/**
 * Created by aaho on 09/05/18.
 */
public class LoginOptionsPagerAdapter extends FragmentStatePagerAdapter {
//    public LoginOptionsPagerAdapter(FragmentManager fm) {
//        super(fm);
//    }
//
//    @Override
//    public Fragment getItem(int i) {
//        Fragment fragment = new LoginPasswordFragment();
//        Bundle args = new Bundle();
//        // Our object is just an integer :-P
//        args.putInt(LoginPasswordFragment.ARG_OBJECT, i + 1);
//        fragment.setArguments(args);
//        return fragment;
//    }
//
//    @Override
//    public int getCount() {
//        return 100;
//    }
//
//    @Override
//    public CharSequence getPageTitle(int position) {
//        return "OBJECT " + (position + 1);
//    }


    private final List<Fragment> mFragmentList = new ArrayList<>();
    private final List<String> mFragmentTitleList = new ArrayList<>();

    public LoginOptionsPagerAdapter(FragmentManager manager) {
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
