package in.aaho.android.ownr;

import android.content.Intent;
import android.os.Bundle;
import android.support.annotation.VisibleForTesting;
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

import in.aaho.android.ownr.common.ApiResponseListener;
import in.aaho.android.ownr.common.EditTextWatcher;
import in.aaho.android.ownr.common.MainApplication;
import in.aaho.android.ownr.common.Utils;
import in.aaho.android.ownr.requests.LoginRequest;
import in.aaho.android.ownr.requests.PostFcmTokenRequest;


public class LoginActivity extends AppDataActivity implements View.OnClickListener {
    private final String TAG = getClass().getSimpleName();
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
                if(isValidInputByUser(mUsernameEditText.getText().toString(),
                        mPasswordEditText.getText().toString())) {
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
            try {
                if (response != null && response.getString("status")
                        .equalsIgnoreCase("success")) {

                    String token = response.getString("token");
                    if (!TextUtils.isEmpty(token)) {
                        Aaho.setToken(token);
                        mLoginButton.setClickable(true);
                        /*fetchData(true);*/
                        // fetchUserData(true, mIOnInitialDataListener);
                        startActivity(new Intent(LoginActivity.this,LoadingActivity.class));
                        LoginActivity.this.finish();
                        // register with fcm server
                        saveTokenIdOnServer(Aaho.getFcmToken(), Aaho.getDeviceId());
                    } else {
                        Utils.toast("Unable to login! Token is empty!");
                    }
                    MainApplication application = MainApplication.getInstance();
                    if (application != null) {
                        application.setPostLoginMainAppFields();
                    }
                }
            } catch (JSONException e) {
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
                }
            } catch (UnsupportedEncodingException e) {
                e.printStackTrace();
            } catch (Exception ex) {
                Log.e(TAG,"Exception = "+ex.getLocalizedMessage());
            }
        }

        /*@Override
        public void onError() {
            dismissProgress();
            mLoginButton.setClickable(true);
        }*/
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


    /***** Added by Suraj *******/

    public boolean isValidInputByUser(String userName,String password) {
        boolean result = true;
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

    private void saveTokenIdOnServer(String token,String deviceId) {
        // save token to server
        makeSaveTokenRequest(token,deviceId);
    }

    private void makeSaveTokenRequest(String token,String deviceId) {
        PostFcmTokenRequest request = new PostFcmTokenRequest(token,deviceId,
                new SaveTokenListener());
        queue(request);
    }

    private class SaveTokenListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            Utils.dismissProgress(getApplicationContext());
            String resp = response.toString();
            try {
                if(response.get("status").toString().equalsIgnoreCase("success")){
                    //Utils.toast(response.get("msg").toString());
                }else{
                    Utils.toast(response.get("msg").toString());
                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }

        @Override
        public void onError() {
            Utils.dismissProgress(getApplicationContext());
            Utils.toast("Failed to save token!");
        }
    }


    /*******************************TEST CASES CODE ONLY*************************************/
    public TextInputEditText getmUsernameEditText() {
        return mUsernameEditText;
    }

    public void setmUsernameEditText(TextInputEditText mUsernameEditText) {
        this.mUsernameEditText = mUsernameEditText;
    }

    public TextInputEditText getmPasswordEditText() {
        return mPasswordEditText;
    }

    public void setmPasswordEditText(TextInputEditText mPasswordEditText) {
        this.mPasswordEditText = mPasswordEditText;
    }

    public void setPrerequisites(String userName,String password) {
        mUsernameEditText.setText(userName);
        mPasswordEditText.setText(password);
    }

    public boolean isValidInputByUserTest(String userName,String password) {
        return isValidInputByUser(userName,password);
    }

    public void makeLoginRequestTest(String userName,String password) {
        makeLoginRequest(userName,password);
    }

    /******************************TEST CASES CODE ONLY END**********************************/

}