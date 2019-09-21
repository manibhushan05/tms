package in.aaho.android.loads;

import android.content.Context;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.design.widget.TextInputEditText;
import android.support.design.widget.TextInputLayout;
import android.support.v4.app.Fragment;
import android.text.TextUtils;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;

import org.json.JSONObject;

import com.android.volley.Request;

import in.aaho.android.loads.common.ApiResponseListener;
import in.aaho.android.loads.common.EditTextWatcher;
import in.aaho.android.loads.common.MainApplication;
import in.aaho.android.loads.common.Utils;
//import in.aaho.android.requirement.profile.PasswordChangeDialogFragment;
import in.aaho.android.loads.requests.ResetPasswordRequest;

/**
 * Created by aaho on 18/04/18.
 */

/**
 * A simple {@link Fragment} subclass.
 * Activities that contain this fragment must implement the
 * {@link OnResetPasswordSubmitListener} interface
 * to handle interaction events.
 * Use the {@link ResetPasswordFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class ResetPasswordFragment extends Fragment implements View.OnClickListener {

    private Button btnReset;
    private TextInputEditText newPasswordEditText,confirmPasswordEditText;
    private TextInputLayout newPasswordTextInputLayout,confirmPasswordTextInputLayout;

    private OnResetPasswordSubmitListener mListener;

    private String username = "";

    public ResetPasswordFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     * @return A new instance of fragment ForgotPasswordFragment.
     */
    public static ResetPasswordFragment newInstance(String username) {
        ResetPasswordFragment fragment = new ResetPasswordFragment();
        Bundle args = new Bundle();
        args.putString(OTPFragment.USERNAME_KEY, username);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            username = getArguments().getString(OTPFragment.USERNAME_KEY);
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
        btnReset = (Button) view.findViewById(R.id.btnReset);
        btnReset.setOnClickListener(this);
        newPasswordEditText = (TextInputEditText) view.findViewById(R.id.newPasswordEditText);
        confirmPasswordEditText = (TextInputEditText) view.findViewById(R.id.confirmPasswordEditText);
        newPasswordTextInputLayout = (TextInputLayout) view.findViewById(R.id.newPasswordTextInputLayout);
        confirmPasswordTextInputLayout = (TextInputLayout) view.findViewById(R.id.confirmPasswordTextInputLayout);
    }

    private void makePasswordResetRequest(String username,String newPass) {
        ResetPasswordRequest passRequest = new ResetPasswordRequest(username,newPass,
                new ResetPasswordListener());
        queue(passRequest);
    }

    private class ResetPasswordListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            Utils.dismissProgress(getActivity());
            Utils.toast("Password reset successfully!");
            onSubmit();
        }

        @Override
        public void onError() {
            Utils.dismissProgress(getActivity());
            Utils.toast("Failed to reset password!");
        }
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
        String newPassword = newPasswordEditText.getText().toString();
        String confirmPassword = confirmPasswordEditText.getText().toString();
        boolean isValidPassword = newPassword.matches("^(?=.*[A-Za-z])(?=.*\\d)[A-Za-z\\d@#$%_&.]{8,}$");
        if(TextUtils.isEmpty(newPassword)) {
            newPasswordTextInputLayout.setError("New password can not be left blank!");
            return false;
        } else if(TextUtils.isEmpty(confirmPassword)) {
            confirmPasswordTextInputLayout.setError("Confirm password can not be left blank!");
            return false;
        } else if(newPassword.length() < 8) {
            confirmPasswordTextInputLayout.setError("Password length should be at least 8 character!");
            return false;
        } else if(!newPassword.equals(confirmPassword)) {
            confirmPasswordTextInputLayout.setError("New password and Confirm password must be same!");
            return false;
        } else if(!isValidPassword) {
            confirmPasswordTextInputLayout.setError("Password should contain," +
                    "\nat least one character," +
                    "\nat least one numeric," +
                    "\nand length should be at least 8 digit!" +
                    "\nSpecial character should be: @, #, $, %, _, ., &");
            return false;
        } else {
            return true;
        }
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
            Utils.showProgress(getActivity());
        }
    }

}

