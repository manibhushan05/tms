package in.aaho.android.ownr.vehicles;

import android.os.Bundle;
import android.support.annotation.Nullable;
import android.text.TextUtils;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;

import com.android.volley.VolleyError;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.UnsupportedEncodingException;
import java.util.Arrays;
import java.util.List;

import in.aaho.android.ownr.Aaho;
import in.aaho.android.ownr.booking.App;
import in.aaho.android.ownr.common.ApiResponseListener;
import in.aaho.android.ownr.common.BaseActivity;
import in.aaho.android.ownr.common.BaseDialogFragment;
import in.aaho.android.ownr.R;
import in.aaho.android.ownr.common.Prefs;
import in.aaho.android.ownr.common.Utils;
import in.aaho.android.ownr.profile.Profile;
import in.aaho.android.ownr.requests.AccountAddEditRequest;

/**
 * Created by shobhit on 8/8/16.
 */

public class AccountAddDialogFragment extends BaseDialogFragment {
    private final String TAG = getClass().getSimpleName();
    private Button doneButton, cancelButton;
    private EditText bankNameEditText, acHolderNameEditText, acNumberEditText, ifscEditText;
    private Spinner acTypeSpinner;
    private View dialogView;

    private BankAccount account;

    private ArrayAdapter<String> spinnerAdapter;

    private static final List<String> acTypeTitles = Arrays.asList(
            "Savings Account", "Current Account", "Kisan Credit Card", "Recurring Account");
    private static final List<String> acTypes = Arrays.asList(
            "SA", "CA", "KCC", "RA");

    private AccountAddListener accountAddListener;

    public static void showNewDialog(BaseActivity activity, BankAccount account, AccountAddListener accountAddListener) {
        AccountAddDialogFragment dialog = new AccountAddDialogFragment();
        dialog.setAccountAddListener(accountAddListener);
        dialog.setActivity(activity);
        dialog.setAccount(account);
        dialog.show(activity.getSupportFragmentManager(), "account_add_fragment");
    }

    public void setAccountAddListener(AccountAddListener accountAddListener) {
        this.accountAddListener = accountAddListener;
    }

    public void setAccount(BankAccount account) {
        if (account == null) {
            /*account = new BankAccount(null, null, null, null, null, null);*/
            account = new BankAccount("", null, null, null, null, null);
        }
        this.account = account;
    }

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        spinnerAdapter = new ArrayAdapter<>(
                getActivity(), android.R.layout.simple_spinner_item, acTypeTitles);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        dialogView = inflater.inflate(R.layout.account_add_dialog, container, false);

        setViewVariables();
        setClickListeners();
        setUpAdapters();

        updateUI();

        return dialogView;
    }

    private void updateUI() {
        bankNameEditText.setText(Utils.def(account.bank, ""));
        acHolderNameEditText.setText(Utils.def(account.accountHolderName, ""));
        acNumberEditText.setText(Utils.def(account.accountNumber, ""));
        ifscEditText.setText(Utils.def(account.ifsc, ""));

        int typeIndex = acTypes.indexOf(account.accountType);
        if (typeIndex != -1) {
            acTypeSpinner.setSelection(typeIndex);
        }
    }

    private void setUpAdapters() {
        spinnerAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        acTypeSpinner.setAdapter(spinnerAdapter);
        acTypeSpinner.setSelection(0);
    }

    private void setClickListeners() {
        doneButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String bankName = bankNameEditText.getText().toString().trim();
                String holderName = acHolderNameEditText.getText().toString().trim();
                String acNumber = acNumberEditText.getText().toString().trim();
                String ifsc = ifscEditText.getText().toString().trim();
                String acType = acTypes.get(acTypeSpinner.getSelectedItemPosition());

                if (holderName.length() == 0) {
                    acHolderNameEditText.setError("This field cannot be left blank");
                    return;
                }
                if (acNumber.length() == 0) {
                    acNumberEditText.setError("This field cannot be left blank");
                    return;
                }

                if (acNumber.length() < 9 || acNumber.length() > 18) {
                    acNumberEditText.setError("Account number lenght should be withing 9 to 18 digit");
                    return;
                }

                if(TextUtils.isEmpty(ifsc)) {
                    ifscEditText.setError("This field cannot be left blank");
                    return;
                } else if(!Utils.isValidIFSC(ifsc)) {
                    ifscEditText.setError("Please enter valid IFSC code!");
                    return;
                } else {
                    ifscEditText.setError(null);
                }

                // make add account request
                makeAccountAddRequest(bankName, holderName, acNumber, acType, ifsc);
            }
        });
        cancelButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dismiss();
            }
        });
    }

    private void makeAccountAddRequest(String bankName, String holderName, String acNumber, String acType, String ifsc) {
        JSONObject jsonObject;
        try {
            /*jsonObject = new BankAccount(account.id, bankName, acType, acNumber, holderName, ifsc).toJson();*/
            jsonObject = new BankAccount(App.getProfile().username, bankName, acType,
                    acNumber, holderName, ifsc).toJsonObject();
        } catch (JSONException e) {
            toast("error forming json");
            e.printStackTrace();
            return;
        }
        AccountAddEditRequest request = new AccountAddEditRequest(jsonObject,
                new AccountAddEditListener());
        queue(request);
    }

    private void setViewVariables() {
        doneButton = dialogView.findViewById(R.id.dialog_add_btn);
        cancelButton = dialogView.findViewById(R.id.dialog_cancel_btn);
        bankNameEditText = dialogView.findViewById(R.id.bank_name_edittext);
        acHolderNameEditText = dialogView.findViewById(R.id.account_holder_name_edittext);
        acNumberEditText = dialogView.findViewById(R.id.account_number_edittext);
        ifscEditText = dialogView.findViewById(R.id.account_ifsc_edittext);
        acTypeSpinner = dialogView.findViewById(R.id.account_type_spinner);
    }

    private class AccountAddEditListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            toast("Account Added");
            if (accountAddListener != null) {
                try {
                    BankAccount account = getAccount(response);
                    accountAddListener.onAccountAdd(account);
                } catch (JSONException e) {
                    toast("error reading response");
                    return;
                }
            }
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
                    toast(errorMsg);
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

    private BankAccount getAccount(JSONObject jsonObject) throws JSONException {
        JSONObject data = jsonObject.getJSONObject("data");
        /*return BankAccount.fromJson(data);*/
        return BankAccount.fromJsonObject(data);
    }


    public interface AccountAddListener {
        void onAccountAdd(BankAccount account);
    }

}