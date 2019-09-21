package in.aaho.android.ownr.transaction;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.common.ApiResponseListener;
import in.aaho.android.ownr.common.BaseActivity;
import in.aaho.android.ownr.requests.Api;

public class TeamBookingDetailsActivity extends BaseActivity {
    private RecyclerView recyclerViewTripDetails;
    private RecyclerView recyclerViewRateDetails;
    private LinearLayoutManager llmTripDetails;
    private LinearLayoutManager llmRateDetails;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_team_booking_details);
        setToolbarTitle("Booking Details");
        loadDataFromServer();
    }

    private void loadDataFromServer() {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put("booking_id", getIntent().getStringExtra("trans_id"));
        } catch (JSONException e) {
            e.printStackTrace();
        }
        TripDetailsRequest appDataRequest = new TripDetailsRequest(jsonObject, new TripDetailsResponseListener());
        queue(appDataRequest);
    }

    private class TripDetailsResponseListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            String resp = response.toString();
            try {
                JSONObject jsonObject = new JSONObject(resp);
//                updateUI(jsonObject);
                Log.e(Api.TAG, String.valueOf(jsonObject));
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

    private void updateUI(JSONObject jsonObject) {
        setUpTripRecycleView();
    }

    private void setUpTripRecycleView() {

    }

    private class TripDetailsVehicleInfoParser {
        private JSONObject jsonObject;
        private ArrayList<TripBasicData> tripBasicDataArrayList;

        public TripDetailsVehicleInfoParser(JSONObject jsonObject) {
            this.jsonObject = jsonObject;
        }

        public ArrayList<TripBasicData> getTripBasicDataArrayList() {
            tripBasicDataArrayList = new ArrayList<>();
            try {
                TripBasicData tripBasicData = new TripBasicData();
                tripBasicData.setDataLabel(jsonObject.getString("data_label"));
                tripBasicData.setDataValue(jsonObject.getString("data_value"));
                tripBasicDataArrayList.add(tripBasicData);

            } catch (JSONException e) {
                e.printStackTrace();
            }
            return tripBasicDataArrayList;
        }

        public void setTripBasicDataArrayList(ArrayList<TripBasicData> tripBasicDataArrayList) {
            this.tripBasicDataArrayList = tripBasicDataArrayList;
        }

    }
}
