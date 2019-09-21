package in.aaho.android.driver;

import android.content.IntentFilter;
import android.os.Bundle;
import android.support.annotation.Nullable;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import com.android.volley.Response;
import com.android.volley.VolleyError;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.driver.common.ApiResponseListener;
import in.aaho.android.driver.common.BaseActivity;
import in.aaho.android.driver.common.BaseDialogFragment;
import in.aaho.android.driver.common.Utils;
import in.aaho.android.driver.otp.OTPDialogFragment;
import in.aaho.android.driver.requests.Api;
import in.aaho.android.driver.requests.EditDriverDetailsRequest;
import in.aaho.android.driver.requests.RegisterVehicleRequest;

/**
 * Created by shobhit on 8/8/16.
 */

public class RegisterDialogFragment extends BaseDialogFragment {

    private Button registerButton, cancelButton;
    private EditText vehicleNumberEditText, vehicleTypeEditText, phoneEditText, nameEditText;
    private ImageView checkImage;
    private TextView verifyBtn;
    private View dialogView;

    private CheckBox termsCheckBox;
    private TextView termsOpenTextView;

    private OnCompleteListener listener;

    private boolean edit = false;

    public void setEdit(boolean edit) {
        this.edit = edit;
    }

    public static void showNewDialog(BaseActivity activity, boolean edit, OnCompleteListener listener) {
        RegisterDialogFragment fragment = new RegisterDialogFragment();
        fragment.setActivity(activity);
        fragment.setEdit(edit);
        fragment.listener = listener;
        fragment.show(activity.getSupportFragmentManager(), "register_dialog");
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        dialogView = inflater.inflate(R.layout.register_dialog, container, false);

        setViewVariables();
        setSavedValues();
        setClickListeners();

        return dialogView;
    }

    private class RegClickListener implements View.OnClickListener {
        @Override
        public void onClick(View v) {
            String vehicleNumber = vehicleNumberEditText.getText().toString();
            String vehicleType = vehicleTypeEditText.getText().toString();
            String driverName = nameEditText.getText().toString();
            String mobileNumber = phoneEditText.getText().toString();

            if (!termsCheckBox.isChecked()) {
                termsCheckBox.setError("You must accept the Terms and Conditions to continue");
                return;
            }

            if (edit) {
                editDeviceDetails(vehicleNumber, vehicleType, driverName, mobileNumber);
            } else {
                registerDevice(vehicleNumber, vehicleType, driverName, mobileNumber);
            }
        }
    }


    private void setClickListeners() {
        registerButton.setOnClickListener(new RegClickListener());
        cancelButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dismiss();
            }
        });
        verifyBtn.setOnClickListener(new RegClickListener());
        termsOpenTextView.setOnClickListener(new OpenTermsDialogListener());
    }

    private class OpenTermsDialogListener implements View.OnClickListener {
        @Override
        public void onClick(View v) {
            showTermsDialog();
        }
    }

    void showTermsDialog() {
        TermsDialogFragment dialogFragment = new TermsDialogFragment();
        dialogFragment.show(getBaseActivity().getSupportFragmentManager(), "tnc_dialog");
    }

    private void setViewVariables() {
        vehicleNumberEditText = (EditText) dialogView.findViewById(R.id.input_vehicle_num);
        vehicleTypeEditText = (EditText) dialogView.findViewById(R.id.input_vehicle_type);
        nameEditText = (EditText) dialogView.findViewById(R.id.input_driver_name);
        phoneEditText = (EditText) dialogView.findViewById(R.id.input_driver_phone_number);
        registerButton = (Button) dialogView.findViewById(R.id.dialog_register_btn);
        cancelButton = (Button) dialogView.findViewById(R.id.dialog_cancel_btn);
        checkImage = (ImageView) dialogView.findViewById(R.id.check_img);
        verifyBtn = (TextView) dialogView.findViewById(R.id.verify_btn);

        termsCheckBox = (CheckBox) dialogView.findViewById(R.id.terms_checkbox);
        termsOpenTextView = (TextView) dialogView.findViewById(R.id.terms_open_btn);
        if (edit) {
            registerButton.setText(R.string.edit_registration);
        }
    }

    public void setSavedValues() {
        String vehicleNumber = Aaho.getVehicleNumber();
        String vehicleType = Aaho.getVehicleType();
        String driverName = Aaho.getDriverName();
        String driverNumber = Aaho.getMobileNumber();
        boolean numberVerified = Aaho.getNumberVerified();

        if (vehicleNumber != null) vehicleNumberEditText.setText(vehicleNumber);
        if (vehicleType != null) vehicleTypeEditText.setText(vehicleType);
        if (driverName != null) nameEditText.setText(driverName);
        if (driverNumber != null) phoneEditText.setText(driverNumber);

        if (numberVerified) {
            checkImage.setVisibility(View.VISIBLE);
            verifyBtn.setVisibility(View.GONE);
        } else {
            if (Utils.not(driverNumber)) {
                checkImage.setVisibility(View.GONE);
                verifyBtn.setVisibility(View.GONE);
            } else {
                checkImage.setVisibility(View.GONE);
                verifyBtn.setVisibility(View.VISIBLE);
            }
        }
    }

    private JSONObject getData(String vehicleNumber, String vehicleType,
                               String driverName, String mobileNumber){
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put("device_id", Aaho.getDeviceId());
            jsonObject.put("vehicle_number", vehicleNumber);
            jsonObject.put("vehicle_type", vehicleType);
            jsonObject.put("driver_name", driverName);
            jsonObject.put("driver_number", mobileNumber);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return jsonObject;
    }

    private class EditResponseListener extends ApiResponseListener {
        private final boolean edit;

        public EditResponseListener(boolean edit) {
            this.edit = edit;
        }

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            try {
                Log.e("response", response + "    from server");
                if (response.getString("status").equals(Api.STATUS_SUCCESS)) {
                    Log.e("SUCCESS", Api.STATUS_SUCCESS);
                    Aaho.updateFromResponse(response);
                    boolean numberVerified = Aaho.getNumberVerified();
                    String phoneNumber = Aaho.getMobileNumber();
                    if (!edit) {
                        String authToken = response.getString("auth_token");
                        Aaho.setAuthToken(authToken);
                    }
                    int successMsg = edit ? R.string.edit_success : R.string.register_success;
                    Toast.makeText(getActivity(), successMsg, Toast.LENGTH_SHORT).show();
                    if (!Utils.not(phoneNumber) && !numberVerified) {
                        showOTPDialog(phoneNumber, listener);
                        dismiss();
                    } else {
                        listener.onComplete();
                        dismiss();
                    }
                } else {
                    // TODO: implement retry in background
                    throw new AssertionError(response.toString());
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }

        @Override
        public void onError() {
            dismissProgress();
        }
    }

    public interface OnCompleteListener {
        void onComplete();
    }

    private void showOTPDialog(String mobileNumber, OnCompleteListener listener) {
        OTPDialogFragment.showNewDialog(getBaseActivity(), mobileNumber, listener);
    }

    private void registerDevice(String vehicleNumber, String vehicleType,
                                String driverName, String mobileNumber){
        RegisterVehicleRequest registerVehicleRequest = new RegisterVehicleRequest(
                getData(vehicleNumber, vehicleType, driverName, mobileNumber),
                new EditResponseListener(false)
        );
        queue(registerVehicleRequest);
    }

    private void editDeviceDetails(String vehicleNumber, String vehicleType,
                                   String driverName, String mobileNumber){
        EditDriverDetailsRequest editDriverDetailsRequest = new EditDriverDetailsRequest(
                getData(vehicleNumber, vehicleType, driverName, mobileNumber),
                new EditResponseListener(true)
        );
        queue(editDriverDetailsRequest);
    }



}