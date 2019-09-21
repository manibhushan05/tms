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
import in.aaho.android.aahocustomers.requests.OwnerAddEditRequest;

/**
 * Created by shobhit on 8/8/16.
 */

public class OwnerAddDialogFragment extends BaseDialogFragment {

    private Button doneButton, cancelButton;
    private EditText nameEditText, phoneEditText;
    private View dialogView;

    private OwnerAddListener ownerAddListener;

    public static void showNewDialog(BaseActivity activity, OwnerAddListener ownerAddListener) {
        OwnerAddDialogFragment dialog = new OwnerAddDialogFragment();
        dialog.setOwnerAddListener(ownerAddListener);
        dialog.setActivity(activity);
        dialog.show(activity.getSupportFragmentManager(), "owner_add_fragment");
    }

    public void setOwnerAddListener(OwnerAddListener ownerAddListener) {
        this.ownerAddListener = ownerAddListener;
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        dialogView = inflater.inflate(R.layout.owner_add_dialog, container, false);

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
                makeOwnerAddRequest(name, phone);
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

    private void makeOwnerAddRequest(String name, String phone) {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put("name", name);
            jsonObject.put("phone", phone);
        } catch (JSONException e) {
            toast("Error forming jsonObject");
            return;
        }
        OwnerAddEditRequest request = new OwnerAddEditRequest(jsonObject, new OwnerAddEditListener());
        queue(request);
    }

    private class OwnerAddEditListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            toast("Owner Added");
            if (ownerAddListener != null) {
                try {
                    VehicleOwner owner = getOwner(response);
                    ownerAddListener.onOwnerAdd(owner);
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

    private VehicleOwner getOwner(JSONObject jsonObject) throws JSONException {
        JSONObject data = jsonObject.getJSONObject("data");
        return VehicleOwner.fromJson(data);
    }

    public interface OwnerAddListener {
        void onOwnerAdd(VehicleOwner owner);
    }

}