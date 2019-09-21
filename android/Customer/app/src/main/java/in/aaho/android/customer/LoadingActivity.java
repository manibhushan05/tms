package in.aaho.android.customer;


import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.TextView;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.customer.common.ApiResponseListener;
import in.aaho.android.customer.requests.LoginRequest;
import in.aaho.android.customer.requests.LoginStatusRequest;


public class LoadingActivity extends AppDataActivity {

    private ProgressBar progressBar;
    private TextView errorText;
    private Button tryAgainBtn;

    private static final String STATE_KEY = "state";

    private static final String STATE_LOGGED_IN = "logged_in";
    private static final String STATE_LOGGED_OUT = "logged_out";
    private static final String STATE_INACTIVE = "inactive";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_loading);
        setViewVariables();
        setClickListeners();
        checkLoginStatusDelay(500);
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

    private void startLoginActivity() {
        Log.e("[####]", "startLoginActivity");
        startActivity(new Intent(LoadingActivity.this, LoginActivity.class));
        LoadingActivity.this.finish();
    }
}