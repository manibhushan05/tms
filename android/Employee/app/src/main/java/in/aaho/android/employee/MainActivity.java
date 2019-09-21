package in.aaho.android.employee;


import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.ContextThemeWrapper;
import android.view.View;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.TextView;

import com.android.volley.VolleyError;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.UnsupportedEncodingException;

import in.aaho.android.employee.common.ApiResponseListener;
import in.aaho.android.employee.common.Utils;
import in.aaho.android.employee.loads.MyLoadsActivity;
import in.aaho.android.employee.requests.AppVersionRequest;
import in.aaho.android.employee.requests.LoginRequest;
import in.aaho.android.employee.requests.LoginStatusRequest;
import in.aaho.android.employee.requests.PostFcmTokenRequest;


public class MainActivity extends AppDataActivity {
    private final String TAG = getClass().getSimpleName();
    private Context context;
    private TextView errorText;
    private Button tryAgainBtn;
    private ProgressBar progressBar = null;

    private static final String STATE_KEY = "state";

    private static final String STATE_LOGGED_IN = "logged_in";
    private static final String STATE_LOGGED_OUT = "logged_out";
    private static final String STATE_INACTIVE = "inactive";
    private static final int SPLASH_SCREEN_DELAY = 100;

    private IOnInitialDataListener mIOnInitialDataListener;

    public interface IOnInitialDataListener {
        void onInitialDataReceived(int statusCode);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        context = MainActivity.this;
        setContentView(R.layout.activity_loading);

        loadInitialDataFromServer(SPLASH_SCREEN_DELAY);

        mIOnInitialDataListener = new IOnInitialDataListener() {
            @Override
            public void onInitialDataReceived(int statusCode) {
                // On initial Data load finished
                if (statusCode == 200) {
                    checkAppVersion();
                    // register with fcm server
                    saveTokenIdOnServer(Aaho.getFcmToken(), Aaho.getDeviceId());
                } else {
                    startLoginActivity();
                }
            }
        };

    }

    private void setClickListeners() {
        tryAgainBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                progressBar.setVisibility(View.VISIBLE);
                errorText.setVisibility(View.INVISIBLE);
                tryAgainBtn.setVisibility(View.INVISIBLE);
                /* commented because we don't check with login status api */
                //checkLoginStatus();

                //fetchInitialData(false, mIOnInitialDataListener);
                fetchCategoryId(false,mIOnInitialDataListener);
            }
        });
    }

    private void setViewVariables() {
        progressBar = findViewById(R.id.loading_progress_bar);
        errorText = findViewById(R.id.error_text_view);
        tryAgainBtn = findViewById(R.id.try_again_button);
    }

    private void setupUI() {
        if (progressBar == null) {
            setViewVariables();
            setClickListeners();
        }
    }

    private void checkAppVersion() {
        String versionName = BuildConfig.VERSION_NAME;
        Log.d(TAG, "Current Version:" + versionName);
        AppVersionRequest appVersionRequest = new AppVersionRequest("android",
                "AE", versionName, new AppVersionListener());
        queue(appVersionRequest, false);
    }

    private class AppVersionListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            setupUI();
            String resp = response.toString();
            try {
                JSONObject jsonObject = new JSONObject(resp);
                if (response.get("status").equals("success")) {
                    JSONObject dataObject = jsonObject.getJSONObject("data");
                    if (dataObject != null && dataObject.get("forceUpgrade").toString().equals("true")) {
                        Log.d(TAG, "App version need to be upgraded forcefully");
                        showForceUpdateDialog(dataObject.get("latest_version").toString());
                    } else if (dataObject != null && dataObject.get("recommendUpgrade").toString().equals("true")) {
                        Log.d(TAG, "App version is recommended to upgrade");
                        showRecommendUpdateDialog(dataObject.get("latest_version").toString());
                    } else {
                        Log.d(TAG, "App version is upto date");
                        startLandingActivity();
                    }
                } else {
                    Log.d(TAG, response.get("msg").toString());
                    startLandingActivity();
                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }

        /*@Override
        public void onError() {
            setupUI();
            progressBar.setVisibility(View.INVISIBLE);
            errorText.setVisibility(View.VISIBLE);
            tryAgainBtn.setVisibility(View.VISIBLE);
        }*/

        @Override
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);
            dismissProgress();
            setupUI();
            progressBar.setVisibility(View.INVISIBLE);
            errorText.setVisibility(View.VISIBLE);
            tryAgainBtn.setVisibility(View.VISIBLE);
            try {
                if (error != null && error.networkResponse != null
                        && error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    JSONObject errorData = new JSONObject(errorMsg);
                    Utils.showInfoDialog(MainActivity.this,
                            Utils.getRequestMessage(errorData),Utils.getRequestData(errorData));
                    Log.i(TAG, errorMsg);
                }
            } catch (UnsupportedEncodingException ex) {
                Log.e(TAG,"UnsupportedEncodingException = "+ex.getLocalizedMessage());
            } catch (Exception ex) {
                Log.e(TAG,"Exception = "+ex.getLocalizedMessage());
            }
        }
    }

    private void loadInitialDataFromServer(int time) {
        final Handler handler = new Handler();
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                //fetchInitialData(false, mIOnInitialDataListener);
                fetchCategoryId(false, mIOnInitialDataListener);
            }
        }, time);
    }

    private void makeLoginRequest(String username, String password) {
        LoginRequest loginRequest = new LoginRequest(username, password, new LoginListener());
        queue(loginRequest);
    }

    private class LoginListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            Log.e(TAG, "LoginListener, Response = "+response.toString());
            startLandingActivity();
        }

        @Override
        public void onError() {
            dismissProgress();
            startLoginActivity();
        }
    }

    private void saveTokenIdOnServer(String token,String deviceId) {
        // save token to server
        makeSaveTokenRequest(token,deviceId);
    }

    private void makeSaveTokenRequest(String token,String deviceId) {
        PostFcmTokenRequest request = new PostFcmTokenRequest(token,deviceId,
                new SaveTokenListener());
        queue(request,false);
    }

    private class SaveTokenListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            Utils.dismissProgress(getApplicationContext());
            try {
                if(response.get("status").equals("success")){
                    //Utils.toast("Token Saved successfully!");
                }else{
                    //Utils.toast(response.get("msg").toString());
                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }

        @Override
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);
            Utils.dismissProgress(getApplicationContext());
            try {
                if (error != null && error.networkResponse != null
                        && error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    /*JSONObject errorData = new JSONObject(errorMsg);
                    Utils.showInfoDialog(MainActivity.this,
                            Utils.getRequestMessage(errorData),Utils.getRequestData(errorData));*/
                    Log.i(TAG, errorMsg);
                }
            } catch (UnsupportedEncodingException ex) {
                Log.e(TAG,"UnsupportedEncodingException = "+ex.getLocalizedMessage());
            } catch (Exception ex) {
                Log.e(TAG,"Exception = "+ex.getLocalizedMessage());
            }
        }
    }

    private void startLoginActivity() {
        Log.e(TAG, "startLoginActivity");
        startActivity(new Intent(this, LoginActivity.class));
        finish();
    }

    public void showForceUpdateDialog(String latest_version) {

        AlertDialog.Builder alertDialogBuilder = new AlertDialog.Builder(new ContextThemeWrapper(context,
                R.style.myBackgroundStyle));

        alertDialogBuilder.setTitle(context.getString(R.string.youAreNotUpdatedTitle));
        alertDialogBuilder.setMessage(context.getString(R.string.youAreNotUpdatedMessage) + " " + latest_version);
        alertDialogBuilder.setCancelable(false);
        alertDialogBuilder.setPositiveButton(R.string.update, new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int id) {
                context.startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("market://details?id=" + context.getPackageName())));
                dialog.cancel();
            }
        });
        alertDialogBuilder.show();
    }

    public void showRecommendUpdateDialog(String latest_version) {

        AlertDialog.Builder alertDialogBuilder = new AlertDialog.Builder(new ContextThemeWrapper(context,
                R.style.myBackgroundStyle));

        alertDialogBuilder.setTitle(context.getString(R.string.youAreNotUpdatedTitle));
        alertDialogBuilder.setMessage(context.getString(R.string.youAreNotUpdatedMessage) + " " + latest_version);
        alertDialogBuilder.setCancelable(false);
        alertDialogBuilder.setPositiveButton(R.string.update, new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int id) {
                context.startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("market://details?id=" + context.getPackageName())));
                dialog.cancel();
            }
        });
        alertDialogBuilder.setNegativeButton(R.string.skip, new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int id) {
                //context.startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("market://details?id=" + context.getPackageName())));
                /*checkLoginStatusDelay(100);*/
                startLandingActivity();
                dialog.cancel();
            }
        });
        alertDialogBuilder.show();
    }


    @SuppressWarnings("unused")
    private void checkLoginStatusDelay(int time) {
        final Handler handler = new Handler();
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                checkLoginStatus();
            }
        }, time);
    }

    private void checkLoginStatus() {
        LoginStatusRequest loginStatusrequest = new LoginStatusRequest(new LoginStatusListener());
        queue(loginStatusrequest, false);
    }

    private class LoginStatusListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            setupUI();
            try {
                String loginState = response.getString(STATE_KEY);
                switch (loginState) {
                    case STATE_INACTIVE:
                        displayInactiveMessage();
                        break;
                    case STATE_LOGGED_IN:
                        startLandingActivity();
                        break;
                    case STATE_LOGGED_OUT:
                        tryAutoLogin();
                        break;
                    default:
                        throw new AssertionError("Unknown login state - " + loginState);
                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }

        @Override
        public void onError() {
            setupUI();
            progressBar.setVisibility(View.INVISIBLE);
            errorText.setVisibility(View.VISIBLE);
            tryAgainBtn.setVisibility(View.VISIBLE);
        }
    }

    private void displayInactiveMessage() {
        toast("inactive user");
    }

    private void tryAutoLogin() {
        String username = Aaho.getUsername();
        String password = Aaho.getPassword();
        boolean loggedOut = !Aaho.getLoginStatus();

        if (loggedOut || username == null || password == null) {
            startLoginActivity();
        } else {
            makeLoginRequest(username, password);
        }
    }

}