package in.aaho.android.ownr;

import android.app.ProgressDialog;
import android.content.Context;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.design.widget.TextInputEditText;
import android.support.design.widget.TextInputLayout;
import android.support.v4.app.Fragment;
import android.text.TextUtils;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

import com.android.volley.Request;
import com.android.volley.VolleyError;

import org.json.JSONObject;

import java.io.UnsupportedEncodingException;

import in.aaho.android.ownr.common.ApiResponseListener;
import in.aaho.android.ownr.common.EditTextWatcher;
import in.aaho.android.ownr.common.MainApplication;
import in.aaho.android.ownr.common.Utils;
import in.aaho.android.ownr.requests.ResetPasswordRequest;


/**
 * A simple {@link Fragment} subclass.
 * Activities that contain this fragment must implement the
 * {@link OnResetPasswordSubmitListener} interface
 * to handle interaction events.
 * Use the {@link ResetPasswordFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class ResetPasswordFragment extends Fragment implements View.OnClickListener {
    private final String TAG = getClass().getSimpleName();
    private TextView tvMsg;
    private Button btnReset;
    private TextInputEditText newPasswordEditText,confirmPasswordEditText;
    private TextInputLayout newPasswordTextInputLayout,confirmPasswordTextInputLayout;

    private OnResetPasswordSubmitListener mListener;

    private String username = "";
    private String token = "";
    private ProgressDialog progress;

    public ResetPasswordFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     * @return A new instance of fragment ForgotPasswordFragment.
     */
    public static ResetPasswordFragment newInstance(String username, String token) {
        ResetPasswordFragment fragment = new ResetPasswordFragment();
        Bundle args = new Bundle();
        args.putString(OTPFragment.USERNAME_KEY, username);
        args.putString(OTPFragment.TOKEN_KEY, token);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            username = getArguments().getString(OTPFragment.USERNAME_KEY);
            token = getArguments().getString(OTPFragment.TOKEN_KEY);
        }
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View view = inflater.inflate(R.layout.fragment_reset_password, container, false);
        findViews(view);
        return view;
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        newPasswordEditText.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                if(i == 0) {
                    newPasswordTextInputLayout.setError(null);
                }
            }
        });

        confirmPasswordEditText.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                if(i == 0) {
                    confirmPasswordTextInputLayout.setError(null);
                }
            }
        });
    }

    public void onSubmit() {
        if (mListener != null) {
            mListener.onResetPasswordSubmit();
        }
    }

    @Override
    public void onAttach(Context context) {
        super.onAttach(context);
        if (context instanceof OnResetPasswordSubmitListener) {
            mListener = (OnResetPasswordSubmitListener) context;
        } else {
            throw new RuntimeException(context.toString()
                    + " must implement OnResetPasswordSubmitListener");
        }
    }

    @Override
    public void onDetach() {
        super.onDetach();
        mListener = null;
    }

    void findViews(View view) {
        btnReset = view.findViewById(R.id.btnReset);
        btnReset.setOnClickListener(this);
        newPasswordEditText = view.findViewById(R.id.newPasswordEditText);
        confirmPasswordEditText = view.findViewById(R.id.confirmPasswordEditText);
        newPasswordTextInputLayout = view.findViewById(R.id.newPasswordTextInputLayout);
        confirmPasswordTextInputLayout = view.findViewById(R.id.confirmPasswordTextInputLayout);
        tvMsg = view.findViewById(R.id.tvMsg);
    }

    private void makePasswordResetRequest(String username, String newPass) {
        Aaho.setToken(token);
        ResetPasswordRequest passRequest = new ResetPasswordRequest(username,newPass,
                new ResetPasswordListener());
        queue(passRequest);
    }

    private class ResetPasswordListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            Utils.toast("Password reset successfully!");
            Aaho.setToken(""); // reset token to allow user login again
            onSubmit();
        }

        @Override
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);
            dismissProgress();
            try {
                if (error != null && error.networkResponse != null
                        && error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    JSONObject errorData = new JSONObject(errorMsg);
                    Utils.showInfoDialog(getActivity(),
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
            Aaho.setToken(""); // reset token to allow user login again
            Utils.dismissProgress(getActivity());
            Utils.toast("Failed to reset password!");
        }*/
    }

    @Override
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.btnReset:
                if(isValidInputByUser()) {
                    makePasswordResetRequest(username,newPasswordEditText.getText().toString());
                }
                break;
            default:
                break;
        }
    }

    boolean isValidInputByUser() {
        boolean isValid = true;
        setMsgText("");
        String newPassword = newPasswordEditText.getText().toString();
        String confirmPassword = confirmPasswordEditText.getText().toString();
        boolean isValidPassword = newPassword.matches("^(?=.*[A-Za-z])(?=.*\\d)[A-Za-z\\d@#$%_&.]{8,}$");
        if(TextUtils.isEmpty(newPassword)) {
            newPasswordTextInputLayout.setError("New password can not be left blank!");
            isValid = false;
        }
        if(TextUtils.isEmpty(confirmPassword)) {
            confirmPasswordTextInputLayout.setError("Confirm password can not be left blank!");
            isValid = false;
        } else {
            if (newPassword.length() < 8 || confirmPassword.length() < 8) {
                setMsgText("Password length should be at least 8 character!");
                isValid = false;
            } else if (!newPassword.equals(confirmPassword)) {
                setMsgText("New password and Confirm password must be same!");
                isValid = false;
            } else {
                if (!isValidPassword) {
                    setMsgText("Password should contain," +
                            "\nat least one character," +
                            "\nat least one numeric," +
                            "\nand length should be at least 8 digit!" +
                            "\nSpecial character should be: @, #, $, %, _, ., &");
                    isValid = false;
                } else {
                    setMsgText("");
                }
            }
        }

        return isValid;
    }

    /**
     * This interface must be implemented by activities that contain this
     * fragment to allow an interaction in this fragment to be communicated
     * to the activity and potentially other fragments contained in that
     * activity.
     * <p>
     * See the Android Training lesson <a href=
     * "http://developer.android.com/training/basics/fragments/communicating.html"
     * >Communicating with Other Fragments</a> for more information.
     */
    public interface OnResetPasswordSubmitListener {
        void onResetPasswordSubmit();
    }

    public void queue(Request<?> request) {
        queue(request, true);
    }

    public void queue(Request<?> request, boolean progress) {
        MainApplication.queueRequest(request);
        if (progress) {
            if(!getActivity().isFinishing())
                showProgress();
        }
    }

    private void setMsgText(String msgText) {
        if(TextUtils.isEmpty(msgText)) {
            tvMsg.setText("");
            tvMsg.setVisibility(View.INVISIBLE);
        } else {
            tvMsg.setText(msgText);
            tvMsg.setVisibility(View.VISIBLE);
        }
    }

    private void showProgress() {
        progress = new ProgressDialog(getActivity());
        progress.setTitle(R.string.progress_title);
        progress.setMessage(getActivity().getString(R.string.progress_msg));
        progress.setCanceledOnTouchOutside(false);
        progress.show();
    }

    private void dismissProgress() {
        if(progress != null) {
            progress.dismiss();
        }
    }

}
