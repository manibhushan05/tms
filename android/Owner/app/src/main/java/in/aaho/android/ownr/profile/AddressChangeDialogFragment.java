package in.aaho.android.ownr.profile;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;

import in.aaho.android.ownr.common.BaseDialogFragment;
import in.aaho.android.ownr.R;

/**
 * Created by shobhit on 8/8/16.
 */

public class AddressChangeDialogFragment extends BaseDialogFragment {

    private Button doneButton, cancelButton;
    private EditText curPassEditText, newPassEditText, confirmPassEditText;
    private View dialogView;
    private ProfileActivity profileActivity;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        dialogView = inflater.inflate(R.layout.password_change_dialog, container, false);

        setViewVariables();
        setClickListeners();
        //setUpAdapters();

        return dialogView;
    }

    private void setClickListeners() {
        doneButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String currPass = curPassEditText.getText().toString();
                String newPass = newPassEditText.getText().toString();
                String confirmPass = confirmPassEditText.getText().toString();

                if (currPass.length() == 0) {
                    curPassEditText.setError("This field cannot be left blank");
                    return;
                }
                if (newPass.length() == 0) {
                    newPassEditText.setError("This field cannot be left blank");
                    return;
                }
                if (confirmPass.length() == 0) {
                    confirmPassEditText.setError("This field cannot be left blank");
                    return;
                }
                if (!newPass.equals(confirmPass)) {
                    confirmPassEditText.setError("Passwords do not Match");
                    return;
                }
                if (newPass.length() < 8) {
                    newPassEditText.setError("Password must be at least 8 characters long");
                    return;
                }

                //updateAddress();
                profileActivity.updateAddressText();
                AddressChangeDialogFragment.this.dismiss();
            }
        });
        cancelButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                AddressChangeDialogFragment.this.dismiss();
            }
        });
    }

    private void setViewVariables() {
        doneButton = dialogView.findViewById(R.id.password_dialog_update_btn);
        cancelButton = dialogView.findViewById(R.id.password_dialog_cancel_btn);
        curPassEditText = dialogView.findViewById(R.id.current_password_edittext);
        newPassEditText = dialogView.findViewById(R.id.new_password_edittext);
        confirmPassEditText = dialogView.findViewById(R.id.confirm_new_password_edittext);
    }

    public void setActivity(ProfileActivity profileActivity) {
        this.profileActivity = profileActivity;
    }
}