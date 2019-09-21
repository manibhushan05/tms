package in.aaho.android.customer.tracking;

import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.view.GestureDetector;
import android.view.MenuItem;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Toast;

import java.util.ArrayList;

import in.aaho.android.customer.LandingActivity;
import in.aaho.android.customer.R;
import in.aaho.android.customer.adapter.TrackingListAdapter;
import in.aaho.android.customer.data.TrackingDataList;

public class TrackingListActivity extends AppCompatActivity {

    private RecyclerView recyclerView;
    private LinearLayoutManager layoutManager;
    private ArrayList<TrackingDataList> trackingData;
    private TrackingListAdapter mAdapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_tracking_list);
//        getSupportActionBar().setTitle("Track");
//        getSupportActionBar().setDisplayHomeAsUpEnabled(true);


        recyclerView = (RecyclerView) findViewById(R.id.recycler_view_tracking_list);
        recyclerView.setHasFixedSize(true);
        layoutManager = new LinearLayoutManager(this);
        recyclerView.setLayoutManager(layoutManager);

        trackingData = new ArrayList<>();
        addTrackingData();
        mAdapter = new TrackingListAdapter(trackingData);
        recyclerView.setAdapter(mAdapter);
//        mAdapter.notifyDataSetChanged();
        recyclerView.addOnItemTouchListener(new RecyclerTouchListener(getApplicationContext(), recyclerView, new ClickListener() {
            @Override
            public void onClick(View view, int position) {
                TrackingDataList data = trackingData.get(position);
                Toast.makeText(getApplicationContext(), data.getTransactionId() + " is selected!", Toast.LENGTH_SHORT).show();
            }

            @Override
            public void onLongClick(View view, int position) {

            }
        }));
    }

    public void addTrackingData() {
        trackingData.add(new TrackingDataList("STR00001", "Loading", "Mumbai", "Ahmedabad", "23-Jul-2016", "Powai", "12 Jul at 10 PM"));
        trackingData.add(new TrackingDataList("STR00002", "In-Transit", "Mumbai", "Ahmedabad", "23-Jul-2016", "Powai", "12 Jul at 10 PM"));
        trackingData.add(new TrackingDataList("STR00003", "Loading", "Mumbai", "Ahmedabad", "23-Jul-2016", "Powai", "12 Jul at 10 PM"));
        trackingData.add(new TrackingDataList("STR00004", "Loading", "Mumbai", "Ahmedabad", "23-Jul-2016", "Powai", "12 Jul at 10 PM"));
        trackingData.add(new TrackingDataList("STR00005", "Loading", "Mumbai", "Ahmedabad", "23-Jul-2016", "Powai", "12 Jul at 10 PM"));
        trackingData.add(new TrackingDataList("STR00006", "Loading", "Mumbai", "Ahmedabad", "23-Jul-2016", "Powai", "12 Jul at 10 PM"));
        trackingData.add(new TrackingDataList("STR00001", "Loading", "Mumbai", "Ahmedabad", "23-Jul-2016", "Powai", "12 Jul at 10 PM"));
        trackingData.add(new TrackingDataList("STR00002", "In-Transit", "Mumbai", "Ahmedabad", "23-Jul-2016", "Powai", "12 Jul at 10 PM"));
        trackingData.add(new TrackingDataList("STR00003", "Loading", "Mumbai", "Ahmedabad", "23-Jul-2016", "Powai", "12 Jul at 10 PM"));
        trackingData.add(new TrackingDataList("STR00004", "Loading", "Mumbai", "Ahmedabad", "23-Jul-2016", "Powai", "12 Jul at 10 PM"));
    }

    public interface ClickListener {
        void onClick(View view, int position);

        void onLongClick(View view, int position);
    }

    public static class RecyclerTouchListener implements RecyclerView.OnItemTouchListener {

        private GestureDetector gestureDetector;
        private TrackingListActivity.ClickListener clickListener;

        public RecyclerTouchListener(Context context, final RecyclerView recyclerView, final TrackingListActivity.ClickListener clickListener) {
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
    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int itemId = item.getItemId();
        switch (itemId) {
            case android.R.id.home:
                startActivity(new Intent(TrackingListActivity.this,LandingActivity.class));
                break;

        }

        return super.onOptionsItemSelected(item);
    }
}
