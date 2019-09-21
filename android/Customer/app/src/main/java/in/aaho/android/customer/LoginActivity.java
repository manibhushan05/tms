package in.aaho.android.customer;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;

import org.json.JSONObject;

import in.aaho.android.customer.common.ApiResponseListener;
import in.aaho.android.customer.requests.LoginRequest;


public class LoginActivity extends AppDataActivity {
    Button mLoginButton;
    EditText mUsernameEditText;
    EditText mPasswordEditText;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        setViewRefs();
        setClickListeners();
    }

    private void setClickListeners() {
        mLoginButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                mLoginButton.setClickable(false);
                checkLogin();
            }
        });
    }

    private void checkLogin() {
        String username = mUsernameEditText.getText().toString();
        String password = mPasswordEditText.getText().toString();
        makeLoginRequest(username, password);
    }

    private void makeLoginRequest(String username, String password) {
        LoginRequest loginRequest = new LoginRequest(username, password, new LoginListener());
        queue(loginRequest);
    }

    private class LoginListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            mLoginButton.setClickable(true);
            fetchData(true);
        }

        @Override
        public void onError() {
            dismissProgress();
            mLoginButton.setClickable(true);
        }
    }


    private void setViewRefs() {
        mUsernameEditText = (EditText) findViewById(R.id.input_username);
        mPasswordEditText = (EditText) findViewById(R.id.input_password);
        mLoginButton = (Button) findViewById(R.id.btn_login);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
    }

    @Override
    protected void onPause() {
        super.onPause();
    }

    @Override
    protected void onStop() {
        super.onStop();
    }

    @Override
    protected void onStart() {
        super.onStart();
    }

    @Override
    protected void onRestart() {
        super.onRestart();
    }

    @Override
    protected void onResume() {
        super.onResume();
    }
}