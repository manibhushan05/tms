package in.aaho.android.customer;

import android.content.Intent;
import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.customer.common.ApiResponseListener;
import in.aaho.android.customer.common.BaseActivity;
import in.aaho.android.customer.booking.App;
import in.aaho.android.customer.requests.AppDataRequest;

/**
 * Created by shobhit on 16/8/16.
 */
public class AppDataActivity extends BaseActivity {


    private void startLandingActivity() {
        Log.e("[LoginActivity]", "startLandingActivity");
        startActivity(new Intent(AppDataActivity.this, LandingActivity.class));
        AppDataActivity.this.finish();
    }

    protected void fetchData(boolean showProgessBar) {
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
                App.createAppData(resp);
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
