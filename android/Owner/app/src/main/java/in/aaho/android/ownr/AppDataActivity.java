package in.aaho.android.ownr;

import android.content.Intent;
import android.text.TextUtils;
import android.util.Log;

import com.android.volley.VolleyError;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.HashMap;
import java.util.Map;

import in.aaho.android.ownr.common.ApiResponseListener;
import in.aaho.android.ownr.common.BaseActivity;
import in.aaho.android.ownr.booking.App;
import in.aaho.android.ownr.common.Utils;
import in.aaho.android.ownr.requests.AppDataRequest;
import in.aaho.android.ownr.requests.CategoryDataRequest;
import in.aaho.android.ownr.requests.UserDataRequest;

/**
 * Created by mani on 16/8/16.
 */
public class AppDataActivity extends BaseActivity {
    private final String TAG = getClass().getSimpleName();

    public void startLandingActivity() {
        Log.e("[LoginActivity]", "startLandingActivity");
        startActivity(new Intent(this, LandingActivity.class));
        finish();
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

    /***************** Added by Suraj M *****************/

    protected void fetchCategoryId(boolean showProgessBar,
                                   LoadingActivity.IOnInitialDataListener iOnInitialDataListener) {
        String category = "supplier";
        Map<String, String> params = new HashMap<String, String>();
        params.put("category", category);
        CategoryDataRequest appDataRequest = new CategoryDataRequest(params,
                new CategoryDataResponseListener(iOnInitialDataListener));
        queue(appDataRequest, showProgessBar);
    }

    private class CategoryDataResponseListener extends ApiResponseListener {
        LoadingActivity.IOnInitialDataListener miOnInitialDataListener;

        public CategoryDataResponseListener(LoadingActivity.IOnInitialDataListener iOnInitialDataListener) {
            super();
            miOnInitialDataListener = iOnInitialDataListener;
        }

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            if (response != null) {
                String resp = response.toString();

                Log.e("[USER DATA REQUEST]", resp);
                try {
                    JSONArray data = response.getJSONArray("data");
                    if (data != null && data.length() > 0) {
                        JSONObject category = data.getJSONObject(0);
                        String categoryId = Utils.get(category, "id");
                        String employeeName = Utils.get(category, "category");
                        if (TextUtils.isEmpty(categoryId)) {
                            // Finish the activity from here only, with showing dialog
                            // Show dialog
                            showDialog("Unable to retrieve category data!");
                        } else {
                            fetchUserData(categoryId,false,miOnInitialDataListener);
                        }
                    } else {
                        // Show dialog to close app
                        showDialog("Unable to retrieve category data!");
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                    /*Utils.toast("error fetching data");*/
                    showDialog("Unable to retrieve category data!");
                }
            } else {
                /*Utils.toast("error fetching data");*/
                showDialog("Unable to retrieve category data!");
            }
        }

        @Override
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);
            try {
                if (error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    miOnInitialDataListener.onInitialDataReceived(error.networkResponse.statusCode);
                    Log.i(TAG, "Error Message = " + errorMsg);
                }
            } catch (Exception ex) {
                miOnInitialDataListener.onInitialDataReceived(400);
                Log.e(TAG, "Exception = " + ex.getLocalizedMessage());
            }
        }
    }

    protected void fetchUserData(String categoryId,boolean showProgessBar,
                                 LoadingActivity.IOnInitialDataListener iOnInitialDataListener) {
        /**NOTE: For FMS App categoryId is constant i.e 1 */
        //String categoryId = "1";
        Map<String, String> params = new HashMap<String, String>();
        params.put("category_id", categoryId);
        UserDataRequest appDataRequest = new UserDataRequest(params,
                new UserDataResponseListener(iOnInitialDataListener));
        queue(appDataRequest, showProgessBar);
    }

    private class UserDataResponseListener extends ApiResponseListener {
        LoadingActivity.IOnInitialDataListener miOnInitialDataListener;

        public UserDataResponseListener(LoadingActivity.IOnInitialDataListener iOnInitialDataListener) {
            this.miOnInitialDataListener = iOnInitialDataListener;
        }

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            if (response != null) {
                String resp = response.toString();
                Log.e("[USER DATA REQUEST]", resp);
                try {
                    App.createUserData(resp);
                    //startLandingActivity();
                    miOnInitialDataListener.onInitialDataReceived(200);
                } catch (JSONException e) {
                    e.printStackTrace();
                    toast("error fetching data");
                }
            } else {
                toast("error fetching data");
            }
        }

        @Override
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);
            try {
                if (error.networkResponse.data != null) {
                    if (error.networkResponse.statusCode == 401) {
                        String errorMsg = new String(error.networkResponse.data, "UTF-8");
                        Log.i(TAG, "Error Message = " + errorMsg);
                    }
                    miOnInitialDataListener.onInitialDataReceived(error.networkResponse.statusCode);
                }
            } catch (Exception ex) {
                Log.e(TAG, "Exception = " + ex.getLocalizedMessage());
                miOnInitialDataListener.onInitialDataReceived(400);
            }
        }
    }

    private class CustomAlertDialogListener implements Utils.AlertDialogListener {

        @Override
        public void onPositiveButtonClicked() {
            startActivity(new Intent(AppDataActivity.this, LoginActivity.class));
            finish();
        }

        @Override
        public void onNegativeButtonClicked() {
            AppDataActivity.this.finish();
        }
    }

    private void showDialog(String msg) {
        Utils.showAlertDialog(AppDataActivity.this,
                getString(R.string.app_name),
                msg,"Go to Login","Exit",
                new CustomAlertDialogListener());
    }

}
