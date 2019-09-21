package in.aaho.android.aahocustomers.drivers;

import android.content.DialogInterface;
import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AlertDialog;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.aahocustomers.R;
import in.aaho.android.aahocustomers.booking.App;
import in.aaho.android.aahocustomers.common.ApiResponseListener;
import in.aaho.android.aahocustomers.common.BaseActivity;
import in.aaho.android.aahocustomers.common.EditTextWatcher;
import in.aaho.android.aahocustomers.common.Utils;
import in.aaho.android.aahocustomers.docs.Document;
import in.aaho.android.aahocustomers.docs.DocumentEditFragment;
import in.aaho.android.aahocustomers.requests.DriverAddEditRequest;
import in.aaho.android.aahocustomers.requests.DriverDetailsRequest;
import in.aaho.android.aahocustomers.vehicles.AccountAddDialogFragment;
import in.aaho.android.aahocustomers.vehicles.BankAccount;

/**
 * Created by mani on 10/10/16.
 */

public class DriverDetailsActivity extends BaseActivity {


    private TextView dlValidityView, panNumberView, dlIdTextView, bankAcTextView;
    private LinearLayout panEditBtn, dlEditBtn, bankAcEditBtn;
    private ImageView panAlert, dlAlert, bankAcAlert;

    private TextView driverNameView;
    private EditText driverNameEditText, driverPhoneEditText;

    private Button saveButton;

    public static int position = -1;
    public static Long driverId;
    public static BrokerDriver driver;

    public static BrokerDriverDetails brokerDriverDetails = new BrokerDriverDetails();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.driver_details_activity);

        setToolbarTitle("Driver Details");

        setViewVariables();
        setClickListeners();
        setupAdapters();

        updateDriver();
        loadDataFromServer();
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        updateDriver();
        loadDataFromServer();
    }

    @Override
    protected void onResume() {
        super.onResume();
        Log.e("Details", "onResume");
        App.setFromSharedPreferencesIfNeeded();
    }

    private void updateDriver() {
        if (position != -1) {
            driver = ListDriversActivity.getDriverList().get(position);
            driverId = driver.getId();
        } else {
            driver = null;
            driverId = null;
            brokerDriverDetails = new BrokerDriverDetails();
        }
    }

    private void setupAdapters() {

    }

    private void setClickListeners() {
        saveButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                sendDriverEditRequest();
            }
        });
        driverNameEditText.addTextChangedListener(new NameTextWatcher());
        driverPhoneEditText.addTextChangedListener(new PhoneTextWatcher());

        panEditBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                launchPanEditDialog(brokerDriverDetails.panDoc);
            }
        });
        dlEditBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                launchDlEditDialog(brokerDriverDetails.dlDoc);
            }
        });
        bankAcEditBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                launchAddEditAccountDialog();
            }
        });
    }

    private void launchPanEditDialog(Document doc) {
        String title = "Driver PAN";
        String idHint = "PAN Number";
        DocumentEditFragment.ResultListener listener = new DocumentEditFragment.ResultListener() {
            @Override
            public void onResult(DocumentEditFragment.Result result) {
                updateDriverPan(result);
            }
        };
        DocumentEditFragment.Builder builder = new DocumentEditFragment.Builder(this, title, listener);
        builder.setHints(idHint, null);
        builder.setValues(doc);
        builder.setEnabled(true, false, false, false, false, false);
        builder.build();
    }

    private void launchDlEditDialog(Document doc) {
        String title = "Driver's Licence";
        String idHint = "Driver Licence Number";
        String validityHint = "Driver Licence Validity";
        DocumentEditFragment.ResultListener listener = new DocumentEditFragment.ResultListener() {
            @Override
            public void onResult(DocumentEditFragment.Result result) {
                updateDriverDl(result);
            }
        };
        DocumentEditFragment.Builder builder = new DocumentEditFragment.Builder(this, title, listener);
        builder.setHints(idHint, validityHint);
        builder.setValues(doc);
        builder.setEnabled(true, true, false, false, true, false);
        builder.build();
    }

    private void updateDriverPan(DocumentEditFragment.Result result) {
        if (result != null && result.isEdited()) {
            brokerDriverDetails.panDoc = result.getDocument();
            updateDriverPanUI();
            enableSave();
        }
    }

    private void updateDriverDl(DocumentEditFragment.Result result) {
        if (result != null && result.isEdited()) {
            brokerDriverDetails.dlDoc = result.getDocument();
            updateDriverDlUI();
            enableSave();
        }
    }


    private void updateDriverPanUI() {
        Document doc = brokerDriverDetails.panDoc;
        panAlert.setVisibility((doc == null || doc.notSet()) ? View.VISIBLE : View.INVISIBLE);
        panNumberView.setText(doc == null || Utils.not(doc.id) ? "-" : doc.id);
    }

    private void updateDriverDlUI() {
        Document doc = brokerDriverDetails.dlDoc;
        dlAlert.setVisibility((doc == null || doc.notSet()) ? View.VISIBLE : View.INVISIBLE);
        dlValidityView.setText(doc == null || doc.validity == null ? "-" : Utils.formatDate(doc.validity));
        dlIdTextView.setText(doc == null || Utils.not(doc.id) ? "-" : doc.id);
    }

    private void updateAccountUI() {
        BankAccount account = brokerDriverDetails.account;
        bankAcAlert.setVisibility((account == null || account.notSet()) ? View.VISIBLE : View.INVISIBLE);
        bankAcTextView.setText(account == null ? "-" : Utils.def(account.title(), "-"));
    }


    private void launchAddEditAccountDialog() {
        AccountAddDialogFragment.showNewDialog(this, brokerDriverDetails.account, new AccountAddDialogFragment.AccountAddListener() {

            @Override
            public void onAccountAdd(BankAccount account) {
                if (account != null) {
                    brokerDriverDetails.account = account;
                    updateAccountUI();
                    enableSave();
                }
            }
        });
    }

    private void updateDriverDetails(BrokerDriverDetails driverDetails) {
        if (driverDetails == null || driverDetails.id == null) {
            return;
        }
        int index = -1;
        for (int i = 0; i < ListDriversActivity.getDriverList().size(); i++) {
            BrokerDriver brokerDriver = ListDriversActivity.getDriverList().get(i);
            if (brokerDriver.getId() == driverDetails.id) {
                index = i;
                break;
            }
        }

        if (index == -1) {
            ListDriversActivity.getDriverList().add(
                    new BrokerDriver(driverDetails.id, driverDetails.name, driverDetails.phone)
            );
            index = ListDriversActivity.getDriverList().size() - 1;
        }
        position = index;
        driver = ListDriversActivity.getDriverList().get(index);
        brokerDriverDetails = driverDetails;
        driverId = driverDetails.id;
        updateUI();
    }

    private void sendDriverEditRequest() {
        BrokerDriverDetails details = brokerDriverDetails;
        if (details == null) {
            return;
        }
        JSONObject jsonObject = null;
        try {
            jsonObject = details.toJson();
        } catch (JSONException e) {
            e.printStackTrace();
            return;
        }
        if (jsonObject != null && jsonObject.length() != 0) {
            DriverAddEditRequest request = new DriverAddEditRequest(jsonObject, new DriverDetailsEditListener());
            queue(request);
        }
    }

    private class DriverDetailsEditListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            hideSave();
            try {
                BrokerDriverDetails driver = getDriverDetails(response);
                updateDriverDetails(driver);
                toast("Details Saved");
            } catch (JSONException e) {
                toast("error reading response");
                return;
            }
        }

        @Override
        public void onError() {
            dismissProgress();
        }
    }


    private BrokerDriverDetails getDriverDetails(JSONObject jsonObject) throws JSONException {
        JSONObject data = jsonObject.getJSONObject("data");
        return BrokerDriverDetails.fromJson(data);
    }

    private void hideSave() {
        if (saveButton != null && saveButton.getVisibility() != View.GONE) {
            saveButton.setVisibility(View.GONE);
        }
    }

    private void enableSave() {
        if (saveButton != null && saveButton.getVisibility() != View.VISIBLE) {
            saveButton.setVisibility(View.VISIBLE);
        }
    }

    private void setViewVariables() {
        driverNameView = findViewById(R.id.driver_details_name_tv);
        driverNameEditText = findViewById(R.id.driver_details_name_edit_text);
        driverPhoneEditText = findViewById(R.id.driver_details_phone_edit_text);

        saveButton = findViewById(R.id.driver_details_save_btn);

        dlValidityView = findViewById(R.id.driver_details_dl_validity_tv);
        panNumberView = findViewById(R.id.driver_details_pan_number_tv);

        panEditBtn = findViewById(R.id.driver_details_pan_edit_btn);
        dlEditBtn = findViewById(R.id.driver_details_dl_edit_btn);
        bankAcEditBtn = findViewById(R.id.driver_details_bank_ac_edit_btn);

        panAlert = findViewById(R.id.driver_details_pan_alert);
        dlAlert = findViewById(R.id.driver_details_dl_alert);
        bankAcAlert = findViewById(R.id.driver_bank_ac_alert);

        bankAcTextView = findViewById(R.id.driver_bank_ac_text_tv);

        dlIdTextView = findViewById(R.id.driver_details_dl_id_tv);

    }

    private void loadDataFromServer() {
        if (driverId == null) {
            return;
        }
        DriverDetailsRequest appDataRequest = new DriverDetailsRequest(driverId, new DriverDetailsResponseListener());
        queue(appDataRequest);
    }

    private void updateUI() {
        driverNameView.setText(Utils.def(brokerDriverDetails.name, "Unnamed driver"));
        driverNameEditText.setText(Utils.def(brokerDriverDetails.name, ""));
        driverPhoneEditText.setText(Utils.def(brokerDriverDetails.phone, ""));
        updateDriverPanUI();
        updateDriverDlUI();
        updateAccountUI();
    }

    private class DriverDetailsResponseListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            String resp = response.toString();
            try {
                JSONObject jsonObject = new JSONObject(resp);
                JSONObject driverData = jsonObject.getJSONObject("data");
                brokerDriverDetails = BrokerDriverDetails.fromJson(driverData);
                updateUI();
                hideSave();
            } catch (JSONException e) {
                e.printStackTrace();
                toast("error reading response data:\n" + resp);
            }
        }

        @Override
        public void onError() {
            dismissProgress();
        }
    }

    private class NameTextWatcher extends EditTextWatcher {

        @Override
        public void onTextChanged(CharSequence s, int start, int before, int count) {
            String text = s.toString();
            if (!Utils.equals(text, brokerDriverDetails.name)) {
                brokerDriverDetails.name = text;
                enableSave();
            }
        }
    }

    private class PhoneTextWatcher extends EditTextWatcher {

        @Override
        public void onTextChanged(CharSequence s, int start, int before, int count) {
            String text = s.toString();
            if (!Utils.equals(text, brokerDriverDetails.phone)) {
                brokerDriverDetails.phone = text;
                enableSave();
            }
        }
    }

    @Override
    public void onBackPressed() {
        Log.e("Details", "onBackPressed");
        if (saveButton != null && saveButton.getVisibility() == View.VISIBLE) {
            showUnsavedProgressAlert();
            return;
        }
        super.onBackPressed();
    }

    private void showUnsavedProgressAlert() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);

        builder.setTitle("Discard unsaved progress?");
        builder.setMessage("All the driver details you have edited so far will be discarded");
        builder.setPositiveButton("Stay", new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int id) {

            }
        });
        builder.setNegativeButton("Discard", new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int id) {
                DriverDetailsActivity.super.onBackPressed();
            }
        });
        builder.show();
    }
}
