package in.aaho.android.aahocustomers.vehicles;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.aahocustomers.R;
import in.aaho.android.aahocustomers.common.ApiResponseListener;
import in.aaho.android.aahocustomers.common.BaseActivity;
import in.aaho.android.aahocustomers.common.BaseDialogFragment;
import in.aaho.android.aahocustomers.requests.DriverAddEditRequest;

/**
 * Created by shobhit on 8/8/16.
 */

public class DriverAddDialogFragment extends BaseDialogFragment {

    private Button doneButton, cancelButton;
    private EditText nameEditText, phoneEditText;
    private View dialogView;

    private DriverAddListener driverAddListener;

    public static void showNewDialog(BaseActivity activity, DriverAddListener driverAddListener) {
        DriverAddDialogFragment dialog = new DriverAddDialogFragment();
        dialog.setDriverAddListener(driverAddListener);
        dialog.setActivity(activity);
        dialog.show(activity.getSupportFragmentManager(), "driver_add_fragment");
    }

    public void setDriverAddListener(DriverAddListener driverAddListener) {
        this.driverAddListener = driverAddListener;
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        dialogView = inflater.inflate(R.layout.driver_add_dialog, container, false);

        setViewVariables();
        setClickListeners();

        return dialogView;
    }

    private void setClickListeners() {
        doneButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String name = nameEditText.getText().toString().trim();
                String phone = phoneEditText.getText().toString().trim();

                if (name.length() == 0) {
                    nameEditText.setError("This field cannot be left blank");
                    return;
                }
                if (phone.length() == 0) {
                    phoneEditText.setError("This field cannot be left blank");
                    return;
                }
                makeDriverAddRequest(name, phone);
            }
        });
        cancelButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dismiss();
            }
        });
    }

    private void setViewVariables() {
        doneButton = dialogView.findViewById(R.id.owner_add_dialog_add_btn);
        cancelButton = dialogView.findViewById(R.id.owner_add_dialog_cancel_btn);
        nameEditText = dialogView.findViewById(R.id.owner_name_edittext);
        phoneEditText = dialogView.findViewById(R.id.owner_phone_edittext);
    }

    private void makeDriverAddRequest(String name, String phone) {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put("name", name);
            jsonObject.put("phone", phone);
        } catch (JSONException e) {
            toast("Error forming jsonObject");
            return;
        }
        DriverAddEditRequest request = new DriverAddEditRequest(jsonObject, new DriverAddEditListener());
        queue(request);
    }

    private class DriverAddEditListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            toast("Driver Added");
            if (driverAddListener != null) {
                try {
                    VehicleDriver driver = getDriver(response);
                    driverAddListener.onDriverAdd(driver);
                } catch (JSONException e) {
                    toast("error reading response");
                    return;
                }
            }
            dismiss();
        }

        @Override
        public void onError() {
            dismissProgress();
            dismiss();
        }
    }

    private VehicleDriver getDriver(JSONObject jsonObject) throws JSONException {
        JSONObject data = jsonObject.getJSONObject("data");
        return VehicleDriver.fromJson(data);
    }


    public interface DriverAddListener {
        void onDriverAdd(VehicleDriver driver);
    }

}