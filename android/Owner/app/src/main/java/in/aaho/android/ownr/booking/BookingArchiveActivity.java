package in.aaho.android.ownr.booking;

import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.FragmentPagerAdapter;
import android.support.v4.view.ViewPager;

import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.common.ApiResponseListener;
import in.aaho.android.ownr.common.BaseActivity;

public class BookingArchiveActivity extends BaseActivity {
    private PendingBookingFragment pendingBookingFragment = new PendingBookingFragment();
    private CompletedBookingFragment completedBookingFragment = new CompletedBookingFragment();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_booking_archive);
        setToolbarTitle("Booking Archive");
        loadFromServer();

    }

    private void loadFromServer() {
        BookingArchiveRequest bookingArchiveRequest = new BookingArchiveRequest(new BookingArchiveResponseListner());
        queue(bookingArchiveRequest);

    }

    private class BookingArchiveResponseListner extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            ViewPager viewPager = findViewById(R.id.viewpager);
            setupViewPager(viewPager);
        }

    }

    private void setupViewPager(ViewPager viewPager) {
        ViewPagerAdapter adapter = new ViewPagerAdapter(getSupportFragmentManager());
        adapter.addFrag(new PendingBookingFragment(), "PENDING");
        adapter.addFrag(new CompletedBookingFragment(), "COMPLETED");
        viewPager.setAdapter(adapter);
    }

    public class ViewPagerAdapter extends FragmentPagerAdapter {
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
