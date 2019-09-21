package in.aaho.android.aahocustomers.vehicles;

import android.content.DialogInterface;
import android.os.Bundle;
import android.support.v7.app.AlertDialog;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.List;

import in.aaho.android.aahocustomers.R;
import in.aaho.android.aahocustomers.booking.App;
import in.aaho.android.aahocustomers.common.ApiResponseListener;
import in.aaho.android.aahocustomers.common.BaseActivity;
import in.aaho.android.aahocustomers.common.S3Util;
import in.aaho.android.aahocustomers.common.Utils;
import in.aaho.android.aahocustomers.docs.Document;
import in.aaho.android.aahocustomers.docs.DocumentEditFragment;
import in.aaho.android.aahocustomers.requests.VehicleAddEditRequest;

/**
 * Created by shobhit on 10/10/16.
 */

public class VehicleDocumentsActivity extends BaseActivity {

    private TextView vehicleNumberView, dlValidityView, ownerDecValidityView, ownerPanNumberView;
    private TextView rcValidityView, permitValidityView, insuranceValidityView, fitnessValidityView, pucValidityView;
    private LinearLayout rcEditBtn, permitEditBtn, insuranceEditBtn, fitnessEditBtn, pucEditBtn;
    private LinearLayout ownerPanEditBtn, ownerDecEditBtn, dlEditBtn, bankAcEditBtn, emailBtn;

    private TextView dlIdTextView, bankAcTextView;
    private TextView permitIdTextView, insuranceIdTextView, fitnessIdTextView, pucIdTextView;
    private ImageView rcAlert, permitAlert, insuranceAlert, fitnessAlert, pucAlert;
    private ImageView ownerPanAlert, ownerDecAlert, dlAlert, bankAcAlert;

    private Button saveButton;

    public static int position;
    public static long vehicleId;
    public static BrokerVehicle vehicle;

    public static BrokerVehicleDetails brokerVehicleDetails;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.vehicle_documents_activity);
        setToolbarTitle("Vehicle Documents");

        setViewVariables();
        setClickListeners();
        setupAdapters();
    }

    @Override
    protected void onResume() {
        super.onResume();
        Log.e("Docs", "onResume");
        App.setFromSharedPreferencesIfNeeded();
        updateVehicle();
        updateUI();
    }

    private void updateVehicle() {
        position = VehicleDetailsActivity.position;
        vehicle = VehicleDetailsActivity.vehicle;
        vehicleId = VehicleDetailsActivity.vehicleId;
        brokerVehicleDetails = VehicleDetailsActivity.brokerVehicleDetails;
    }

    private void setupAdapters() {

    }

    private void setClickListeners() {
        rcEditBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                launchRcEditDialog(brokerVehicleDetails.rcDoc);
            }
        });
        insuranceEditBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                launchInsuranceEditDialog(brokerVehicleDetails.insuranceDoc);
            }
        });
        permitEditBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                launchPermitEditDialog(brokerVehicleDetails.permitDoc);
            }
        });
        fitnessEditBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                launchFitnessEditDialog(brokerVehicleDetails.fitnessDoc);
            }
        });
        pucEditBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                launchPucEditDialog(brokerVehicleDetails.pucDoc);
            }
        });
        ownerDecEditBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                launchOwnerDecEditDialog(brokerVehicleDetails.ownerDecDoc);
            }
        });
        ownerPanEditBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                launchOwnerPanEditDialog(brokerVehicleDetails.ownerPanDoc);
            }
        });
        dlEditBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                launchDlEditDialog(brokerVehicleDetails.driverDlDoc);
            }
        });
        bankAcEditBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                launchBankAcEditDialog();
            }
        });
        saveButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                sendDocumentEditRequest();
            }
        });
        emailBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showSendEmailDialog();
            }
        });
    }

    private void showSendEmailDialog() {
        if (saveButton.getVisibility() == View.VISIBLE) {
            toast("Please save before sending the documents");
            return;
        }
        if (brokerVehicleDetails == null || brokerVehicleDetails.id == null) {
            toast("Vehicle Details not set");
            return;
        }
        if (!brokerVehicleDetails.hasDocuments()) {
            toast("No documents present to send");
            return;
        }
        List<DocDetail> docList = brokerVehicleDetails.getDocDetailsList();
        if (Utils.not(docList)) {
            toast("This should not happen, debugging needed");
            return;
        }
        DocEmailDialogFragment.showNewDialog(this, brokerVehicleDetails.id, docList);
    }


    private void sendDocumentEditRequest() {
        BrokerVehicleDetails details = brokerVehicleDetails;
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
            VehicleAddEditRequest request = new VehicleAddEditRequest(jsonObject, new VehicleEditListener());
            queue(request);
        }
    }


    private class VehicleEditListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            hideSave();
            toast("Documents Saved");
        }

        @Override
        public void onError() {
            dismissProgress();
        }
    }

    private void hideSave() {
        if (saveButton != null) {
            saveButton.setVisibility(View.GONE);
        }
    }

    private void launchRcEditDialog(Document doc) {
        String title = "Registration Certificate";
        String validityHint = "Registration Validity";
        DocumentEditFragment.ResultListener listener = new DocumentEditFragment.ResultListener() {
            @Override
            public void onResult(DocumentEditFragment.Result result) {
                updateRc(result);
            }
        };

        DocumentEditFragment.Builder builder = new DocumentEditFragment.Builder(this, title, listener);
        builder.setHints(null, validityHint);
        builder.setValues(doc);
        builder.setEnabled(false, true, true, false, false, false);
        builder.setUploadId(S3Util.S3_UPLOAD_ID_FOR_VEHICLE_RC_DIR);
        builder.build();
    }

    private void launchInsuranceEditDialog(Document doc) {
        String title = "Insurance";
        String idHint = "Insurance Number";
        String validityHint = "Insurance Validity";
        DocumentEditFragment.ResultListener listener = new DocumentEditFragment.ResultListener() {
            @Override
            public void onResult(DocumentEditFragment.Result result) {
                updateInsurance(result);
            }
        };
        DocumentEditFragment.Builder builder = new DocumentEditFragment.Builder(this, title, listener);
        builder.setHints(idHint, validityHint);
        builder.setValues(doc);
        builder.setEnabled(true, true, false, true, false, false);
        builder.setUploadId(S3Util.S3_UPLOAD_ID_FOR_VEHICLE_INSURANCE_DIR);
        builder.build();
    }

    private void launchPermitEditDialog(Document doc) {
        String title = "Permit";
        String idHint = "Permit Number";
        String validityHint = "Permit Validity";
        DocumentEditFragment.ResultListener listener = new DocumentEditFragment.ResultListener() {
            @Override
            public void onResult(DocumentEditFragment.Result result) {
                updatePermit(result);
            }
        };
        DocumentEditFragment.Builder builder = new DocumentEditFragment.Builder(this, title, listener);
        builder.setHints(idHint, validityHint);
        builder.setValues(doc);
        builder.setEnabled(true, true, false, false, false, true);
        builder.setUploadId(S3Util.S3_UPLOAD_ID_FOR_VEHICLE_PERMIT_DIR);
        builder.build();
    }

    private void launchFitnessEditDialog(Document doc) {
        String title = "Fitness Certificate";
        String idHint = "Fitness Certificate Number";
        String validityHint = "Fitness Certificate Validity";
        DocumentEditFragment.ResultListener listener = new DocumentEditFragment.ResultListener() {
            @Override
            public void onResult(DocumentEditFragment.Result result) {
                updateFitness(result);
            }
        };
        DocumentEditFragment.Builder builder = new DocumentEditFragment.Builder(this, title, listener);
        builder.setHints(idHint, validityHint);
        builder.setValues(doc);
        builder.setEnabled(true, true, false, false, false, false);
        builder.setUploadId(S3Util.S3_UPLOAD_ID_FOR_VEHICLE_FITNESS_DIR);
        builder.build();
    }

    private void launchPucEditDialog(Document doc) {
        String title = "PUC Certificate";
        String idHint = "PUC Certificate Number";
        String validityHint = "PUC Certificate Validity";
        DocumentEditFragment.ResultListener listener = new DocumentEditFragment.ResultListener() {
            @Override
            public void onResult(DocumentEditFragment.Result result) {
                updatePuc(result);
            }
        };
        DocumentEditFragment.Builder builder = new DocumentEditFragment.Builder(this, title, listener);
        builder.setHints(idHint, validityHint);
        builder.setValues(doc);
        builder.setEnabled(true, true, false, false, false, false);
        builder.setUploadId(S3Util.S3_UPLOAD_ID_FOR_VEHICLE_PUC_DIR);
        builder.build();
    }

    private void launchOwnerDecEditDialog(Document doc) {
        String title = "Owner Declaration";
        String validityHint = "Declaration Validity";
        DocumentEditFragment.ResultListener listener = new DocumentEditFragment.ResultListener() {
            @Override
            public void onResult(DocumentEditFragment.Result result) {
                updateOwnerDec(result);
            }
        };
        DocumentEditFragment.Builder builder = new DocumentEditFragment.Builder(this, title, listener);
        builder.setHints(null, validityHint);
        builder.setValues(doc);
        builder.setEnabled(false, true, false, false, false, false);
        builder.setUploadId(S3Util.S3_UPLOAD_ID_FOR_SUPPLIER_DECLARATION_DIR);
        builder.build();
    }

    private void launchOwnerPanEditDialog(Document doc) {
        String title = "Owner PAN";
        String idHint = "PAN Number";
        DocumentEditFragment.ResultListener listener = new DocumentEditFragment.ResultListener() {
            @Override
            public void onResult(DocumentEditFragment.Result result) {
                updateOwnerPan(result);
            }
        };
        DocumentEditFragment.Builder builder = new DocumentEditFragment.Builder(this, title, listener);
        builder.setHints(idHint, null);
        builder.setValues(doc);
        builder.setEnabled(true, false, false, false, false, false);
        builder.setUploadId(S3Util.S3_UPLOAD_ID_FOR_SUPPLIER_PAN_DIR);
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
        builder.setUploadId(S3Util.S3_UPLOAD_ID_FOR_DRIVER_LICENCE_DIR);
        builder.build();
    }

    private void launchBankAcEditDialog() {

        AccountSelectDialogFragment.showNewDialog(this, new AccountSelectDialogFragment.AccountChangeListener() {
            @Override
            public void onChange(BankAccount account) {
                if (brokerVehicleDetails != null) {
                    if (brokerVehicleDetails.account == null && account == null) {
                        return;
                    }
                    if (brokerVehicleDetails.account != null && account != null && Utils.equals(account.id, brokerVehicleDetails.account.id)) {
                        return;
                    }
                    brokerVehicleDetails.account = account;
                    updateAccountUI();
                    enableSave();
                }
            }
        });
    }

    private void updateRc(DocumentEditFragment.Result result) {
        if (result != null && result.isEdited()) {
            brokerVehicleDetails.rcDoc = result.getDocument();
            updateRcUI();
            enableSave();
        }
    }

    private void updateInsurance(DocumentEditFragment.Result result) {
        if (result != null && result.isEdited()) {
            brokerVehicleDetails.insuranceDoc = result.getDocument();
            updateInsuranceUI();
            enableSave();
        }
    }

    private void updatePermit(DocumentEditFragment.Result result) {
        if (result != null && result.isEdited()) {
            brokerVehicleDetails.permitDoc = result.getDocument();
            updatePermitUI();
            enableSave();
        }
    }

    private void updateFitness(DocumentEditFragment.Result result) {
        if (result != null && result.isEdited()) {
            brokerVehicleDetails.fitnessDoc = result.getDocument();
            updateFitnessUI();
            enableSave();
        }
    }

    private void updatePuc(DocumentEditFragment.Result result) {
        if (result != null && result.isEdited()) {
            brokerVehicleDetails.pucDoc = result.getDocument();
            updatePucUI();
            enableSave();
        }
    }

    private void updateOwnerDec(DocumentEditFragment.Result result) {
        if (result != null && result.isEdited()) {
            brokerVehicleDetails.ownerDecDoc = result.getDocument();
            updateOwnerDecUI();
            enableSave();
        }
    }

    private void updateOwnerPan(DocumentEditFragment.Result result) {
        if (result != null && result.isEdited()) {
            brokerVehicleDetails.ownerPanDoc = result.getDocument();
            updateOwnerPanUI();
            enableSave();
        }
    }

    private void updateDriverDl(DocumentEditFragment.Result result) {
        if (result != null && result.isEdited()) {
            brokerVehicleDetails.driverDlDoc = result.getDocument();
            updateDriverDlUI();
            enableSave();
        }
    }

    private void enableSave() {
        if (saveButton != null) {
            saveButton.setVisibility(View.VISIBLE);
        }
    }

    private void setViewVariables() {
        vehicleNumberView = findViewById(R.id.vehicle_documents_number_tv);
        rcValidityView = findViewById(R.id.vehicle_rc_validity_tv);
        permitValidityView = findViewById(R.id.vehicle_permit_validity_tv);
        fitnessValidityView = findViewById(R.id.vehicle_fitness_validity_tv);
        insuranceValidityView = findViewById(R.id.vehicle_insurance_validity_tv);
        pucValidityView = findViewById(R.id.vehicle_puc_validity_tv);
        dlValidityView = findViewById(R.id.vehicle_driver_dl_validity_tv);
        ownerDecValidityView = findViewById(R.id.vehicle_owner_dec_validity_tv);
        ownerPanNumberView = findViewById(R.id.vehicle_owner_pan_number_tv);

        rcEditBtn = findViewById(R.id.vehicle_rc_edit_btn);
        permitEditBtn = findViewById(R.id.vehicle_permit_edit_btn);
        fitnessEditBtn = findViewById(R.id.vehicle_fitness_edit_btn);
        insuranceEditBtn = findViewById(R.id.vehicle_insurance_edit_btn);
        pucEditBtn = findViewById(R.id.vehicle_puc_edit_btn);
        ownerPanEditBtn = findViewById(R.id.vehicle_owner_pan_edit_btn);
        ownerDecEditBtn = findViewById(R.id.vehicle_owner_dec_edit_btn);
        dlEditBtn = findViewById(R.id.vehicle_driver_dl_edit_btn);
        bankAcEditBtn = findViewById(R.id.vehicle_bank_ac_edit_btn);
        emailBtn = findViewById(R.id.documents_email_btn);

        saveButton = findViewById(R.id.vehicle_docs_save_btn);

        rcAlert = findViewById(R.id.vehicle_rc_alert);
        insuranceAlert = findViewById(R.id.vehicle_insurance_alert);
        permitAlert = findViewById(R.id.vehicle_permit_alert);
        fitnessAlert = findViewById(R.id.vehicle_fitness_alert);
        pucAlert = findViewById(R.id.vehicle_puc_alert);
        ownerPanAlert = findViewById(R.id.vehicle_owner_pan_alert);
        ownerDecAlert = findViewById(R.id.vehicle_owner_dec_alert);
        dlAlert = findViewById(R.id.vehicle_driver_dl_alert);
        bankAcAlert = findViewById(R.id.vehicle_bank_ac_alert);

        dlIdTextView = findViewById(R.id.vehicle_dl_id_tv);
        permitIdTextView = findViewById(R.id.vehicle_permit_id_tv);
        insuranceIdTextView = findViewById(R.id.vehicle_insurance_id_tv);
        fitnessIdTextView = findViewById(R.id.vehicle_fitness_id_tv);
        pucIdTextView = findViewById(R.id.vehicle_puc_id_tv);
        bankAcTextView = findViewById(R.id.vehicle_bank_ac_text_tv);
    }

    private void updateAccountUI() {
        BankAccount account = brokerVehicleDetails.account;
        bankAcAlert.setVisibility((account == null || account.notSet()) ? View.VISIBLE : View.INVISIBLE);
        bankAcTextView.setText(account == null ? "-" : Utils.def(account.title(), "-"));
    }

    private void updateRcUI() {
        Document doc = brokerVehicleDetails.rcDoc;
        rcAlert.setVisibility((doc == null || doc.notSet()) ? View.VISIBLE : View.INVISIBLE);
        rcValidityView.setText(doc == null || doc.validity == null ? "-" : Utils.formatDate(doc.validity));
    }

    private void updateInsuranceUI() {
        Document doc = brokerVehicleDetails.insuranceDoc;
        insuranceAlert.setVisibility((doc == null || doc.notSet()) ? View.VISIBLE : View.INVISIBLE);
        insuranceValidityView.setText(doc == null || doc.validity == null ? "-" : Utils.formatDate(doc.validity));
        insuranceIdTextView.setText(doc == null || Utils.not(doc.id) ? "-" : doc.id);
    }

    private void updatePermitUI() {
        Document doc = brokerVehicleDetails.permitDoc;
        permitAlert.setVisibility((doc == null || doc.notSet()) ? View.VISIBLE : View.INVISIBLE);
        permitValidityView.setText(doc == null || doc.validity == null ? "-" : Utils.formatDate(doc.validity));
        permitIdTextView.setText(doc == null || Utils.not(doc.id) ? "-" : doc.id);
    }

    private void updateFitnessUI() {
        Document doc = brokerVehicleDetails.fitnessDoc;
        fitnessAlert.setVisibility((doc == null || doc.notSet()) ? View.VISIBLE : View.INVISIBLE);
        fitnessValidityView.setText(doc == null || doc.validity == null ? "-" : Utils.formatDate(doc.validity));
        fitnessIdTextView.setText(doc == null || Utils.not(doc.id) ? "-" : doc.id);

    }

    private void updatePucUI() {
        Document doc = brokerVehicleDetails.pucDoc;
        pucAlert.setVisibility((doc == null || doc.notSet()) ? View.VISIBLE : View.INVISIBLE);
        pucValidityView.setText(doc == null || doc.validity == null ? "-" : Utils.formatDate(doc.validity));
        pucIdTextView.setText(doc == null || Utils.not(doc.id) ? "-" : doc.id);

    }

    private void updateOwnerPanUI() {
        Document doc = brokerVehicleDetails.ownerPanDoc;
        ownerPanAlert.setVisibility((doc == null || doc.notSet()) ? View.VISIBLE : View.INVISIBLE);
        ownerPanNumberView.setText(doc == null || Utils.not(doc.id) ? "-" : doc.id);
    }

    private void updateOwnerDecUI() {
        Document doc = brokerVehicleDetails.ownerDecDoc;
        ownerDecAlert.setVisibility((doc == null || doc.notSet()) ? View.VISIBLE : View.INVISIBLE);
        ownerDecValidityView.setText(doc == null || doc.validity == null ? "-" : Utils.formatDate(doc.validity));
    }

    private void updateDriverDlUI() {
        Document doc = brokerVehicleDetails.driverDlDoc;
        dlAlert.setVisibility((doc == null || doc.notSet()) ? View.VISIBLE : View.INVISIBLE);
        dlValidityView.setText(doc == null || doc.validity == null ? "-" : Utils.formatDate(doc.validity));
        dlIdTextView.setText(doc == null || Utils.not(doc.id) ? "-" : doc.id);
    }

    private void updateUI() {
        vehicleNumberView.setText(brokerVehicleDetails.getNumber() == null ? "" : brokerVehicleDetails.getNumber());
        updateRcUI();
        updateInsuranceUI();
        updatePermitUI();
        updateFitnessUI();
        updatePucUI();
        updateOwnerPanUI();
        updateOwnerDecUI();
        updateDriverDlUI();
        updateAccountUI();
    }

    @Override
    public void onBackPressed() {
        if (saveButton != null && saveButton.getVisibility() == View.VISIBLE) {
            showUnsavedProgressAlert();
            return;
        }
        super.onBackPressed();
    }

    private void showUnsavedProgressAlert() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);

        builder.setTitle("Discard unsaved progress?");
        builder.setMessage("All the documents you have edited so far will be discarded");
        builder.setPositiveButton("Stay", new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int id) {

            }
        });
        builder.setNegativeButton("Discard", new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int id) {
                VehicleDocumentsActivity.super.onBackPressed();
            }
        });
        builder.show();
    }
}
