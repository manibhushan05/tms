package in.aaho.android.customer.profile;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.customer.common.ApiResponseListener;
import in.aaho.android.customer.common.BaseActivity;
import in.aaho.android.customer.common.BaseDialogFragment;
import in.aaho.android.customer.R;
import in.aaho.android.customer.booking.Vendor;
import in.aaho.android.customer.requests.VendorAddRequest;

/**
 * Created by shobhit on 8/8/16.
 */

public class VendorAddDialogFragment extends BaseDialogFragment {

    private Button addButton, cancelButton;
    private EditText nameEditText, phoneEditText;
    private View dialogView;
    private UpdateVendorListener listener;

    public static void showNewDialog(BaseActivity activity, UpdateVendorListener listener) {
        VendorAddDialogFragment vendorAddDialog = new VendorAddDialogFragment();
        vendorAddDialog.setListener(listener);
        vendorAddDialog.setActivity(activity);
        vendorAddDialog.show(activity.getSupportFragmentManager(), "add_vendor_dialog");
    }

    public interface UpdateVendorListener {
        void onVendorUpdate();
    }

    public void setListener(UpdateVendorListener listener) {
        this.listener = listener;
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        dialogView = inflater.inflate(R.layout.add_vendor_dialog, container, false);

        setViewVariables();
        setClickListeners();

        return dialogView;
    }

    private void setClickListeners() {
        addButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String name = nameEditText.getText().toString();
                String phone = phoneEditText.getText().toString();

                if (name.length() == 0) {
                    nameEditText.setError("This field cannot be left blank");
                    return;
                }
                if (phone.length() == 0) {
                    phoneEditText.setError("This field cannot be left blank");
                    return;
                }
                makeVendorAddRequest(name, phone);
            }
        });
        cancelButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                VendorAddDialogFragment.this.dismiss();
            }
        });
    }

    private void setViewVariables() {
        addButton = (Button) dialogView.findViewById(R.id.add_vendor_dialog_add_btn);
        cancelButton = (Button) dialogView.findViewById(R.id.add_vendor_dialog_cancel_btn);
        nameEditText = (EditText) dialogView.findViewById(R.id.add_vendor_name_edittext);
        phoneEditText = (EditText) dialogView.findViewById(R.id.add_vendor_phone_edittext);
    }

    private void makeVendorAddRequest(String name, String phone) {
        VendorAddRequest vendorAddRequest = new VendorAddRequest(name, phone, new VendorAddListener());
        queue(vendorAddRequest);
    }

    private class VendorAddListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            try {
                Vendor.createFromJson(response.getJSONArray("vendors"));
                listener.onVendorUpdate();
            } catch (JSONException e) {
                e.printStackTrace();
            }
            toast("Vendor Added");
            dismiss();
        }

        @Override
        public void onError() {
            dismissProgress();
            dismiss();
        }
    }
}