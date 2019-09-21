package in.aaho.android.aahocustomers;

import android.content.Intent;
import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;


import in.aaho.android.aahocustomers.common.ApiResponseListener;
import in.aaho.android.aahocustomers.common.BaseActivity;
import in.aaho.android.aahocustomers.common.Prefs;
import in.aaho.android.aahocustomers.requests.AppDataRequest;
//import in.aaho.android.requirement.booking.App;

/**
 * Created by aaho on 18/04/18.
 */


public class AppDataActivity extends BaseActivity {


    private void startLandingActivity() {
        Log.e("[LoginActivity]", "startLandingActivity");
        startActivity(new Intent(this, LandingActivity.class));
        finish();
    }

    public void fetchData(boolean showProgessBar) {
        AppDataRequest appDataRequest = new AppDataRequest(new AppDataResponseListener());
        queue(appDataRequest, showProgessBar);
    }

    private class AppDataResponseListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            String resp = response.toString();
            Log.e("[APP DATA REQUEST]", resp);
            try {
                JSONObject jsonObject = new JSONObject(resp);
                JSONObject dataObject = jsonObject.getJSONObject("data");
                Prefs.set("customer_id", dataObject.get("customer_id").toString());
                Prefs.set("aaho_office_id", dataObject.get("aaho_office_id").toString());
                Log.e("[APP DATA REQUEST]", Prefs.get("customer_id"));
                startLandingActivity();
            } catch (JSONException e) {
                e.printStackTrace();
                toast("error fetching data");
            }
        }

        @Override
        public void onError() {
            dismissProgress();
        }
    }

}

