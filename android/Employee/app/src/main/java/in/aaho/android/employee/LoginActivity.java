package in.aaho.android.employee;

import android.content.Intent;
import android.os.Bundle;
import android.support.design.widget.TextInputEditText;
import android.support.design.widget.TextInputLayout;
import android.text.TextUtils;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import com.android.volley.VolleyError;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.UnsupportedEncodingException;

import in.aaho.android.employee.common.ApiResponseListener;
import in.aaho.android.employee.common.EditTextWatcher;
import in.aaho.android.employee.common.MainApplication;
import in.aaho.android.employee.common.Utils;
import in.aaho.android.employee.requests.LoginRequest;
import in.aaho.android.employee.requests.PostFcmTokenRequest;

/**
 * Created by aaho on 18/04/18.
 */

public class LoginActivity extends AppDataActivity implements View.OnClickListener {
    private static final String TAG = "LoginActivity";
    Button mLoginButton;
    TextView tvForgotPassword;
    TextInputEditText mUsernameEditText;
    TextInputEditText mPasswordEditText;
    TextInputLayout mUserNameTextInputLayout,mPasswordTextInputLayout;

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
                if(isValidInputByUser()) {
                    checkLogin();
                }
            }
        });

        mUsernameEditText.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                if(i == 0) {
                    mUserNameTextInputLayout.setError(null);
                }
            }
        });

        mPasswordEditText.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                if(i == 0) {
                    mPasswordTextInputLayout.setError(null);
                }
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
        Aaho.setUsername(username);
        queue(loginRequest);
    }

    private class LoginListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            try {
                if (response != null && response.getString("status")
                        .equalsIgnoreCase("success")) {

                    String token = response.getString("token");
                    if (!TextUtils.isEmpty(token)) {
                        Aaho.setToken(token);
                        mLoginButton.setClickable(true);
                        startActivity(new Intent(LoginActivity.this,MainActivity.class));
                        LoginActivity.this.finish();
                    } else {
                        mLoginButton.setClickable(true);
                        Utils.toast("Unable to login! Token is empty!");
                    }
                    MainApplication application = MainApplication.getInstance();
                    if (application != null) {
                        application.setPostLoginMainAppFields();
                    }
                }
            } catch (JSONException e) {
                mLoginButton.setClickable(true);
                e.printStackTrace();
                Utils.toast("Unable to login!");
            }
        }

        @Override
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);
            dismissProgress();
            mLoginButton.setClickable(true);
            try {
                if (error != null && error.networkResponse != null
                        && error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    JSONObject errorData = new JSONObject(errorMsg);
                    Utils.showInfoDialog(LoginActivity.this,
                            Utils.getRequestMessage(errorData),Utils.getRequestData(errorData));
                    Log.i(TAG, errorMsg);
                } else {
                    Utils.toast("Something went wrong, please try again later!");
                }
            } catch (UnsupportedEncodingException ex) {
                Log.e(TAG,"UnsupportedEncodingException = "+ex.getLocalizedMessage());
                Utils.toast("Something went wrong, please try again later!");
            } catch (Exception ex) {
                Log.e(TAG,"Exception = "+ex.getLocalizedMessage());
                Utils.toast("Something went wrong, please try again later!");
            }
        }
    }

    @Override
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.tvForgotPassword:
                // Reset editText fields
                mUsernameEditText.setText("");
                mPasswordEditText.setText("");
                startActivity(new Intent(LoginActivity.this,ForgotPasswordActivity.class));
                break;
        }
    }

    private void setViewRefs() {
        mUsernameEditText = findViewById(R.id.input_username);
        mPasswordEditText = findViewById(R.id.input_password);
        mLoginButton = findViewById(R.id.btn_login);
        mPasswordTextInputLayout = findViewById(R.id.passwordTextInputLayout);
        mUserNameTextInputLayout = findViewById(R.id.userNameTextInputLayout);
        tvForgotPassword = findViewById(R.id.tvForgotPassword);
        tvForgotPassword.setOnClickListener(this);
    }

    @Override
    protected void onDestroy() {
        dismissProgress();
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

    private boolean isValidInputByUser() {
        boolean result = true;
        String userName = mUsernameEditText.getText().toString();
        String password = mPasswordEditText.getText().toString();
        if(TextUtils.isEmpty(userName)) {
            mUserNameTextInputLayout.setError("User name can not be left blank!");
            mLoginButton.setClickable(true);
            result = false;
        }
        if(TextUtils.isEmpty(password)) {
            mPasswordTextInputLayout.setError("Password can not be left blank!");
            mLoginButton.setClickable(true);
            result = false;
        }

        return result;
    }
}