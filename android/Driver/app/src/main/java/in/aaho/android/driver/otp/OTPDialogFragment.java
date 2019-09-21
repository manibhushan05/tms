package in.aaho.android.driver.otp;

import android.os.Bundle;
import android.support.annotation.Nullable;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.driver.Aaho;
import in.aaho.android.driver.R;
import in.aaho.android.driver.RegisterDialogFragment;
import in.aaho.android.driver.common.ApiResponseListener;
import in.aaho.android.driver.common.BaseActivity;
import in.aaho.android.driver.common.BaseDialogFragment;
import in.aaho.android.driver.requests.Api;
import in.aaho.android.driver.requests.EditDriverDetailsRequest;
import in.aaho.android.driver.requests.RegisterVehicleRequest;

/**
 * Created by shobhit on 8/8/16.
 */

public class OTPDialogFragment extends BaseDialogFragment {

    private View dialogView;

    private OtpStateMachine otpStateMachine;
    private String phoneNumber;

    private RegisterDialogFragment.OnCompleteListener listener;


    public static void showNewDialog(BaseActivity activity, String phoneNumber, RegisterDialogFragment.OnCompleteListener listener) {
        OTPDialogFragment fragment = new OTPDialogFragment();
        fragment.setActivity(activity);
        fragment.phoneNumber = phoneNumber;
        fragment.listener = listener;
        fragment.show(activity.getSupportFragmentManager(), "register_dialog");
    }

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

    }

    private void setVerified() {
        Aaho.setNumberVerified();
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        dialogView = inflater.inflate(R.layout.otp_dialog, container, false);

        setViewVariables();
        setSavedValues();
        setClickListeners();

        otpStateMachine = new OtpStateMachine(getBaseActivity(), dialogView, phoneNumber, new OtpStateMachine.OnChangeListener() {
            @Override
            public void onSuccess() {
                toast("Success verifying phone number");
                setVerified();
                listener.onComplete();
                dismiss();
            }

            @Override
            public void onCancel() {
                toast("Canceled");
                listener.onComplete();
                dismiss();
            }
        });
        otpStateMachine.activate();

        return dialogView;
    }



    private void setClickListeners() {

    }

    private void setViewVariables() {

    }

    public void setSavedValues() {

    }

    @Override
    public void dismiss() {
        super.dismiss();
        if (otpStateMachine != null) {
            otpStateMachine.unregister();
        }
    }
}