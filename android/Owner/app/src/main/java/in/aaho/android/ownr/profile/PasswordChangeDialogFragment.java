package in.aaho.android.ownr.profile;

import android.os.Bundle;
import android.text.TextUtils;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;

import com.android.volley.VolleyError;

import org.json.JSONObject;

import java.io.UnsupportedEncodingException;

import in.aaho.android.ownr.LoginActivity;
import in.aaho.android.ownr.common.ApiResponseListener;
import in.aaho.android.ownr.common.BaseDialogFragment;
import in.aaho.android.ownr.R;
import in.aaho.android.ownr.common.Utils;
import in.aaho.android.ownr.requests.PasswordEditRequest;
import okhttp3.internal.Util;

/**
 * Created by shobhit on 8/8/16.
 */

public class PasswordChangeDialogFragment extends BaseDialogFragment {
    private final String TAG = getClass().getSimpleName();
    private Button doneButton, cancelButton;
    private EditText curPassEditText, newPassEditText, confirmPassEditText;
    private View dialogView;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        dialogView = inflater.inflate(R.layout.password_change_dialog, container, false);

        setViewVariables();
        setClickListeners();

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

                makePasswordChangeRequest(currPass, newPass);
            }
        });
        cancelButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                PasswordChangeDialogFragment.this.dismiss();
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

    private void makePasswordChangeRequest(String currPass, String newPass) {
        PasswordEditRequest passRequest = new PasswordEditRequest(currPass, newPass, new PasswordEditListener());
        queue(passRequest);
    }

    private class PasswordEditListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            String msg = Utils.getRequestMessage(response);
            Utils.toast(msg);
            dismiss();
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
            dismissProgress();
            dismiss();
        }*/
    }
}