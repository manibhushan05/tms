package in.aaho.android.ownr;

import android.app.ProgressDialog;
import android.content.Context;
import android.os.Bundle;
import android.os.CountDownTimer;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.design.widget.TextInputEditText;
import android.support.design.widget.TextInputLayout;
import android.support.v4.app.Fragment;
import android.support.v4.content.ContextCompat;
import android.text.TextUtils;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

import com.android.volley.Request;
import com.android.volley.VolleyError;
import com.msg91.sendotp.library.SendOtpVerification;
import com.msg91.sendotp.library.Verification;
import com.msg91.sendotp.library.VerificationListener;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.UnsupportedEncodingException;

import in.aaho.android.ownr.common.ApiResponseListener;
import in.aaho.android.ownr.common.EditTextWatcher;
import in.aaho.android.ownr.common.MainApplication;
import in.aaho.android.ownr.common.Utils;
import in.aaho.android.ownr.requests.ForgotPasswordRequest;
import in.aaho.android.ownr.requests.VerifyOtpRequest;


/**
 * A simple {@link Fragment} subclass.
 * Activities that contain this fragment must implement the
 * {@link OnOTPSubmitListener} interface
 * to handle interaction events.
 * Use the {@link OTPFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class OTPFragment extends Fragment implements
        View.OnClickListener,VerificationListener {

    private final String TAG = getClass().getSimpleName();
    private TextView tvOTPLabel,tvResendOTP;
    private Button btnSubmit;
    private TextInputEditText otp_editext;
    private TextInputLayout OTPTextInputLayout;

    public static final String PHONE_NO_KEY = "phoneNoKey";
    public static final String USERNAME_KEY = "usernameKey";
    public static final String MESSAGE_KEY = "msgKey";
    public static final String TOKEN_KEY = "tokenKey";
    private String phoneNo = "";
    private String username = "";
    private String message = "";
    private final int OTP_EXPIRY_MINUTE = 5;
    private final int RESEND_OTP_MINUTE = 1;

    /** Verification Listener for OTP by MSG91 */
    private Verification mVerification;
    private OnOTPSubmitListener mListener;

    private ProgressDialog progress;

    public OTPFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     * @return A new instance of fragment ForgotPasswordFragment.
     * @param msg message
     */
    public static OTPFragment newInstance(String msg, String username) {
        OTPFragment fragment = new OTPFragment();
        Bundle args = new Bundle();
        args.putString(MESSAGE_KEY, msg);
        args.putString(USERNAME_KEY, username);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            message = getArguments().getString(MESSAGE_KEY);
            username = getArguments().getString(USERNAME_KEY);
        }
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View view = inflater.inflate(R.layout.fragment_otp, container, false);
        findViews(view);
        return view;
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        tvOTPLabel.setText(message);

        otp_editext.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                if(i == 0) {
                    OTPTextInputLayout.setError(null);
                }
            }
        });

        /* We are not sending OTP from mobile side now this process is happens at back end */
        /** send otp to given mobile no for verification */
        // doOTPVerifiction(phoneNo);
    }

    @Override
    public void onAttach(Context context) {
        super.onAttach(context);
        if (context instanceof OnOTPSubmitListener) {
            mListener = (OnOTPSubmitListener) context;
        } else {
            throw new RuntimeException(context.toString()
                    + " must implement OnOTPSubmitListener");
        }
    }

    @Override
    public void onDetach() {
        super.onDetach();
        mListener = null;
    }

    public void onSubmit(String token) {
        if (mListener != null) {
            mListener.onOTPSubmit(username,token);
        }
    }

    void findViews(View view) {
        tvOTPLabel = view.findViewById(R.id.tvOTPLabel);
        tvResendOTP = view.findViewById(R.id.tvResendOTP);
        tvResendOTP.setOnClickListener(this);
        btnSubmit = view.findViewById(R.id.btnSubmit);
        btnSubmit.setOnClickListener(this);
        otp_editext = view.findViewById(R.id.otp_editext);
        OTPTextInputLayout = view.findViewById(R.id.OTPTextInputLayout);
    }

    @Override
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.btnSubmit:
                if(isValidInputByUser()) {
                    verifyOTP(otp_editext.getText().toString());
                }
                break;
            case R.id.tvResendOTP:
                startTimer();
                // call otp verification api again
                makeOTPRequest();
                /*mVerification.resend("voice");*/
                break;
            default:
                break;
        }
    }

    boolean isValidInputByUser() {
        String newPassword = otp_editext.getText().toString();
        if(TextUtils.isEmpty(newPassword)) {
            OTPTextInputLayout.setError("This field can not be left blank!");
            return false;
        } else {
            return true;
        }
    }

    private void verifyOTP(String OTP) {
        /*mVerification.verify(OTP);*/
        VerifyOtpRequest verifyOtpRequest = new VerifyOtpRequest(username,OTP,
                new VerifyOtpResponseListener());
        queue(verifyOtpRequest);
    }

    private class VerifyOtpResponseListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            String resp = response.toString();
            try {
                String msg = Utils.get(response,"msg");
                if(response != null && response.getString("status")
                        .equalsIgnoreCase("success")) {
                    //This token only used to call reset API, resetting it in reset password screen
                    String token = Utils.get(response,"token");
                    onSubmit(token);
                } else {
                    Utils.toast(msg);
                }
            } catch (JSONException e) {
                e.printStackTrace();
                Utils.toast("Could not verify OTP! Please try again later.");
                Log.e(TAG,"error reading response data:\n" + resp);
            }
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
    }

    private void makeOTPRequest() {
        ForgotPasswordRequest forgotPasswordRequest = new ForgotPasswordRequest(
                username, new ForgotPasswordResponseListener());
        queue(forgotPasswordRequest);
    }

    private class ForgotPasswordResponseListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            String resp = response.toString();
            try {
                String msg = Utils.get(response,"msg");
                if(response != null && response.getString("status")
                        .equalsIgnoreCase("success")) {

                } else {
                    Utils.toast(msg);
                }
            } catch (JSONException e) {
                e.printStackTrace();
                Utils.toast("Could not send OTP! Please try again later.");
                Log.e(TAG,"error reading response data:\n" + resp);
            }
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
    public interface OnOTPSubmitListener {
        void onOTPSubmit(String username, String token);
    }

    private void startTimer() {
        tvResendOTP.setClickable(false);
        tvResendOTP.setTextColor(ContextCompat.getColor(getActivity(), R.color.colorPrimaryText));
        new CountDownTimer(RESEND_OTP_MINUTE *60000, 1000) {
            int secondsLeft = 0;

            public void onTick(long ms) {
                if (Math.round((float) ms / 1000.0f) != secondsLeft) {
                    secondsLeft = Math.round((float) ms / 1000.0f);
                    tvResendOTP.setText("Resend will enable in ( " + secondsLeft + " )");
                }
            }

            public void onFinish() {
                tvResendOTP.setClickable(true);
                tvResendOTP.setText("Resend OTP");
                tvResendOTP.setTextColor(ContextCompat.getColor(getActivity(), R.color.colorPrimary));
            }
        }.start();
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

    /*****************************UNUSED CODE******************************/
    /** This will initialize the verification process by sending the OTP
     *  to given mobile number
     * @param phoneKey phone number to which the OTP will be sent
     */
    private void doOTPVerifiction(String phoneKey) {
        mVerification = SendOtpVerification.createSmsVerification
                (SendOtpVerification
                        .config("91" + phoneKey)
                        .context(getActivity())
                        .expiry(String.valueOf(OTP_EXPIRY_MINUTE))
                        .httpsConnection(true)
                        .autoVerification(true)
                        .build(), this);

        mVerification.initiate();
    }

    @Override
    public void onInitiated(String response) {
        Log.i(TAG,"onInitiated");
        //Utils.showProgress(getActivity());
    }

    @Override
    public void onInitiationFailed(Exception paramException) {
        Log.i(TAG,"onInitiationFailed");
        /*Utils.dismissProgress(getActivity());*/
    }

    @Override
    public void onVerified(String response) {
        Log.i(TAG,"onVerified");
        // OTP verified successfully
        /*Utils.dismissProgress(getActivity());*/
        onSubmit("token");
    }

    @Override
    public void onVerificationFailed(Exception paramException) {
        Log.i(TAG,"onVerificationFailed");
        /*Utils.dismissProgress(getActivity());*/
        Utils.toast(paramException.getMessage());
    }

}
