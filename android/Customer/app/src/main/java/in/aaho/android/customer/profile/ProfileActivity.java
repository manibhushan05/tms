package in.aaho.android.customer.profile;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.widget.DefaultItemAnimator;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.support.v7.widget.Toolbar;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.customer.common.ApiResponseListener;
import in.aaho.android.customer.common.BaseActivity;
import in.aaho.android.customer.LandingActivity;
import in.aaho.android.customer.R;
import in.aaho.android.customer.booking.App;
import in.aaho.android.customer.booking.UserAddress;
import in.aaho.android.customer.booking.Vendor;
import in.aaho.android.customer.requests.ProfileEditRequest;


public class ProfileActivity extends BaseActivity {

    private EditText usernameEditText, passwordEditText;
    private EditText nameEditText, addressEditText;
    private EditText contactNameEditText, contactPhoneEditText;
    private EditText contactEmailEditText, contactDesignationEditText;

    private TextView noVendorsTextView;
    private Button addVendorButton;

    private Button saveButton;

    private RecyclerView vendorContainer;

    private ProfileVendorAdapter profileVendorAdapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.profile_activity);

        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        toolbar.setTitle("Profile");
        setSupportActionBar(toolbar);
        getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        getSupportActionBar().setDisplayShowHomeEnabled(true);

        profileVendorAdapter = new ProfileVendorAdapter(Vendor.getAll(), this);

        setViewVariables();
        setClickListeners();
        setupAdapters();
        setFromData();
    }

    private void setupAdapters() {
        setupVendorAdapter();
    }

    private void setupVendorAdapter() {
        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getApplicationContext());
        vendorContainer.setLayoutManager(mLayoutManager);
        vendorContainer.setItemAnimator(new DefaultItemAnimator());
        vendorContainer.setAdapter(profileVendorAdapter);

        profileVendorAdapter.notifyDataSetChanged();
        updateVendorUI();
    }

    public void updateVendorUI() {
        profileVendorAdapter.notifyDataSetChanged();
        if (profileVendorAdapter.getItemCount() == 0) {
            noVendorsTextView.setVisibility(View.VISIBLE);
        } else {
            noVendorsTextView.setVisibility(View.GONE);
        }
    }

    private void setViewVariables() {
        vendorContainer = (RecyclerView) findViewById(R.id.profile_vendor_container);

        usernameEditText = (EditText) findViewById(R.id.profile_username_edittext);
        passwordEditText = (EditText) findViewById(R.id.profile_password_edittext);

        nameEditText = (EditText) findViewById(R.id.profile_name_edittext);
        addressEditText = (EditText) findViewById(R.id.profile_address_edittext);

        contactNameEditText = (EditText) findViewById(R.id.profile_contact_name_edittext);
        contactPhoneEditText = (EditText) findViewById(R.id.profile_contact_phone_edittext);
        contactEmailEditText = (EditText) findViewById(R.id.profile_contact_email_edittext);
        contactDesignationEditText = (EditText) findViewById(R.id.profile_designation_edittext);

        saveButton = (Button) findViewById(R.id.save_profile_btn);

        noVendorsTextView = (TextView) findViewById(R.id.profile_no_vendors_message);
        addVendorButton = (Button) findViewById(R.id.profile_add_vendor_btn);
    }

    private JSONObject getUpdatedProfileData() {
        String name = nameEditText.getText().toString().trim();
        String contactName = contactNameEditText.getText().toString().trim();
        String contactPhone = contactPhoneEditText.getText().toString().trim();
        String contactEmail = contactEmailEditText.getText().toString().trim();
        String contactDesignation = contactDesignationEditText.getText().toString().trim();

        try {
            JSONObject data = App.getUpdatedUserProfileJson(name, contactName, contactPhone,
                    contactEmail, contactDesignation);
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
            toast("Profile Updated");
            try {
                App.setUserData(response.getJSONObject("user"));
                resetProfilePage();
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }

        @Override
        public void onError() {
            dismissProgress();
        }
    }

    private void resetProfilePage() {
        setFromData();
        saveButton.setVisibility(View.GONE);
    }

    private void setClickListeners() {
        nameEditText.setOnFocusChangeListener(new EditTextClickListener());
        contactNameEditText.setOnFocusChangeListener(new EditTextClickListener());
        contactPhoneEditText.setOnFocusChangeListener(new EditTextClickListener());
        contactEmailEditText.setOnFocusChangeListener(new EditTextClickListener());
        contactDesignationEditText.setOnFocusChangeListener(new EditTextClickListener());
        passwordEditText.setOnClickListener(new PasswordClickListener());
        addressEditText.setOnClickListener(new AddressClickListener());
        saveButton.setOnClickListener(new ProfileClickListener());
        addVendorButton.setOnClickListener(new AddVendorClickListener());
    }

    private class AddVendorClickListener implements View.OnClickListener {
        @Override
        public void onClick(View v) {
            showAddVendorDialog();
        }
    }

    private void showAddVendorDialog() {
        VendorAddDialogFragment.showNewDialog(this, new VendorAddDialogFragment.UpdateVendorListener() {
            @Override
            public void onVendorUpdate() {
                profileVendorAdapter.notifyDataSetChanged();
            }
        });
    }

    private class ProfileClickListener implements View.OnClickListener {
        @Override
        public void onClick(View v) {
            makeProfileEditRequest();
        }
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
        // AddressChangeDialogFragment addressDialog = new AddressChangeDialogFragment();
        // addressDialog.setActivity(this);
        // addressDialog.show(this.getSupportFragmentManager(), "address_change_dialog");
    }

    public void updateAddressText() {
        addressEditText.setText(UserAddress.get().getAddress());
        saveButton.setVisibility(View.VISIBLE);
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
        usernameEditText.setText(App.username == null ? "" : App.username);
        nameEditText.setText(App.userFullName == null ? "" : App.userFullName);
        addressEditText.setText(UserAddress.get().getAddress());
        contactNameEditText.setText(App.userContactName == null ? "" : App.userContactName);
        contactPhoneEditText.setText(App.userPhone == null ? "" : App.userPhone);
        contactEmailEditText.setText(App.userEmail == null ? "" : App.userEmail);
        contactDesignationEditText.setText(App.userDesignation == null ? "" : App.userDesignation);
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int itemId = item.getItemId();
        switch (itemId) {
            case android.R.id.home:
                startActivity(new Intent(ProfileActivity.this, LandingActivity.class));
                this.finish();
                break;

        }
        return super.onOptionsItemSelected(item);
    }

    @Override
    protected void onResume() {
        super.onResume();
        App.setFromSharedPreferencesIfNeeded();
    }

    @Override
    public void onBackPressed() {
        super.onBackPressed();
        this.finish();
    }
}
