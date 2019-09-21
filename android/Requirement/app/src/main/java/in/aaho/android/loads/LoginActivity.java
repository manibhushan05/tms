package in.aaho.android.loads;

import android.os.Bundle;
import android.support.design.widget.TextInputEditText;
import android.support.design.widget.TextInputLayout;
import android.text.TextUtils;
import android.util.Log;
import android.view.View;
import android.widget.Button;

import org.json.JSONObject;
import org.json.JSONException;

import in.aaho.android.loads.common.ApiResponseListener;
import in.aaho.android.loads.common.EditTextWatcher;
import in.aaho.android.loads.common.Utils;
import in.aaho.android.loads.requests.LoginRequest;
import in.aaho.android.loads.common.Prefs;
import in.aaho.android.loads.requests.PostFcmTokenRequest;

/**
 * Created by aaho on 18/04/18.
 */

public class LoginActivity extends AppDataActivity implements View.OnClickListener {
    private static final String TAG = "LoginActivity";
    Button mLoginButton;
    //TextView tvForgotPassword;
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
                if(response.get("status").equals("success")){
                    Utils.toast("Token Saved successfully!");
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

    @Override
    public void onClick(View view) {
//        switch (view.getId()) {
//            case R.id.tvForgotPassword:
//                // Reset editText fields
//                mUsernameEditText.setText("");
//                mPasswordEditText.setText("");
//                startActivity(new Intent(LoginActivity.this,ForgotPasswordActivity.class));
//                break;
//        }
    }

    private class LoginListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            String resp = response.toString();
            try {
                if(response.get("status").equals("success")){
                    JSONObject jsonObject = new JSONObject(resp);
                    JSONObject dataObject = jsonObject.getJSONObject("data");
                    Prefs.set("aaho_office_id", dataObject.get("aaho_office_id").toString());
                    Log.d(TAG,"DeviceID:"+Aaho.getDeviceId());
                    Log.d(TAG,"TokenID:"+Aaho.getFcmToken());
                    mLoginButton.setClickable(true);
                    fetchData(true);
                    saveTokenIdOnServer(Aaho.getFcmToken(),Aaho.getDeviceId());
                }else{
                    dismissProgress();
                    Utils.toast(response.get("msg").toString());
                    mLoginButton.setClickable(true);
                    Log.e("[LoginActivity]", "Login Failure");
                }
            } catch (JSONException e) {
                e.printStackTrace();
                toast("error decoding json");
            }

        }

        @Override
        public void onError() {
            dismissProgress();
            mLoginButton.setClickable(true);
        }
    }


    private void setViewRefs() {
        mUsernameEditText = (TextInputEditText) findViewById(R.id.input_username);
        mPasswordEditText = (TextInputEditText) findViewById(R.id.input_password);
        mLoginButton = (Button) findViewById(R.id.btn_login);
        mPasswordTextInputLayout = (TextInputLayout) findViewById(R.id.passwordTextInputLayout);
        mUserNameTextInputLayout = (TextInputLayout) findViewById(R.id.userNameTextInputLayout);
        //tvForgotPassword = (TextView) findViewById(R.id.tvForgotPassword);
        //tvForgotPassword.setOnClickListener(this);
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
        String userName = mUsernameEditText.getText().toString();
        String password = mPasswordEditText.getText().toString();
        if(TextUtils.isEmpty(userName)) {
            mUserNameTextInputLayout.setError("User name can not be left blank!");
            mLoginButton.setClickable(true);
            return false;
        } else if(TextUtils.isEmpty(password)) {
            mPasswordTextInputLayout.setError("Password can not be left blank!");
            mLoginButton.setClickable(true);
            return false;
        } else {
            return true;
        }
    }
}