package in.aaho.android.aahocustomers.login_options;

import android.content.Intent;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.design.widget.TextInputEditText;
import android.support.design.widget.TextInputLayout;
import android.support.v4.app.Fragment;
import android.text.Editable;
import android.text.TextUtils;
import android.text.TextWatcher;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

import org.json.JSONObject;

import in.aaho.android.aahocustomers.AppDataActivity;
import in.aaho.android.aahocustomers.LoginActivity;
import in.aaho.android.aahocustomers.R;
import in.aaho.android.aahocustomers.common.ApiResponseListener;
import in.aaho.android.aahocustomers.common.BaseActivity;
import in.aaho.android.aahocustomers.common.EditTextWatcher;
import in.aaho.android.aahocustomers.requests.LoginRequest;

/**
 * Created by aaho on 09/05/18.
 */
public class LoginPasswordFragment extends Fragment implements View.OnClickListener {
//    public static final String ARG_OBJECT = "object";

    Button mLoginButton;
    //TextView tvForgotPassword;
    TextInputEditText mUsernameEditText;
    TextInputEditText mPasswordEditText;
    TextInputLayout mUserNameTextInputLayout,mPasswordTextInputLayout;


    @Override
    public View onCreateView(LayoutInflater inflater,
                             ViewGroup container, Bundle savedInstanceState) {
        // The last two arguments ensure LayoutParams are inflated
        // properly.
        View rootView = inflater.inflate(
                R.layout.activity_login, container, false);
        Bundle args = getArguments();
//        print("First Fragment");
//        ((TextView) rootView.findViewById(android.R.id.text1)).setText(
//                "First Fragment");
        setViewRefs(rootView);
//        setClickListeners();

        return rootView;
    }


    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

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

//        queue(loginRequest);
    }
    private class LoginListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            mLoginButton.setClickable(true);
//           fetchData(true);
        }

        @Override
        public void onError() {
//            dismissProgress();
            mLoginButton.setClickable(true);
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

    private void setViewRefs(View view) {
        mUsernameEditText = view.findViewById(R.id.input_username);
        mPasswordEditText = view.findViewById(R.id.input_password);
        mLoginButton = view.findViewById(R.id.btn_login);
        mPasswordTextInputLayout = view.findViewById(R.id.passwordTextInputLayout);
        mUserNameTextInputLayout = view.findViewById(R.id.userNameTextInputLayout);
        //tvForgotPassword = (TextView) findViewById(R.id.tvForgotPassword);
        //tvForgotPassword.setOnClickListener(this);
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
