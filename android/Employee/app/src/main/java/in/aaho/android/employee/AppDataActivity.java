package in.aaho.android.employee;

import android.content.Intent;
import android.text.TextUtils;
import android.util.Log;

import com.android.volley.VolleyError;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;


import java.util.HashMap;
import java.util.Map;

import in.aaho.android.employee.common.ApiResponseListener;
import in.aaho.android.employee.common.BaseActivity;
import in.aaho.android.employee.common.Utils;
import in.aaho.android.employee.requests.AppDataRequest;
import in.aaho.android.employee.requests.CategoryDataRequest;
import in.aaho.android.employee.requests.UserDataRequest;

/**
 * Created by aaho on 18/04/18.
 */

public class AppDataActivity extends BaseActivity {
    private final String TAG = getClass().getSimpleName();

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
            //try {
            //App.createAppData(resp);
            startLandingActivity();
//            } catch (JSONException e) {
//                e.printStackTrace();
//                toast("error fetching data");
//            }
        }

        @Override
        public void onError() {
            dismissProgress();
        }
    }

    /***************** Added by Suraj M *****************/

    protected void fetchCategoryId(boolean showProgessBar,
                                   MainActivity.IOnInitialDataListener iOnInitialDataListener) {
        String category = "employee";
        Map<String, String> params = new HashMap<String, String>();
        params.put("category", category);
        CategoryDataRequest appDataRequest = new CategoryDataRequest(params,
                new CategoryDataResponseListener(iOnInitialDataListener));
        queue(appDataRequest, showProgessBar);
    }

    private class CategoryDataResponseListener extends ApiResponseListener {
        MainActivity.IOnInitialDataListener miOnInitialDataListener;

        public CategoryDataResponseListener(MainActivity.IOnInitialDataListener iOnInitialDataListener) {
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
                            fetchInitialData(categoryId,false,miOnInitialDataListener);
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

    protected void fetchInitialData(String categoryId,boolean showProgessBar,
                                    MainActivity.IOnInitialDataListener iOnInitialDataListener) {
        /**NOTE: For Employee App categoryId is constant i.e 2 */
        //String categoryId = "2";
        Map<String, String> params = new HashMap<String, String>();
        params.put("category_id", categoryId);
        UserDataRequest appDataRequest = new UserDataRequest(params,
                new UserDataResponseListener(iOnInitialDataListener));
        queue(appDataRequest, showProgessBar);
    }

    private class UserDataResponseListener extends ApiResponseListener {
        MainActivity.IOnInitialDataListener miOnInitialDataListener;

        public UserDataResponseListener(MainActivity.IOnInitialDataListener iOnInitialDataListener) {
            this.miOnInitialDataListener = iOnInitialDataListener;
        }

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            if (response != null) {
                String resp = response.toString();
                Log.e("[USER DATA REQUEST]", resp);
                try {
                    JSONObject user = response.getJSONObject("user");
                    if (user != null) {
                        String employeeName = Utils.get(user, "full_name");
                        String employeeId = Utils.get(user, "employee_id");
                        if (TextUtils.isEmpty(employeeId)) {
                            // Finish the activity from here only, with showing dialog
                            // Show dialog
                            showDialog("Unable to retrieve employee data!");
                        } else {
                            Aaho.setUserFullname(employeeName);
                            Aaho.setEmployeeId(employeeId);
                            miOnInitialDataListener.onInitialDataReceived(200);
                        }
                    } else {
                        // Show dialog to close app
                        showDialog("Unable to retrieve employee data!");
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                    /*Utils.toast("error fetching data");*/
                    showDialog("Unable to retrieve employee data!");
                }
            } else {
                /*Utils.toast("error fetching data");*/
                showDialog("Unable to retrieve employee data!");
            }
        }

        @Override
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);
            try {
                if (error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    JSONObject errorData = new JSONObject(errorMsg);
                    String msg = Utils.getRequestMessage(errorData);
                    Aaho.setToken("");
                    showDialog(msg);
                    //miOnInitialDataListener.onInitialDataReceived(error.networkResponse.statusCode);
                    Log.i(TAG, "Error Message = " + errorMsg);
                }
            } catch (Exception ex) {
                miOnInitialDataListener.onInitialDataReceived(400);
                Log.e(TAG, "Exception = " + ex.getLocalizedMessage());
            }
        }
    }

    public void startLandingActivity() {
        Log.e(TAG, "startLandingActivity");
        startActivity(new Intent(this, LandingActivity.class));
        finish();
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

