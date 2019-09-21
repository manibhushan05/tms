package in.aaho.android.loads;

import android.app.DatePickerDialog;
import android.content.Intent;
import android.os.Bundle;
import android.support.design.widget.NavigationView;
import android.support.design.widget.TextInputEditText;
import android.support.design.widget.TextInputLayout;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.KeyEvent;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.AutoCompleteTextView;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.DatePicker;
import android.widget.LinearLayout;
import android.widget.TextView;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.Calendar;

import in.aaho.android.loads.adapter.AahoOfficeSuggestionAdapter;
import in.aaho.android.loads.adapter.CitySuggestionAdapter;
import in.aaho.android.loads.adapter.VehicleTypeSuggestionAdapter;
import in.aaho.android.loads.adapter.CustomerSuggestionAdapter;
import in.aaho.android.loads.common.ApiResponseListener;
import in.aaho.android.loads.common.EditTextWatcher;
import in.aaho.android.loads.common.Utils;
import in.aaho.android.loads.parser.AahoOfficeParser;
import in.aaho.android.loads.parser.CityParser;
import in.aaho.android.loads.parser.VehicleTypeParser;
import in.aaho.android.loads.parser.CustomerParser;
import in.aaho.android.loads.requests.RequirementRequest;
import in.aaho.android.loads.requests.LogoutRequest;
import in.aaho.android.loads.common.BaseActivity;
import in.aaho.android.loads.requests.RequirementUpdateRequest;

/**
 * Created by aaho on 18/04/18.
 */

public class RequirementActivity extends BaseActivity implements View.OnClickListener{
    private static final String TAG = "RequirementActivity";
    Button mSubmitButton;
    TextInputEditText mFromShipDateEditText;
    TextInputEditText mToShipDateEditText;
    TextInputEditText mTonnageEditText;
    TextInputLayout mTonnageTextInputLayout;
    TextInputEditText mNoOfVehiclesEditText;
    TextInputLayout mNoOfVehiclesTextInputLayout;
    TextInputEditText mMaterialEditText;
    TextInputLayout mMaterialTextInputLayout;
    TextInputEditText mRateEditText;
    TextInputEditText mRemarkEditText;
    TextInputLayout mRateTextInputLayout;
    TextInputLayout mRemarkTextInputLayout;
    private AutoCompleteTextView fromCity_autoComplete;
    private AutoCompleteTextView toCity_autoComplete;
    private AutoCompleteTextView aahoOffice_autoComplete;
    private AutoCompleteTextView vehicleType_autoComplete;
    private AutoCompleteTextView client_autoComplete;
    private Integer mReqId;
    private Integer mFromCityId;
    private Integer mToCityId;
    private Integer mVehicleTypeId;
    private Integer mClientId;
    private String mFromShipDate;
    private String mToShipDate;
    private Integer mAahoOfficeId;
    private LinearLayout linear_fromcity_section;
    private LinearLayout linear_tocity_section;
    private LinearLayout linear_aahooffice_section;
    private LinearLayout linear_vehicletype_section;
    private LinearLayout linear_client_section;
    private CheckBox cbIsVerified;
    private CheckBox cbFullfilled;
    private CheckBox cbCancelled;
    private TextView txtStatus;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_requirement);

        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        getSupportActionBar().setTitle("Aaho Loads");

        setViewRefs();
        setClickListeners();

        Bundle bundle = getIntent().getExtras();
        if(bundle != null) {
            autoFillData(bundle);
        }
    }

    @Override
    public void onClick(View view) {

    }

    public void setClickListeners(){
        mSubmitButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                mSubmitButton.setClickable(false);
                makeReqSubmitRequest();
            }
        });
        mTonnageEditText.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                if(i == 0) {
                    mTonnageTextInputLayout.setError(null);
                }
            }
        });
        mNoOfVehiclesEditText.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                if(i == 0) {
                    mNoOfVehiclesTextInputLayout.setError(null);
                }
            }
        });
        mMaterialEditText.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                if(i == 0) {
                    mMaterialTextInputLayout.setError(null);
                }
            }
        });
        mRateEditText.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                if(i == 0) {
                    mRateTextInputLayout.setError(null);
                }
            }
        });

        mFromShipDateEditText.setOnClickListener(new FromShipDateClickListener());
        mToShipDateEditText.setOnClickListener(new ToShipDateClickListener());

        fromCity_autoComplete.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            public void onItemClick(AdapterView<?> parent, View view, int position, long rowId) {
                CityParser selection = (CityParser) parent.getItemAtPosition(position);
                fromCity_autoComplete.setText(selection.getText().toString());
                mFromCityId = selection.getId();
            }
        });
        toCity_autoComplete.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            public void onItemClick(AdapterView<?> parent, View view, int position, long rowId) {
                CityParser selection = (CityParser) parent.getItemAtPosition(position);
                toCity_autoComplete.setText(selection.getText().toString());
                mToCityId = selection.getId();
            }
        });
        aahoOffice_autoComplete.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            public void onItemClick(AdapterView<?> parent, View view, int position, long rowId) {
                AahoOfficeParser selection = (AahoOfficeParser) parent.getItemAtPosition(position);
                aahoOffice_autoComplete.setText(selection.getText().toString());
                mAahoOfficeId = selection.getId();
            }
        });
//        aahoOffice_autoComplete.setThreshold(0);
        vehicleType_autoComplete.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            public void onItemClick(AdapterView<?> parent, View view, int position, long rowId) {
                VehicleTypeParser selection = (VehicleTypeParser) parent.getItemAtPosition(position);
                vehicleType_autoComplete.setText(selection.getText().toString());
                mVehicleTypeId = selection.getId();
            }
        });
//        vehicleType_autoComplete.setThreshold(0);
        client_autoComplete.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            public void onItemClick(AdapterView<?> parent, View view, int position, long rowId) {
                CustomerParser selection = (CustomerParser) parent.getItemAtPosition(position);
                client_autoComplete.setText(selection.getText().toString());
                mClientId = selection.getId();
            }
        });

        fromCity_autoComplete.setAdapter(new CitySuggestionAdapter(RequirementActivity.this,
                fromCity_autoComplete.getText().toString()));

        toCity_autoComplete.setAdapter(new CitySuggestionAdapter(RequirementActivity.this,
                toCity_autoComplete.getText().toString()));

        aahoOffice_autoComplete.setAdapter(new AahoOfficeSuggestionAdapter(RequirementActivity.this,
                aahoOffice_autoComplete.getText().toString()));

        vehicleType_autoComplete.setAdapter(new VehicleTypeSuggestionAdapter(RequirementActivity.this,
                vehicleType_autoComplete.getText().toString()));

        client_autoComplete.setAdapter(new CustomerSuggestionAdapter(RequirementActivity.this,
                client_autoComplete.getText().toString()));

    }

    private void setViewRefs() {
        mSubmitButton = (Button) findViewById(R.id.btn_submit);
        mFromShipDateEditText = (TextInputEditText)findViewById(R.id.from_shipment_date);
        mToShipDateEditText = (TextInputEditText)findViewById(R.id.to_shipment_date);
        mTonnageEditText = (TextInputEditText) findViewById(R.id.tonnage);
        mTonnageTextInputLayout = (TextInputLayout) findViewById(R.id.tonnageTextInputLayout);
        mNoOfVehiclesEditText = (TextInputEditText) findViewById(R.id.no_of_vehicles);
        mNoOfVehiclesTextInputLayout = (TextInputLayout) findViewById(R.id.noOfVehiclesTextInputLayout);
        mMaterialEditText = (TextInputEditText) findViewById(R.id.material);
        mMaterialTextInputLayout = (TextInputLayout) findViewById(R.id.materialTextInputLayout);
        mRateEditText = (TextInputEditText) findViewById(R.id.rate);
        mRemarkEditText = (TextInputEditText) findViewById(R.id.remark);
        mRateTextInputLayout = (TextInputLayout) findViewById(R.id.rateTextInputLayout);
        mRemarkTextInputLayout = (TextInputLayout) findViewById(R.id.remarkTextInputLayout);
        linear_fromcity_section = (LinearLayout)findViewById(R.id.linear_fromcity_section);
        linear_tocity_section = (LinearLayout)findViewById(R.id.linear_tocity_section);
        linear_aahooffice_section = (LinearLayout)findViewById(R.id.linear_aahooffice_section);
        linear_vehicletype_section = (LinearLayout)findViewById(R.id.linear_vehicletype_section);
        linear_client_section = (LinearLayout)findViewById(R.id.linear_client_section);
        fromCity_autoComplete = (AutoCompleteTextView)findViewById(R.id.fromCity_autoComplete);
        toCity_autoComplete = (AutoCompleteTextView)findViewById(R.id.toCity_autoComplete);
        aahoOffice_autoComplete = (AutoCompleteTextView)findViewById(R.id.aahoOffice_autoComplete);
        vehicleType_autoComplete = (AutoCompleteTextView)findViewById(R.id.vehicleType_autoComplete);
        client_autoComplete = (AutoCompleteTextView)findViewById(R.id.client_autoComplete);
        linear_fromcity_section.setVisibility(View.VISIBLE);
        linear_tocity_section.setVisibility(View.VISIBLE);
        linear_aahooffice_section.setVisibility(View.VISIBLE);
        linear_vehicletype_section.setVisibility(View.VISIBLE);
        linear_client_section.setVisibility(View.VISIBLE);
        cbIsVerified = findViewById(R.id.cbIsVerified);
        cbFullfilled = findViewById(R.id.cbFullfilled);
        cbCancelled = findViewById(R.id.cbCancelled);
        txtStatus = findViewById(R.id.txtStatus);
    }

    private void makeReqSubmitRequest() {
        String tonnage = mTonnageEditText.getText().toString();
        String no_of_vehicles = mNoOfVehiclesEditText.getText().toString();
        String material = mMaterialEditText.getText().toString();
        String rate = mRateEditText.getText().toString();
        String remark = mRemarkEditText.getText().toString();
        if(getIntent().getExtras() == null) {
            // means this is new requirement
            RequirementRequest requirementRequest = new RequirementRequest(mClientId, mFromShipDate,
                    mToShipDate, mFromCityId, mToCityId, mAahoOfficeId, tonnage, no_of_vehicles,
                    material, mVehicleTypeId, rate, remark, new RequirementListener());
            queue(requirementRequest, false);
        } else {
            // means we have to update the data
            mFromShipDate = mFromShipDateEditText.getText().toString();
            if(mToShipDateEditText.getText() == null || mToShipDateEditText.getText().toString().equalsIgnoreCase("")) {
                mToShipDate = null;
            } else {
                mToShipDate = mToShipDateEditText.getText().toString();
            }

            RequirementUpdateRequest requirementUpdateRequest = new RequirementUpdateRequest(
                    mReqId,mClientId, mFromShipDate,mToShipDate, mFromCityId, mToCityId,
                    mAahoOfficeId, tonnage, no_of_vehicles,
                    material, mVehicleTypeId, rate, remark, cbIsVerified.isChecked(), cbFullfilled.isChecked(),
                    cbCancelled.isChecked(), new RequirementUpdateListener());
            queue(requirementUpdateRequest, true);
        }
    }

    private class RequirementListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            try{
                if(response.get("status").equals("success")){
                    mSubmitButton.setClickable(true);
                    mFromShipDateEditText.getText().clear();
                    mToShipDateEditText.getText().clear();
                    client_autoComplete.getText().clear();
                    fromCity_autoComplete.getText().clear();
                    toCity_autoComplete.getText().clear();
                    aahoOffice_autoComplete.getText().clear();
                    vehicleType_autoComplete.getText().clear();
                    mTonnageEditText.getText().clear();
                    mNoOfVehiclesEditText.getText().clear();
                    mMaterialEditText.getText().clear();
                    mRateEditText.getText().clear();
                    mRemarkEditText.getText().clear();
                    Utils.toast("Requirement is submitted successfully!");
                    RequirementActivity.this.finish();
                }else{
                    mSubmitButton.setClickable(true);
                    Utils.toast("Unsuccessful! " + response.get("msg"));
                }
            } catch (JSONException e) {
                e.printStackTrace();
                toast("error reading response data:\n" );
            }
        }

        @Override
        public void onError() {
            dismissProgress();
            //mLoginButton.setClickable(true);
        }
    }

    private class RequirementUpdateListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            try{
                if(response.get("status").equals("success")){
                    mSubmitButton.setClickable(true);
                    mFromShipDateEditText.getText().clear();
                    mToShipDateEditText.getText().clear();
                    client_autoComplete.getText().clear();
                    fromCity_autoComplete.getText().clear();
                    toCity_autoComplete.getText().clear();
                    aahoOffice_autoComplete.getText().clear();
                    vehicleType_autoComplete.getText().clear();
                    mTonnageEditText.getText().clear();
                    mNoOfVehiclesEditText.getText().clear();
                    mMaterialEditText.getText().clear();
                    mRateEditText.getText().clear();
                    mRemarkEditText.getText().clear();
                    Utils.toast("Requirement is updated successfully!");
                    RequirementActivity.this.finish();
                }else{
                    mSubmitButton.setClickable(true);
                    Utils.toast("Unsuccessful! " + response.get("msg"));
                }
            } catch (JSONException e) {
                e.printStackTrace();
                toast("error reading response data:\n" );
            }
        }

        @Override
        public void onError() {
            dismissProgress();
            mSubmitButton.setClickable(true);
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
    }

    @Override
    protected void onPause() {
        super.onPause();
    }

    @Override
    protected void onStop() {
        super.onStop();
    }

    @Override
    protected void onStart() {
        super.onStart();
    }

    @Override
    protected void onRestart() {
        super.onRestart();
    }

    @Override
    protected void onResume() {
        super.onResume();
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_BACK && event.getRepeatCount() == 0) {
            finish();
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }

    private class FromShipDateClickListener implements View.OnClickListener {
        @Override
        public void onClick(View v) {
            Calendar c = Calendar.getInstance();
            int mYear = c.get(Calendar.YEAR);
            int mMonth = c.get(Calendar.MONTH);
            int mDay = c.get(Calendar.DAY_OF_MONTH);
            ValidityFromSetListener dateSetListener = new ValidityFromSetListener();
            DatePickerDialog datePickerDialog = new DatePickerDialog(RequirementActivity.this, dateSetListener, mYear, mMonth, mDay);
            datePickerDialog.show();
            datePickerDialog.getDatePicker().setMinDate(System.currentTimeMillis() - 1000);
        }
    }
    private class ValidityFromSetListener implements DatePickerDialog.OnDateSetListener {
        @Override
        public void onDateSet(DatePicker view, int year, int monthOfYear, int dayOfMonth) {
            mFromShipDate = Integer.toString(year)+"-"+Integer.toString(monthOfYear+1)+"-"+Integer.toString(dayOfMonth);
            mFromShipDateEditText.setText(mFromShipDate);
        }
    }
    private class ToShipDateClickListener implements View.OnClickListener {
        @Override
        public void onClick(View v) {
            Calendar c = Calendar.getInstance();
            int mYear = c.get(Calendar.YEAR);
            int mMonth = c.get(Calendar.MONTH);
            int mDay = c.get(Calendar.DAY_OF_MONTH);
            ValidityToSetListener dateSetListener = new ValidityToSetListener();
            DatePickerDialog datePickerDialog = new DatePickerDialog(RequirementActivity.this, dateSetListener, mYear, mMonth, mDay);
            datePickerDialog.show();
            datePickerDialog.getDatePicker().setMinDate(System.currentTimeMillis() - 1000);
        }
    }
    private class ValidityToSetListener implements DatePickerDialog.OnDateSetListener {
        @Override
        public void onDateSet(DatePicker view, int year, int monthOfYear, int dayOfMonth) {
            mToShipDate = Integer.toString(year)+"-"+Integer.toString(monthOfYear+1)+"-"+Integer.toString(dayOfMonth);
            mToShipDateEditText.setText(mToShipDate);
        }
    }

    private void autoFillData(Bundle bundle) {
        if(bundle != null) {
            client_autoComplete.setText(bundle.getString("client"));
            mFromShipDateEditText.setText(bundle.getString("fromShipmentDate"));
            mToShipDateEditText.setText(bundle.getString("toShipmentDate"));
            fromCity_autoComplete.setText(bundle.getString("fromCity"));
            toCity_autoComplete.setText(bundle.getString("toCity"));
            aahoOffice_autoComplete.setText(bundle.getString("aahoOffice"));
            mTonnageEditText.setText(bundle.getString("tonnage"));
            mNoOfVehiclesEditText.setText(bundle.getString("noOfVehicles"));
            mMaterialEditText.setText(bundle.getString("material"));
            vehicleType_autoComplete.setText(bundle.getString("typeOfVehicle"));
            mRateEditText.setText(bundle.getString("rate"));
            mRemarkEditText.setText(bundle.getString("remark"));

            // set id's
            mReqId = Integer.valueOf(bundle.getString("id"));
            mFromCityId = Integer.valueOf(bundle.getString("fromCityId"));
            mToCityId = Integer.valueOf(bundle.getString("toCityId"));
            String vehicle_id = bundle.getString("typeOfVehicleId");
            if(vehicle_id != null && vehicle_id.length() > 0)
                mVehicleTypeId = Integer.valueOf(vehicle_id);
            mClientId = Integer.valueOf(bundle.getString("clientId"));
            mAahoOfficeId = Integer.valueOf(bundle.getString("officeId"));

            mSubmitButton.setText("Update");

            if(bundle.getString("context").equals("CustomerLoads")){
                cbIsVerified.setVisibility(View.VISIBLE);
                if(bundle.getString("reqStatus").equals("open")){
                    cbIsVerified.setChecked(true);
                }
            }
            if(bundle.getString("context").equals("MyLoads")){
                cbCancelled.setVisibility(View.VISIBLE);
                cbFullfilled.setVisibility(View.VISIBLE);
                txtStatus.setVisibility(View.VISIBLE);
                if(bundle.getString("reqStatus").equals("cancelled")){
                    cbCancelled.setChecked(true);
                }
                if(bundle.getString("reqStatus").equals("fulfilled")){
                    cbFullfilled.setChecked(true);
                }
                if(bundle.getString("reqStatus").equals("open")){
                    cbIsVerified.setChecked(true);
                }
            }

            if(bundle.getBoolean("rdOnlyStatus")){
                disableRequirementForm();
            }
        }
    }

    private void disableRequirementForm(){
        client_autoComplete.setEnabled(false);
        fromCity_autoComplete.setEnabled(false);
        toCity_autoComplete.setEnabled(false);
        mFromShipDateEditText.setEnabled(false);
        mToShipDateEditText.setEnabled(false);
        aahoOffice_autoComplete.setEnabled(false);
        mTonnageEditText.setEnabled(false);
        mNoOfVehiclesEditText.setEnabled(false);
        mMaterialEditText.setEnabled(false);
        vehicleType_autoComplete.setEnabled(false);
        mRateEditText.setEnabled(false);
        mRemarkEditText.setEnabled(false);
        mSubmitButton.setEnabled(false);
        cbIsVerified.setEnabled(false);
        cbCancelled.setEnabled(false);
        cbFullfilled.setEnabled(false);
    }


}

