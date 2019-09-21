package in.aaho.android.ownr.profile;

import android.content.DialogInterface;
import android.os.Bundle;
import android.os.Handler;
import android.support.v7.app.AlertDialog;
import android.support.v7.widget.DefaultItemAnimator;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.text.TextUtils;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.AutoCompleteTextView;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import com.android.volley.VolleyError;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.UnsupportedEncodingException;

import in.aaho.android.ownr.AppDataActivity;
import in.aaho.android.ownr.LoadingActivity;
import in.aaho.android.ownr.R;
import in.aaho.android.ownr.adapter.CitySuggestionAdapter;
import in.aaho.android.ownr.booking.App;
import in.aaho.android.ownr.common.ApiResponseListener;
import in.aaho.android.ownr.common.BaseActivity;
import in.aaho.android.ownr.common.EditTextWatcher;
import in.aaho.android.ownr.common.S3Util;
import in.aaho.android.ownr.common.Utils;
import in.aaho.android.ownr.docs.Document;
import in.aaho.android.ownr.docs.DocumentEditFragment;
import in.aaho.android.ownr.parser.CityParser;
import in.aaho.android.ownr.requests.ProfileEditRequest;
import in.aaho.android.ownr.vehicles.AccountAddDialogFragment;
import in.aaho.android.ownr.vehicles.BankAccount;

import static in.aaho.android.ownr.profile.Profile.CITY_ID_KEY;
import static in.aaho.android.ownr.profile.Profile.CITY_KEY;
import static in.aaho.android.ownr.profile.Profile.CITY_NAME_KEY;


public class ProfileActivity extends AppDataActivity {
    private final String TAG = getClass().getSimpleName();
    private AutoCompleteTextView city_autoComplete;
    private TextView decValidityView, panNumberView;
    private LinearLayout ownerPanEditBtn, ownerDecEditBtn, linear_city_section;
    private ImageView panAlert, decAlert;

    private EditText usernameEditText, passwordEditText;
    private EditText nameEditText, addressEditText;
    private EditText contactNameEditText, contactPhoneEditText;
    private EditText contactEmailEditText, contactDesignationEditText;

    private Button saveButton, acAddBtn;
    private RecyclerView acContainer;
    private TextView emptyView;
    private String mCityId;
    /** To knwo if city is selected from suggestion or not */
    private boolean mIsCitySelectedFromSuggestion = false;

    private AccountProfileAdapter accountAdapter;

    private LoadingActivity.IOnInitialDataListener mIOnInitialDataListener;
    private boolean mbIsFirstTime = true;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.profile_activity);

        setToolbarTitle("Profile");

        setViewVariables();
        setClickListeners();
        setupAdapters();
        updateUI();

        mIOnInitialDataListener = new LoadingActivity.IOnInitialDataListener() {
            @Override
            public void onInitialDataReceived(int statusCode) {
                // On initial Data load finished
                if(statusCode == 200) {
                    resetProfilePage();
                    if(mbIsFirstTime) {
                        // don't show toast on first load
                        mbIsFirstTime = false;
                    } else {
                        toast("Profile Updated");
                    }
                } else {
                    toast("Failed to update profile!");
                }
            }
        };

        loadProfileDataFromServer();
    }

    /** To fetch the profile data from server each time when activity loads */
    private void loadProfileDataFromServer() {
        final Handler handler = new Handler();
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                fetchCategoryId(false,mIOnInitialDataListener);
            }
        }, 100);
    }

    private void updateUI() {
        setFromData();
        updateDecUI();
        updatePanUI();
        updateAcUI();
    }

    private void setupAdapters() {
        setupAcAdapter();
    }

    private void setupAcAdapter() {
        accountAdapter = new AccountProfileAdapter(new AccountProfileAdapter.AccountSelectListener() {
            @Override
            public void onSelect(BankAccount account) {
                launchAddAccountDialog(account);
            }
        });
        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getApplicationContext());
        acContainer.setLayoutManager(mLayoutManager);
        acContainer.setItemAnimator(new DefaultItemAnimator());
        acContainer.setAdapter(accountAdapter);
        acContainer.setNestedScrollingEnabled(false);

    }


    private void setViewVariables() {
        linear_city_section = findViewById(R.id.linear_city_section);
        city_autoComplete = findViewById(R.id.city_autoComplete);
        //TOOD: uncomment below line when city is ready from backend
        linear_city_section.setVisibility(View.VISIBLE);

        usernameEditText = (EditText) findViewById(R.id.profile_username_edittext);
        passwordEditText = (EditText) findViewById(R.id.profile_password_edittext);


        nameEditText = findViewById(R.id.profile_name_edittext);
        addressEditText = findViewById(R.id.profile_address_edittext);

        contactNameEditText = findViewById(R.id.profile_contact_name_edittext);
        contactPhoneEditText = findViewById(R.id.profile_contact_phone_edittext);
        contactEmailEditText = findViewById(R.id.profile_contact_email_edittext);
        contactDesignationEditText = findViewById(R.id.profile_designation_edittext);

        saveButton = findViewById(R.id.save_profile_btn);

        decValidityView = findViewById(R.id.dec_validity_tv);
        panNumberView = findViewById(R.id.pan_number_tv);

        ownerPanEditBtn = findViewById(R.id.pan_edit_btn);
        ownerDecEditBtn = findViewById(R.id.dec_edit_btn);

        panAlert = findViewById(R.id.pan_alert);
        decAlert = findViewById(R.id.dec_alert);

        acAddBtn = findViewById(R.id.account_add_btn);
        acContainer = findViewById(R.id.account_list_container);
        emptyView = findViewById(R.id.empty_view);

    }

    private JSONObject getUpdatedProfileData() {
        String name = nameEditText.getText().toString().trim();
        String contactName = contactNameEditText.getText().toString().trim();
        String contactPhone = contactPhoneEditText.getText().toString().trim();
        String contactEmail = contactEmailEditText.getText().toString().trim();
        String contactDesignation = contactDesignationEditText.getText().toString().trim();
        String address = addressEditText.getText().toString().trim();
        String cityId = mCityId;

        try {
            JSONObject data = App.getProfile().getUpdatedUserProfileJson(name, contactName, contactPhone,
                    contactEmail, contactDesignation,address,cityId);
            return data.length() == 0 ? null : data;
        } catch (JSONException e) {
            return null;
        }
    }

    private void makeProfileEditRequest() {
        JSONObject data = getUpdatedProfileData();
        if (data == null) {
            toast("Already Updated");
            return;
        }
        ProfileEditRequest profileRequest = new ProfileEditRequest(data, new ProfileEditListener());
        queue(profileRequest);
    }

    private class ProfileEditListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();

            try {
                /*App.setUserData(response.getJSONObject("user"));*/
                if(response != null && response.getString("status")
                        .equalsIgnoreCase("success")) {
                    /*App.getProfile().username = Utils.get(response,"username");
                    App.getProfile().userFullName = Utils.get(response,"full_name");
                    if (response.has("address") && !response.isNull("address")) {
                        JSONObject addressObj = response.getJSONObject("address");
                        App.getProfile().address.updateAddress(addressObj);
                    }

                    if(response.has(CITY_KEY)) {
                        JSONObject city = response.getJSONObject(CITY_KEY);
                        App.getProfile().mCityId = city.optString(CITY_ID_KEY);
                        App.getProfile().mCityName = city.optString(CITY_NAME_KEY);
                    }

                    App.getProfile().userFullName = Utils.get(response,"username");
                    App.getProfile().userFullName = Utils.get(response,"username");*/
                    /*fetchUserData(false,mIOnInitialDataListener);*/
                    fetchCategoryId(false,mIOnInitialDataListener);
                } else {
                    toast("Failed to update profile!");
                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }

        /*@Override
        public void onError() {
            dismissProgress();
        }*/

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

    }

    private void resetProfilePage() {
        updateUI();
        hideSave();
    }

    private void hideSave() {
        if (saveButton != null) {
            saveButton.setVisibility(View.GONE);
        }
    }

    private void setClickListeners() {
        nameEditText.setOnFocusChangeListener(new EditTextClickListener());
        contactNameEditText.setOnFocusChangeListener(new EditTextClickListener());
        contactPhoneEditText.setOnFocusChangeListener(new EditTextClickListener());
        contactEmailEditText.setOnFocusChangeListener(new EditTextClickListener());
        contactDesignationEditText.setOnFocusChangeListener(new EditTextClickListener());
        passwordEditText.setOnClickListener(new PasswordClickListener());
        /** NOTE: We are not calling any api on editText so keep it as editable only */
        //addressEditText.setOnClickListener(new AddressClickListener());
        addressEditText.setOnFocusChangeListener(new EditTextClickListener());
        saveButton.setOnClickListener(new ProfileClickListener());

        ownerDecEditBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                launchDecEditDialog(App.getProfile().decDoc);
            }
        });
        ownerPanEditBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                launchPanEditDialog(App.getProfile().panDoc);
            }
        });
        acAddBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                launchAddAccountDialog(null);
            }
        });

        city_autoComplete.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int start, int before, int count) {
                if(count == 0) {
                    mIsCitySelectedFromSuggestion = false;
                    disableSave();
                }
            }
        });

        city_autoComplete.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            public void onItemClick(AdapterView<?> parent, View view, int position, long rowId) {
                CityParser selection = (CityParser) parent.getItemAtPosition(position);
                city_autoComplete.setText(selection.getText().toString());
                mCityId = selection.getId().toString();
                mIsCitySelectedFromSuggestion = true;
                enableSave();
            }
        });

        city_autoComplete.setAdapter(new CitySuggestionAdapter(ProfileActivity.this,
                city_autoComplete.getText().toString()));
    }

    private void launchAddAccountDialog(BankAccount oldAccount) {
        AccountAddDialogFragment.showNewDialog(this, oldAccount, new AccountAddDialogFragment.AccountAddListener() {

            @Override
            public void onAccountAdd(BankAccount account) {
                if (account != null) {
                    BankAccount.add(account);
                    updateAcUI();
                }
            }
        });
    }

    private void updateAcUI() {
        boolean empty = BankAccount.accountList.isEmpty();
        emptyView.setVisibility(empty ? View.VISIBLE : View.GONE);
        acContainer.setVisibility(empty ? View.GONE : View.VISIBLE);
        accountAdapter.notifyDataSetChanged();
    }

    private void launchDecEditDialog(Document doc) {
        String title = "Owner Declaration";
        String validityHint = "Declaration Validity";
        DocumentEditFragment.ResultListener listener = new DocumentEditFragment.ResultListener() {
            @Override
            public void onResult(DocumentEditFragment.Result result) {
                updateDec(result);
            }
        };
        DocumentEditFragment.Builder builder = new DocumentEditFragment.Builder(this, title, listener);
        builder.setHints(null, validityHint);
        builder.setValues(doc);
        builder.setEnabled(false, true, false, false, false, false);
        builder.setUploadId(S3Util.S3_UPLOAD_ID_FOR_PROFILE_SUPPLIER_DECLARATION_DIR);
        builder.build();
    }

    private void launchPanEditDialog(Document doc) {
        String title = "Owner PAN";
        String idHint = "PAN Number";
        DocumentEditFragment.ResultListener listener = new DocumentEditFragment.ResultListener() {
            @Override
            public void onResult(DocumentEditFragment.Result result) {
                updatePan(result);
            }
        };
        DocumentEditFragment.Builder builder = new DocumentEditFragment.Builder(this, title, listener);
        builder.setHints(idHint, null);
        builder.setValues(doc);
        builder.setEnabled(true, false, false, false, false, false);
        builder.setUploadId(S3Util.S3_UPLOAD_ID_FOR_PROFILE_SUPPLIER_PAN_DIR);
        builder.build();
    }


    private void updateDec(DocumentEditFragment.Result result) {
        if (result != null && result.isEdited()) {
            App.getProfile().decDoc = result.getDocument();
            updateDecUI();
            enableSave();
        }
    }

    private void updatePan(DocumentEditFragment.Result result) {
        if (result != null && result.isEdited()) {
            App.getProfile().panDoc = result.getDocument();
            updatePanUI();
            enableSave();
        }
    }

    private void updatePanUI() {
        Document doc = App.getProfile().panDoc;
        panAlert.setVisibility((doc == null || doc.notSet()) ? View.VISIBLE : View.INVISIBLE);
        panNumberView.setText(doc == null || Utils.not(doc.id) ? "-" : doc.id);
    }

    private void updateDecUI() {
        Document doc = App.getProfile().decDoc;
        decAlert.setVisibility((doc == null || doc.notSet()) ? View.VISIBLE : View.INVISIBLE);
        decValidityView.setText(doc == null || doc.validity == null ? "-" : Utils.formatDate(doc.validity));
    }

    private void enableSave() {
        if (saveButton != null) {
            saveButton.setVisibility(View.VISIBLE);
        }
    }

    private void disableSave() {
        if (saveButton != null) {
            saveButton.setVisibility(View.GONE);
        }
    }

    private class ProfileClickListener implements View.OnClickListener {
        @Override
        public void onClick(View v) {
            if(isValidInputByUser()) {
                makeProfileEditRequest();
            }
        }
    }

    private boolean isValidInputByUser() {
        boolean bResult = true;
        if(!TextUtils.isEmpty(contactEmailEditText.getText().toString())) {
            // since email id is not mandatory field we check validation
            // only if some value entered by user
            if (!Utils.isValidEmail(contactEmailEditText.getText().toString())) {
                Toast.makeText(this, "Please enter valid email Id!",
                        Toast.LENGTH_SHORT).show();
                bResult = false;
            }
        }

        return bResult;
    }

    private class PasswordClickListener implements View.OnClickListener {
        @Override
        public void onClick(View v) {
            showPasswordChangeDialog();
        }
    }

    private class AddressClickListener implements View.OnClickListener {
        @Override
        public void onClick(View v) {
            showAddressChangeDialog();
        }
    }

    private void showPasswordChangeDialog() {
        PasswordChangeDialogFragment passwordDialog = new PasswordChangeDialogFragment();
        passwordDialog.show(this.getSupportFragmentManager(), "password_change_dialog");
    }

    private void showAddressChangeDialog() {
        AddressChangeDialogFragment addressDialog = new AddressChangeDialogFragment();
        addressDialog.setActivity(this);
        addressDialog.show(this.getSupportFragmentManager(), "address_change_dialog");
    }

    public void updateAddressText() {
        addressEditText.setText(App.getProfile().address.getAddress());
        enableSave();
    }

    private class EditTextClickListener implements View.OnFocusChangeListener {

        @Override
        public void onFocusChange(View v, boolean hasFocus) {
            if (hasFocus) {
                saveButton.setVisibility(View.VISIBLE);
            }
        }
    }

    private void setFromData() {
        usernameEditText.setText(Utils.def(App.getProfile().username, ""));
        nameEditText.setText(Utils.def(App.getProfile().userFullName, ""));
        /*addressEditText.setText(App.getProfile().address.getAddress());*/
        addressEditText.setText(App.getProfile().userAddress);
        contactNameEditText.setText(Utils.def(App.getProfile().userContactName, ""));
        contactPhoneEditText.setText(Utils.def(App.getProfile().userPhone, ""));
        contactEmailEditText.setText(Utils.def(App.getProfile().userEmail, ""));
        contactDesignationEditText.setText(Utils.def(App.getProfile().userDesignation, ""));
        city_autoComplete.setText(Utils.def(App.getProfile().mCityName,""));
    }

    @Override
    protected void onResume() {
        super.onResume();
        App.setFromSharedPreferencesIfNeeded();
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
        builder.setMessage("All the profile details you have edited so far will be discarded");
        builder.setPositiveButton("Stay", new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int id) {

            }
        });
        builder.setNegativeButton("Discard", new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int id) {
                ProfileActivity.super.onBackPressed();
            }
        });
        builder.show();
    }


}
