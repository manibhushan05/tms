package in.aaho.android.employee;

import android.annotation.TargetApi;
import android.app.AlertDialog;
import android.app.DatePickerDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import android.support.annotation.RequiresApi;
import android.support.design.widget.NavigationView;
import android.support.design.widget.TextInputEditText;
import android.support.design.widget.TextInputLayout;
import android.support.v7.widget.Toolbar;
import android.text.InputFilter;
import android.text.InputType;
import android.text.Spanned;
import android.text.TextUtils;
import android.util.Log;
import android.view.KeyEvent;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.AutoCompleteTextView;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.CompoundButton;
import android.widget.DatePicker;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import com.android.volley.VolleyError;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Iterator;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import in.aaho.android.employee.adapter.AahoOfficeSuggestionAdapter;
import in.aaho.android.employee.adapter.CitySuggestionAdapter;
import in.aaho.android.employee.adapter.VehicleTypeSuggestionAdapter;
import in.aaho.android.employee.adapter.CustomerSuggestionAdapter;
import in.aaho.android.employee.common.ApiResponseListener;
import in.aaho.android.employee.common.EditTextWatcher;
import in.aaho.android.employee.common.Utils;
import in.aaho.android.employee.parser.AahoOfficeParser;
import in.aaho.android.employee.parser.CityParser;
import in.aaho.android.employee.parser.VehicleTypeParser;
import in.aaho.android.employee.parser.CustomerParser;
import in.aaho.android.employee.requests.ReasonListDataRequest;
import in.aaho.android.employee.requests.RequirementRequest;
import in.aaho.android.employee.requests.LogoutRequest;
import in.aaho.android.employee.common.BaseActivity;
import in.aaho.android.employee.requests.RequirementUpdateRequest;
import in.aaho.android.employee.requests.SmeDataRequest;

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
    private ImageView imgClearClient,imgClearFromDate,imgClearToDate,
            imgClearFromCity,imgClearToCity,imgClearAahoOffice,
            imgClearTonnage,imgClearNoOfVehicles,imgClearMaterial,
            imgClearVehicleType,imgClearRate,imgClearRemark;
    private Integer mReqId;
    private Integer mFromCityId = 0;
    private Integer mToCityId = 0;
    private Integer mVehicleTypeId = 0;
    private Integer mClientId = 0;
    private String mFromShipDate;
    private String mToShipDate;
    private String cancelReason;
    private Integer mAahoOfficeId = 0;
    private LinearLayout linear_fromcity_section;
    private LinearLayout linear_tocity_section;
    private LinearLayout linear_aahooffice_section;
    private LinearLayout linear_vehicletype_section;
    private LinearLayout linear_client_section;
    private CheckBox cbIsVerified;
    private CheckBox cbFullfilled;
    private CheckBox cbCancelled;
    private TextView txtStatus,tvCancelReason;
    /* To know whether list is dismissed because of edit reason dialog or not */
    private boolean isReasonEditDialogShowing = false;

    private ArrayList<String> reasonList = new ArrayList<>();
    private boolean bIsUpdate = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_requirement_new);

        setViewRefs();
        setClickListeners();

        Bundle bundle = getIntent().getExtras();
        if(bundle != null) {
            if(bundle.containsKey("toolbarName")) {
                Toolbar toolbar = findViewById(R.id.toolbar);
                setSupportActionBar(toolbar);
                getSupportActionBar().setTitle(bundle.getString("toolbarName"));
            }
            if(bundle.containsKey("isUpdate")) {
                bIsUpdate = bundle.getBoolean("isUpdate");
                if(bIsUpdate) {
                    // Auto fill data
                    autoFillData(bundle);
                }
            }
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

        client_autoComplete.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                if(i == 0) {
                    mClientId = 0;
                    // As discussed aaho office & material should get cleared on client clear
                    mAahoOfficeId = 0;
                    aahoOffice_autoComplete.setText("");
                    mMaterialEditText.setText("");
                    client_autoComplete.setError(null);
                    imgClearClient.setVisibility(View.INVISIBLE);
                }
                if(i2 > 0) {
                    imgClearClient.setVisibility(View.VISIBLE);
                }
            }
        });

        fromCity_autoComplete.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                if(i == 0) {
                    mFromCityId = 0;
                    fromCity_autoComplete.setError(null);
                    imgClearFromCity.setVisibility(View.INVISIBLE);
                }
                if(i2 > 0) {
                    imgClearFromCity.setVisibility(View.VISIBLE);
                }
            }
        });

        toCity_autoComplete.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                if(i == 0) {
                    mToCityId = 0;
                    toCity_autoComplete.setError(null);
                    imgClearToCity.setVisibility(View.INVISIBLE);
                }
                if(i2 > 0) {
                    imgClearToCity.setVisibility(View.VISIBLE);
                }
            }
        });

        mToShipDateEditText.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                if(i == 0) {
                    mToShipDate = "";
                    imgClearToDate.setVisibility(View.INVISIBLE);
                }
                if(i2 > 0) {
                    imgClearToDate.setVisibility(View.VISIBLE);
                }
            }
        });
        mFromShipDateEditText.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                if(i == 0) {
                    mFromShipDate = "";
                    imgClearFromDate.setVisibility(View.INVISIBLE);
                }
                if(i2 > 0) {
                    imgClearFromDate.setVisibility(View.VISIBLE);
                }
            }
        });
        mTonnageEditText.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                if(i == 0) {
                    mTonnageTextInputLayout.setError(null);
                    imgClearTonnage.setVisibility(View.INVISIBLE);
                }
                if(i2 > 0) {
                    imgClearTonnage.setVisibility(View.VISIBLE);
                }
            }
        });
        mNoOfVehiclesEditText.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                if(i == 0) {
                    mNoOfVehiclesTextInputLayout.setError(null);
                    imgClearNoOfVehicles.setVisibility(View.INVISIBLE);
                }
                if(i2 > 0) {
                    imgClearNoOfVehicles.setVisibility(View.VISIBLE);
                }
            }
        });
        mMaterialEditText.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                if(i == 0) {
                    mMaterialTextInputLayout.setError(null);
                    imgClearMaterial.setVisibility(View.INVISIBLE);
                }
                if(i2 > 0) {
                    imgClearMaterial.setVisibility(View.VISIBLE);
                }
            }
        });
        mRateEditText.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                if(i == 0) {
                    mRateTextInputLayout.setError(null);
                    imgClearRate.setVisibility(View.INVISIBLE);
                }
                if(i2 > 0) {
                    imgClearRate.setVisibility(View.VISIBLE);
                }
            }
        });

        aahoOffice_autoComplete.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                if(i == 0) {
                    mAahoOfficeId = 0;
                    aahoOffice_autoComplete.setError(null);
                    imgClearAahoOffice.setVisibility(View.INVISIBLE);
                }
                if(i2 > 0) {
                    imgClearAahoOffice.setVisibility(View.VISIBLE);
                }
            }
        });

        vehicleType_autoComplete.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                if(i == 0) {
                    mVehicleTypeId = 0;
                    vehicleType_autoComplete.setError(null);
                    imgClearVehicleType.setVisibility(View.INVISIBLE);
                }
                if(i2 > 0) {
                    imgClearVehicleType.setVisibility(View.VISIBLE);
                }
            }
        });

        mRemarkEditText.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                if(i == 0) {
                    mRemarkEditText.setError(null);
                    imgClearRemark.setVisibility(View.INVISIBLE);
                }
                if(i2 > 0) {
                    imgClearRemark.setVisibility(View.VISIBLE);
                }
            }
        });


        mFromShipDateEditText.setOnClickListener(new FromShipDateClickListener());
        mToShipDateEditText.setOnClickListener(new ToShipDateClickListener());

        client_autoComplete.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            public void onItemClick(AdapterView<?> parent, View view, int position, long rowId) {
                CustomerParser selection = (CustomerParser) parent.getItemAtPosition(position);
                client_autoComplete.setText(selection.getText().toString());
                mClientId = selection.getId();
                imgClearClient.setVisibility(View.VISIBLE);
                // Call API to get material & aaho office data from server to auto fill
                makeAutoFillDataReq();
            }
        });

        fromCity_autoComplete.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            public void onItemClick(AdapterView<?> parent, View view, int position, long rowId) {
                CityParser selection = (CityParser) parent.getItemAtPosition(position);
                fromCity_autoComplete.setText(selection.getText().toString());
                mFromCityId = selection.getId();
                imgClearFromCity.setVisibility(View.VISIBLE);
            }
        });

        toCity_autoComplete.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            public void onItemClick(AdapterView<?> parent, View view, int position, long rowId) {
                CityParser selection = (CityParser) parent.getItemAtPosition(position);
                toCity_autoComplete.setText(selection.getText().toString());
                mToCityId = selection.getId();
                imgClearToCity.setVisibility(View.VISIBLE);
            }
        });

        aahoOffice_autoComplete.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            public void onItemClick(AdapterView<?> parent, View view, int position, long rowId) {
                AahoOfficeParser selection = (AahoOfficeParser) parent.getItemAtPosition(position);
                aahoOffice_autoComplete.setText(selection.getText().toString());
                mAahoOfficeId = selection.getId();
                imgClearAahoOffice.setVisibility(View.VISIBLE);
            }
        });

        vehicleType_autoComplete.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            public void onItemClick(AdapterView<?> parent, View view, int position, long rowId) {
                VehicleTypeParser selection = (VehicleTypeParser) parent.getItemAtPosition(position);
                vehicleType_autoComplete.setText(selection.getText().toString());
                mVehicleTypeId = selection.getId();
                imgClearVehicleType.setVisibility(View.VISIBLE);
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

        cbFullfilled.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton compoundButton, boolean isChecked) {
                if(isChecked && compoundButton.isPressed()) {
                    cbCancelled.setChecked(false);
                    reasonList.clear();
                    setReasonText("");
                }
            }
        });

        cbCancelled.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton compoundButton, boolean isChecked) {
                if(isChecked && compoundButton.isPressed()) {
                    cbFullfilled.setChecked(false);
                    reasonList.clear();
                    makeReasonListDataReq();
                } else if(compoundButton.isPressed()){
                    reasonList.clear();
                    setReasonText("");
                }
            }
        });

        // Allow only 4 digit & 2 decimal
        mTonnageEditText.setFilters(new InputFilter[] {
                new DecimalDigitsInputFilter(4,2)});

        imgClearClient.setOnClickListener(new ImageClearClientListener());
        imgClearFromDate.setOnClickListener(new ImageClearEditTextListener(mFromShipDateEditText));
        imgClearToDate.setOnClickListener(new ImageClearEditTextListener(mToShipDateEditText));
        imgClearFromCity.setOnClickListener(new ImageClearAutoCompleteTextViewListener(fromCity_autoComplete));
        imgClearToCity.setOnClickListener(new ImageClearAutoCompleteTextViewListener(toCity_autoComplete));
        imgClearAahoOffice.setOnClickListener(new ImageClearAutoCompleteTextViewListener(aahoOffice_autoComplete));
        imgClearTonnage.setOnClickListener(new ImageClearEditTextListener(mTonnageEditText));
        imgClearNoOfVehicles.setOnClickListener(new ImageClearEditTextListener(mNoOfVehiclesEditText));
        imgClearMaterial.setOnClickListener(new ImageClearEditTextListener(mMaterialEditText));
        imgClearVehicleType.setOnClickListener(new ImageClearAutoCompleteTextViewListener(vehicleType_autoComplete));
        imgClearRate.setOnClickListener(new ImageClearEditTextListener(mRateEditText));
        imgClearRemark.setOnClickListener(new ImageClearEditTextListener(mRemarkEditText));
    }



    public class ImageClearEditTextListener implements View.OnClickListener {

        private EditText editText;
        public ImageClearEditTextListener(EditText editText) {
            this.editText = editText;
        }

        @Override
        public void onClick(View view) {
            editText.setText("");
        }
    }

    public class ImageClearAutoCompleteTextViewListener implements View.OnClickListener {

        private AutoCompleteTextView autoCompleteTextView;
        public ImageClearAutoCompleteTextViewListener(AutoCompleteTextView autoCompleteTextView) {
            this.autoCompleteTextView = autoCompleteTextView;
        }

        @Override
        public void onClick(View view) {
            autoCompleteTextView.setText("");
        }
    }

    public class ImageClearClientListener implements View.OnClickListener {

        @Override
        public void onClick(View view) {
            client_autoComplete.setText("");
            // As discussed aaho office & material should get cleared on client clear
            mAahoOfficeId = 0;
            aahoOffice_autoComplete.setText("");
            mMaterialEditText.setText("");
        }
    }

    private void setViewRefs() {
        mSubmitButton = findViewById(R.id.btn_submit);
        mFromShipDateEditText = findViewById(R.id.from_shipment_date);
        mToShipDateEditText = findViewById(R.id.to_shipment_date);
        mTonnageEditText = findViewById(R.id.tonnage);
        mTonnageTextInputLayout = findViewById(R.id.tonnageTextInputLayout);
        mNoOfVehiclesEditText = findViewById(R.id.no_of_vehicles);
        mNoOfVehiclesTextInputLayout = findViewById(R.id.noOfVehiclesTextInputLayout);
        mMaterialEditText = findViewById(R.id.material);
        mMaterialTextInputLayout = findViewById(R.id.materialTextInputLayout);
        mRateEditText = findViewById(R.id.rate);
        mRemarkEditText = findViewById(R.id.remark);
        mRateTextInputLayout = findViewById(R.id.rateTextInputLayout);
        mRemarkTextInputLayout = findViewById(R.id.remarkTextInputLayout);
        linear_fromcity_section = findViewById(R.id.linear_fromcity_section);
        linear_tocity_section = findViewById(R.id.linear_tocity_section);
        linear_aahooffice_section = findViewById(R.id.linear_aahooffice_section);
        linear_vehicletype_section = findViewById(R.id.linear_vehicletype_section);
        linear_client_section = findViewById(R.id.linear_client_section);
        fromCity_autoComplete = findViewById(R.id.fromCity_autoComplete);
        toCity_autoComplete = findViewById(R.id.toCity_autoComplete);
        aahoOffice_autoComplete = findViewById(R.id.aahoOffice_autoComplete);
        vehicleType_autoComplete = findViewById(R.id.vehicleType_autoComplete);
        client_autoComplete = findViewById(R.id.client_autoComplete);
        /*linear_fromcity_section.setVisibility(View.VISIBLE);
        linear_tocity_section.setVisibility(View.VISIBLE);
        linear_aahooffice_section.setVisibility(View.VISIBLE);
        linear_vehicletype_section.setVisibility(View.VISIBLE);
        linear_client_section.setVisibility(View.VISIBLE);*/
        cbIsVerified = findViewById(R.id.cbIsVerified);
        cbFullfilled = findViewById(R.id.cbFullfilled);
        cbCancelled = findViewById(R.id.cbCancelled);
        txtStatus = findViewById(R.id.txtStatus);
        tvCancelReason = findViewById(R.id.tvCancelReason);

        imgClearClient = findViewById(R.id.imgClearClient);
        imgClearFromDate = findViewById(R.id.imgClearFromDate);
        imgClearToDate = findViewById(R.id.imgClearToDate);
        imgClearFromCity = findViewById(R.id.imgClearFromCity);
        imgClearToCity = findViewById(R.id.imgClearToCity);
        imgClearAahoOffice = findViewById(R.id.imgClearAahoOffice);
        imgClearTonnage = findViewById(R.id.imgClearTonnage);
        imgClearNoOfVehicles = findViewById(R.id.imgClearNoOfVehicles);
        imgClearMaterial = findViewById(R.id.imgClearMaterial);
        imgClearVehicleType = findViewById(R.id.imgClearVehicleType);
        imgClearRate = findViewById(R.id.imgClearRate);
        imgClearRemark = findViewById(R.id.imgClearRemark);
    }

    private void makeReqSubmitRequest() {
        String tonnage = mTonnageEditText.getText().toString();
        if(TextUtils.isEmpty(tonnage) && tonnage.startsWith(".")) {
            tonnage = tonnage.replace(".","0.");
        }
        String no_of_vehicles = mNoOfVehiclesEditText.getText().toString();
        String material = mMaterialEditText.getText().toString();
        String rate = mRateEditText.getText().toString();
        String remark = mRemarkEditText.getText().toString();
        String fromShipmentDate = mFromShipDateEditText.getText().toString();
        String toShipmentDate = mToShipDateEditText.getText().toString();

        /*if(TextUtils.isEmpty(tonnage) && TextUtils.isEmpty(no_of_vehicles)) {
            Utils.toast("Unsuccessfull! Enter either tonnage or number of vehicles.");
            mSubmitButton.setClickable(true);
            return;
        }*/

        /*if(getIntent().getExtras() == null) {*/
        if(!bIsUpdate) {
            // means this is new requirement
            RequirementRequest requirementRequest = new RequirementRequest(mClientId, fromShipmentDate,
                    toShipmentDate, mFromCityId, mToCityId, mAahoOfficeId, tonnage, no_of_vehicles,
                    material, mVehicleTypeId, rate, remark, new RequirementListener());
            queue(requirementRequest, true);
        } else {
            // means we have to update the data
            mFromShipDate = mFromShipDateEditText.getText().toString();
            if(mToShipDateEditText.getText() == null || mToShipDateEditText.getText().toString().equalsIgnoreCase("")) {
                mToShipDate = null;
            } else {
                mToShipDate = mToShipDateEditText.getText().toString();
            }

            // Set the cancel reason
            cancelReason = tvCancelReason.getText().toString();

            String reqStatus = getIntent().getExtras().getString("reqStatus");
            if(!TextUtils.isEmpty(reqStatus)) {
                if (reqStatus.equalsIgnoreCase("lapsed")) {
                    if (!cbFullfilled.isChecked() && !cbCancelled.isChecked()) {
                        Utils.toast("Please select field either Fullfilled or Cancelled!");
                        mSubmitButton.setClickable(true);
                        return;
                    }
                }
            }

            RequirementUpdateRequest requirementUpdateRequest = new RequirementUpdateRequest(
                    mReqId,mClientId, mFromShipDate,mToShipDate, mFromCityId, mToCityId,
                    mAahoOfficeId, tonnage, no_of_vehicles,
                    material, mVehicleTypeId, rate, remark, cbIsVerified.isChecked(), cbFullfilled.isChecked(),
                    cbCancelled.isChecked(), cancelReason, new RequirementUpdateListener());
            queue(requirementUpdateRequest, true);
        }
    }

    private class RequirementListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            try{
                if(response.getString("status").equalsIgnoreCase("success")){
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
                    Utils.toast("Inquiry is submitted successfully!");
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
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);
            dismissProgress();
            mSubmitButton.setClickable(true);
            try {
                if (error != null && error.networkResponse != null
                        && error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    JSONObject errorData = new JSONObject(errorMsg);
                    Utils.showInfoDialog(RequirementActivity.this,
                            Utils.getRequestMessage(errorData),Utils.getRequestData(errorData));
                    Log.i(TAG, errorMsg);
                }
            } catch (UnsupportedEncodingException ex) {
                Log.e(TAG,"UnsupportedEncodingException = "+ex.getLocalizedMessage());
            } catch (Exception ex) {
                Log.e(TAG,"Exception = "+ex.getLocalizedMessage());
            }
        }
    }

    private class RequirementUpdateListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            try{
                if(response.getString("status").equalsIgnoreCase("success")){
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
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);
            dismissProgress();
            mSubmitButton.setClickable(true);
            try {
                if (error != null && error.networkResponse != null
                        && error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    JSONObject errorData = new JSONObject(errorMsg);
                    Utils.showInfoDialog(RequirementActivity.this,
                            Utils.getRequestMessage(errorData),Utils.getRequestData(errorData));
                    Log.i(TAG, errorMsg);
                }
            } catch (UnsupportedEncodingException ex) {
                Log.e(TAG,"UnsupportedEncodingException = "+ex.getLocalizedMessage());
            } catch (Exception ex) {
                Log.e(TAG,"Exception = "+ex.getLocalizedMessage());
            }
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
            imgClearFromDate.setVisibility(View.VISIBLE);
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
            imgClearToDate.setVisibility(View.VISIBLE);
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
            setReasonText(bundle.getString("cancelReason"));

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

            String reqStatus = bundle.getString("reqStatus");

            if(bundle.getString("context").equals("CustomerLoads")){
                cbIsVerified.setVisibility(View.VISIBLE);
                if(reqStatus.equals("open")){
                    cbIsVerified.setChecked(true);
                }
            }
            if(bundle.getString("context").equals("MyLoads")){
                cbCancelled.setVisibility(View.VISIBLE);
                cbFullfilled.setVisibility(View.VISIBLE);
                txtStatus.setVisibility(View.VISIBLE);
                if(reqStatus.equals("cancelled")){
                    cbCancelled.setChecked(true);
                }
                if(reqStatus.equals("fulfilled")){
                    cbFullfilled.setChecked(true);
                }
                if(reqStatus.equals("open")){
                    cbIsVerified.setChecked(true);
                }
            }

            if(bundle.getBoolean("rdOnlyStatus")){
                disableRequirementForm();
            }

            if(reqStatus.equalsIgnoreCase("lapsed")) {
                // Lapsed inquiry's status can be changed to fulfilled or cancelled.
                cbCancelled.setEnabled(true);
                cbFullfilled.setEnabled(true);
                mSubmitButton.setEnabled(true);
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
        txtStatus.setEnabled(false);

        imgClearClient.setEnabled(false);
        imgClearFromDate.setEnabled(false);
        imgClearToDate.setEnabled(false);
        imgClearFromCity.setEnabled(false);
        imgClearToCity.setEnabled(false);
        imgClearAahoOffice.setEnabled(false);
        imgClearTonnage.setEnabled(false);
        imgClearNoOfVehicles.setEnabled(false);
        imgClearMaterial.setEnabled(false);
        imgClearVehicleType.setEnabled(false);
        imgClearRate.setEnabled(false);
        imgClearRemark.setEnabled(false);

        imgClearClient.setVisibility(View.INVISIBLE);
        imgClearFromDate.setVisibility(View.INVISIBLE);
        imgClearToDate.setVisibility(View.INVISIBLE);
        imgClearFromCity.setVisibility(View.INVISIBLE);
        imgClearToCity.setVisibility(View.INVISIBLE);
        imgClearAahoOffice.setVisibility(View.INVISIBLE);
        imgClearTonnage.setVisibility(View.INVISIBLE);
        imgClearNoOfVehicles.setVisibility(View.INVISIBLE);
        imgClearMaterial.setVisibility(View.INVISIBLE);
        imgClearVehicleType.setVisibility(View.INVISIBLE);
        imgClearRate.setVisibility(View.INVISIBLE);
        imgClearRemark.setVisibility(View.INVISIBLE);
    }

    public class DecimalDigitsInputFilter implements InputFilter {

        private Pattern mPattern;

        private final Pattern mFormatPattern = Pattern.compile("\\d+\\.\\d+");

        public DecimalDigitsInputFilter(int digitsBeforeDecimal, int digitsAfterDecimal) {
            mPattern = Pattern.compile(
                    "^\\d{0," + digitsBeforeDecimal + "}([\\.,](\\d{0," + digitsAfterDecimal +
                            "})?)?$");
        }

        @Override
        public CharSequence filter(CharSequence source, int start, int end, Spanned dest,
                                   int dstart, int dend) {

            String newString =
                    dest.toString().substring(0, dstart) + source.toString().substring(start, end)
                            + dest.toString().substring(dend, dest.toString().length());

            Matcher matcher = mPattern.matcher(newString);
            if (!matcher.matches()) {
                return "";
            }
            return null;
        }
    }


    private void makeAutoFillDataReq() {
        SmeDataRequest smeDataRequest = new SmeDataRequest(mClientId,new AutoFillDataListener());
        queue(smeDataRequest,true);
    }

    private class AutoFillDataListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            try{
                if(response != null)
                    if(response.getString("status").equalsIgnoreCase("success")){
                        JSONObject data = response.getJSONObject("data");
                        if(data != null) {
                            if(data.has("aaho_office") && data.has("aaho_office_branch")) {
                                JSONObject aahoOfficeData = data.getJSONObject("aaho_office_branch");
                                if(aahoOfficeData != null) {
                                    String aahoOffice = Utils.get(aahoOfficeData, "branch_name");
                                    aahoOffice_autoComplete.setText(aahoOffice);
                                    String aahoofficeId = Utils.get(data, "aaho_office");
                                    if (!TextUtils.isEmpty(aahoofficeId) &&
                                            !aahoofficeId.equalsIgnoreCase("null")) {
                                        mAahoOfficeId = Integer.valueOf(aahoofficeId);
                                    }
                                }
                            }
                            if(data.has("material")) {
                                mMaterialEditText.setText(Utils.get(data,"material"));
                            }
                        }
                    } else {
                        Utils.toast("Unsuccessful! " + response.get("msg"));
                    }
            } catch (JSONException e) {
                e.printStackTrace();
                toast("error reading response data:\n" );
            }
        }

        @Override
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);
            dismissProgress();
            mSubmitButton.setClickable(true);
            try {
                if (error != null && error.networkResponse != null
                        && error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    JSONObject errorData = new JSONObject(errorMsg);
                    Utils.showInfoDialog(RequirementActivity.this,
                            Utils.getRequestMessage(errorData),Utils.getRequestData(errorData));
                    Log.i(TAG, errorMsg);
                }
            } catch (UnsupportedEncodingException ex) {
                Log.e(TAG,"UnsupportedEncodingException = "+ex.getLocalizedMessage());
            } catch (Exception ex) {
                Log.e(TAG,"Exception = "+ex.getLocalizedMessage());
            }
        }
    }


    private void makeReasonListDataReq() {
        ReasonListDataRequest reasonListDataRequest = new ReasonListDataRequest(
                new ReasonListDataListener());
        queue(reasonListDataRequest,true);
    }

    private class ReasonListDataListener extends ApiResponseListener {
        @TargetApi(Build.VERSION_CODES.JELLY_BEAN_MR1)
        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            try {
                if(response != null)
                    if(response.getString("status").equalsIgnoreCase("success")){
                        JSONObject data = response.getJSONObject("data");
                        if(data != null) {
                            for (int i = 0; i < data.names().length(); i++) {
                                String id = data.names().getString(i);
                                reasonList.add(data.getString(id));
                            }

                            if(reasonList.size() > 0) {
                                // Add other option in current list if user wants to enter
                                // another of predefined reason
                                reasonList.add("Other");
                                showReasonListDialog();
                            }
                        }
                    } else {
                        Utils.toast("Unsuccessful! " + response.get("msg"));
                    }
            } catch (JSONException e) {
                e.printStackTrace();
                Utils.toast("error reading response data:" );
            }
        }

        @Override
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);
            dismissProgress();
            mSubmitButton.setClickable(true);
            try {
                if (error != null && error.networkResponse != null
                        && error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    JSONObject errorData = new JSONObject(errorMsg);
                    Utils.showInfoDialog(RequirementActivity.this,
                            Utils.getRequestMessage(errorData),Utils.getRequestData(errorData));
                    Log.i(TAG, errorMsg);
                }
            } catch (UnsupportedEncodingException ex) {
                Log.e(TAG,"UnsupportedEncodingException = "+ex.getLocalizedMessage());
            } catch (Exception ex) {
                Log.e(TAG,"Exception = "+ex.getLocalizedMessage());
            }
        }
    }

    /** Show reason list dialog to pick one of the reason */
    @TargetApi(Build.VERSION_CODES.JELLY_BEAN_MR1)
    private void showReasonListDialog() {
        AlertDialog.Builder alertbox = new AlertDialog.Builder(this);
        String[] array = new String[reasonList.size()];
        reasonList.toArray(array); // fill the array
        alertbox.setTitle("Pick one reason")
                .setItems(array, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int pos) {
                        //pos will give the selected item position
                        String reasonText = reasonList.get(pos);
                        if(reasonText.equalsIgnoreCase("Other")) {
                            // Open dialog to enter some other text
                            showReasonEditDialog();
                        } else {
                            setReasonText(reasonList.get(pos));
                        }
                    }
                })
                .setOnDismissListener(new DialogInterface.OnDismissListener() {
                    @Override
                    public void onDismiss(DialogInterface dialogInterface) {
                        if(TextUtils.isEmpty(tvCancelReason.getText())
                                && !isReasonEditDialogShowing) {
                            cbCancelled.setChecked(false);
                        }
                    }
                });
        alertbox.show();
    }

    /** Show edit text alert dialog to enter the custom reason */
    public void showReasonEditDialog() {
        isReasonEditDialogShowing = true;
        AlertDialog.Builder alertbox = new AlertDialog.Builder(this);
        LinearLayout ll_alert_layout = new LinearLayout(this);
        ll_alert_layout.setOrientation(LinearLayout.VERTICAL);
        final EditText ed_input = new EditText(this);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.setMargins(15, 0, 15, 0);
        ed_input.setLayoutParams(lp);
        ed_input.setMaxLines(1);
        InputFilter[] filterArray = new InputFilter[1];
        filterArray[0] = new InputFilter.LengthFilter(20);
        ed_input.setFilters(filterArray);
        ll_alert_layout.addView(ed_input);

        alertbox.setTitle(getString(R.string.app_name));
        alertbox.setMessage("Enter reason");
        alertbox.setCancelable(false);
        //setting linear layout to alert dialog
        alertbox.setView(ll_alert_layout);

        alertbox.setNegativeButton("CANCEL",
                new DialogInterface.OnClickListener() {

                    public void onClick(DialogInterface arg0, int arg1) {
                        // will automatically dismiss the dialog and will do nothing
                        if(TextUtils.isEmpty(tvCancelReason.getText())) {
                            cbCancelled.setChecked(false);
                        }
                        isReasonEditDialogShowing = false;
                    }
                });

        alertbox.setPositiveButton("OK",
                new DialogInterface.OnClickListener() {

                    public void onClick(DialogInterface arg0, int arg1) {
                        // set input text to reason textView
                        String input_text = ed_input.getText().toString();
                        if(TextUtils.isEmpty(input_text)) {
                            Utils.toast("Reason can not be left blank!");
                            cbCancelled.setChecked(false);
                        } else {
                            setReasonText(input_text);
                        }
                        isReasonEditDialogShowing = false;
                    }
                });
        alertbox.show();
    }

    private void setReasonText(String reasonText) {
        if(TextUtils.isEmpty(reasonText)) {
            tvCancelReason.setText("");
            tvCancelReason.setVisibility(View.INVISIBLE);
            cbCancelled.setChecked(false);
        } else {
            tvCancelReason.setText(reasonText);
            tvCancelReason.setVisibility(View.VISIBLE);
            cbCancelled.setChecked(true);
        }
    }


}