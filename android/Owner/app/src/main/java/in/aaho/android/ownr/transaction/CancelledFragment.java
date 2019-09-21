package in.aaho.android.ownr.transaction;

import android.content.Context;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.view.GestureDetector;
import android.view.LayoutInflater;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.adapter.CancelledTransactionAdapter;
import in.aaho.android.ownr.data.CancelTransactionData;
import in.aaho.android.ownr.parser.BookingDataParser;
import in.aaho.android.ownr.parser.TransactionsDataParser;


public class CancelledFragment extends Fragment {
    private RecyclerView recyclerView;
    private LinearLayoutManager layoutManager;
    private ArrayList<CancelTransactionData> cancelTransactionData;
    private CancelledTransactionAdapter mAdapter;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        recyclerView = (RecyclerView) inflater.inflate(R.layout.fragment_cancelled, container, false);
        SetupRecycleView(recyclerView);
        return recyclerView;
    }

    void SetupRecycleView(RecyclerView recList) {
        recList.setHasFixedSize(true);
        layoutManager = new LinearLayoutManager(getActivity());
        layoutManager.setOrientation(LinearLayoutManager.VERTICAL);
        recList.setLayoutManager(layoutManager);
        String transactionData= getArguments().getString("transactionData");
        try {
            JSONArray jsonArray = new JSONArray(transactionData);
            BookingDataParser bookingDataParser = new BookingDataParser(jsonArray);
            mAdapter = new CancelledTransactionAdapter(bookingDataParser.getCancelTransactionDataArrayList());
            recList.setAdapter(mAdapter);
        } catch (JSONException e) {
            e.printStackTrace();
        }

    }

    public interface ClickListener {
        void onClick(View view, int position);

        void onLongClick(View view, int position);
    }

    public static class RecyclerTouchListener implements RecyclerView.OnItemTouchListener {

        private GestureDetector gestureDetector;
        private CancelledFragment.ClickListener clickListener;

        public RecyclerTouchListener(Context context, final RecyclerView recyclerView, final CancelledFragment.ClickListener clickListener) {
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
}
