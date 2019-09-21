package in.aaho.android.aahocustomers;


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

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.aahocustomers.common.ApiResponseListener;
import in.aaho.android.aahocustomers.requests.AppVersionRequest;
import in.aaho.android.aahocustomers.requests.LoginRequest;
import in.aaho.android.aahocustomers.requests.LoginStatusRequest;
import in.aaho.android.aahocustomers.BuildConfig;


public class MainActivity extends AppDataActivity {

    private static final String TAG = "MainActivity";
    private ProgressBar progressBar = null;
    private TextView errorText;
    private Button tryAgainBtn;
    private Context context;

    private static final String STATE_KEY = "state";

    private static final String STATE_LOGGED_IN = "logged_in";
    private static final String STATE_LOGGED_OUT = "logged_out";
    private static final String STATE_INACTIVE = "inactive";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        context = MainActivity.this;
        setContentView(R.layout.activity_loading);
        checkAppVersion();
        //checkLoginStatusDelay(1);
    }

    private void setClickListeners() {
        tryAgainBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                progressBar.setVisibility(View.VISIBLE);
                errorText.setVisibility(View.INVISIBLE);
                tryAgainBtn.setVisibility(View.INVISIBLE);
                checkLoginStatus();
            }
        });
    }

    private void setViewVariables() {
        progressBar = (ProgressBar) findViewById(R.id.loading_progress_bar);
        errorText = (TextView) findViewById(R.id.error_text_view);
        tryAgainBtn = (Button) findViewById(R.id.try_again_button);
    }

    private void setupUI() {
        if (progressBar == null) {
            setViewVariables();
            setClickListeners();
        }
    }

    private void checkLoginStatusDelay(int time) {
        final Handler handler = new Handler();
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                checkLoginStatus();
            }
        }, time);
    }

    private void checkAppVersion(){
        String versionName = BuildConfig.VERSION_NAME;
        Log.d(TAG,"Current Version:"+versionName);
        AppVersionRequest appVersionRequest = new AppVersionRequest("android", "AC",
                versionName, new AppVersionListener());
        queue(appVersionRequest, false);
    }

    private class AppVersionListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            setupUI();
            String resp = response.toString();
            try {
                JSONObject jsonObject = new JSONObject(resp);
                if(response.get("status").equals("success")){
                    JSONObject dataObject = jsonObject.getJSONObject("data");
                    if(dataObject != null && dataObject.get("forceUpgrade").toString().equals("true")){
                        Log.d(TAG,"App version need to be upgraded forcefully");
                        showForceUpdateDialog(dataObject.get("latest_version").toString());
                    }else if(dataObject != null && dataObject.get("recommendUpgrade").toString().equals("true")){
                        Log.d(TAG,"App version is recommended to upgrade");
                        showRecommendUpdateDialog(dataObject.get("latest_version").toString());
                    }else{
                        Log.d(TAG,"App version is upto date");
                        checkLoginStatusDelay(1);
                    }
                }else{
                    Log.d(TAG,response.get("msg").toString());
                    checkLoginStatusDelay(1);
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

    private void checkLoginStatus() {
        LoginStatusRequest loginStatusrequest = new LoginStatusRequest(new LoginStatusListener());
        queue(loginStatusrequest, false);
        //tryAutoLogin();
    }

    private class LoginStatusListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            setupUI();
            try {
                String loginState = response.getString(STATE_KEY);
                if (loginState.equals(STATE_INACTIVE)) {
                    displayInactiveMessage();
                } else if (loginState.equals(STATE_LOGGED_IN)) {
                    fetchData(false);
                } else if (loginState.equals(STATE_LOGGED_OUT)) {
                    tryAutoLogin();
                } else {
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

    private class LoginListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            Log.e("[LoginListener]", response.toString());
            fetchData(false);
        }

        @Override
        public void onError() {
            dismissProgress();
            startLoginActivity();
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

    private void makeLoginRequest(String username, String password) {
        LoginRequest loginRequest = new LoginRequest(username, password, new LoginListener());
        queue(loginRequest);
    }


    @Override
    protected void onDestroy() {
        super.onDestroy();

    }

    @Override
    protected void onPause() {
        super.onPause();
    }

    private void startLoginActivity() {
        Log.e("[####]", "startLoginActivity");
        startActivity(new Intent(this, LoginActivity.class));
        finish();
    }
    public void showForceUpdateDialog(String latest_version){

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

    public void showRecommendUpdateDialog(String latest_version){

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
                checkLoginStatusDelay(1);
                dialog.cancel();
            }
        });
        alertDialogBuilder.show();
    }
}