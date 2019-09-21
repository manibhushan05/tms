package in.aaho.android.loads;

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


import com.msg91.sendotp.library.SendOtpVerification;
import com.msg91.sendotp.library.Verification;
import com.msg91.sendotp.library.VerificationListener;

import in.aaho.android.loads.common.EditTextWatcher;
import in.aaho.android.loads.common.Utils;

/**
 * Created by aaho on 18/04/18.
 */

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
    private String phoneNo = "";
    private String username = "";
    private final int OTP_EXPIRY_MINUTE = 5;
    private final int RESEND_OTP_MINUTE = 1;

    /** Verification Listener for OTP by MSG91 */
    private Verification mVerification;
    private OnOTPSubmitListener mListener;

    public OTPFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     * @return A new instance of fragment ForgotPasswordFragment.
     * @param phoneNo
     */
    public static OTPFragment newInstance(String phoneNo, String username) {
        OTPFragment fragment = new OTPFragment();
        Bundle args = new Bundle();
        args.putString(PHONE_NO_KEY, phoneNo);
        args.putString(USERNAME_KEY, username);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            phoneNo = getArguments().getString(PHONE_NO_KEY);
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

        String otpMessage = "A OTP has been sent to "+phoneNo
                +"\nWe are trying to detect it automatically, in case we failed "
                +"to detect it,\nPlease enter the OTP in the field below to verify";
        tvOTPLabel.setText(otpMessage);

        otp_editext.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                if(i == 0) {
                    OTPTextInputLayout.setError(null);
                }
            }
        });

        /** send otp to given mobile no for verification */
        doOTPVerifiction(phoneNo);
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

    public void onSubmit() {
        if (mListener != null) {
            mListener.onOTPSubmit(username);
        }
    }

    void findViews(View view) {
        tvOTPLabel = (TextView) view.findViewById(R.id.tvOTPLabel);
        tvResendOTP = (TextView) view.findViewById(R.id.tvResendOTP);
        tvResendOTP.setOnClickListener(this);
        btnSubmit = (Button) view.findViewById(R.id.btnSubmit);
        btnSubmit.setOnClickListener(this);
        otp_editext = (TextInputEditText) view.findViewById(R.id.otp_editext);
        OTPTextInputLayout = (TextInputLayout) view.findViewById(R.id.OTPTextInputLayout);
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
                mVerification.resend("voice");
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

    private void verifyOTP(String OTP) {
        Utils.showProgress(getActivity());
        mVerification.verify(OTP);
    }


    @Override
    public void onInitiated(String response) {
        Log.i(TAG,"onInitiated");
        //Utils.showProgress(getActivity());
    }

    @Override
    public void onInitiationFailed(Exception paramException) {
        Log.i(TAG,"onInitiationFailed");
        Utils.dismissProgress(getActivity());
    }

    @Override
    public void onVerified(String response) {
        Log.i(TAG,"onVerified");
        // OTP verified successfully
        Utils.dismissProgress(getActivity());
        onSubmit();
    }

    @Override
    public void onVerificationFailed(Exception paramException) {
        Log.i(TAG,"onVerificationFailed");
        Utils.dismissProgress(getActivity());
        Utils.toast(paramException.getMessage());
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
        void onOTPSubmit(String username);
    }

    private void startTimer() {
        tvResendOTP.setClickable(false);
        tvResendOTP.setTextColor(ContextCompat.getColor(getActivity(), R.color.colorPrimaryText));
        new CountDownTimer(RESEND_OTP_MINUTE *60000, 1000) {
            int secondsLeft = 0;

            public void onTick(long ms) {
                if (Math.round((float) ms / 1000.0f) != secondsLeft) {
                    secondsLeft = Math.round((float) ms / 1000.0f);
                    tvResendOTP.setText("Resend via call ( " + secondsLeft + " )");
                }
            }

            public void onFinish() {
                tvResendOTP.setClickable(true);
                tvResendOTP.setText("Resend via call");
                tvResendOTP.setTextColor(ContextCompat.getColor(getActivity(), R.color.colorPrimary));
            }
        }.start();
    }

}
