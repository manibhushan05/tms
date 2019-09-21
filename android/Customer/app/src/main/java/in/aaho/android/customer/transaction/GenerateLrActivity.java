package in.aaho.android.customer.transaction;

import android.os.Bundle;
import android.widget.AutoCompleteTextView;

import in.aaho.android.customer.common.BaseActivity;
import in.aaho.android.customer.R;

public class GenerateLrActivity extends BaseActivity {

    private AutoCompleteTextView atvConsignorName;
    private AutoCompleteTextView atvConsignorAddress;
    private AutoCompleteTextView atvConsignorCity;
    private AutoCompleteTextView atvConsignorPin;
    private AutoCompleteTextView atvConsignorPhone;
    private AutoCompleteTextView atvConsignorCstTin;

    private AutoCompleteTextView atvConsigneeName;
    private AutoCompleteTextView atvConsigneeAddress;
    private AutoCompleteTextView atvConsigneeCity;
    private AutoCompleteTextView atvConsigneePin;
    private AutoCompleteTextView atvConsigneePhone;
    private AutoCompleteTextView atvConsigneeCstTin;

    private AutoCompleteTextView atvSourceCity;
    private AutoCompleteTextView atvDestinationCity;
    private AutoCompleteTextView atvInvoiceNumber;
    private AutoCompleteTextView atvInvoiceDate;
    private AutoCompleteTextView atvInvoiceAmount;

    private AutoCompleteTextView atvNumberOfPackage;
    private AutoCompleteTextView atvMaterial;
    private AutoCompleteTextView atvActualWeight;
    private AutoCompleteTextView atvChargedWeight;
    private AutoCompleteTextView atvRate;

    private AutoCompleteTextView atvVehicleNumber;
    private AutoCompleteTextView atvDriverName;
    private AutoCompleteTextView atvDriverPhone;
    private AutoCompleteTextView atvDriverLicence;
    private AutoCompleteTextView atvRoadPermitNumber;


    private AutoCompleteTextView atvInsuranceProvider;
    private AutoCompleteTextView atvInsurancePolicyNumber;
    private AutoCompleteTextView atvInsuranceAmount;
    private AutoCompleteTextView atvInsuranceDate;
    private AutoCompleteTextView atvInsuranceRisk;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_generate_lr);
        setToolbarTitle("Generate LR");

        setViewRefs();
    }
    private void setViewRefs(){
        atvConsignorName = (AutoCompleteTextView) findViewById(R.id.input_lr_consignor_name);
        atvConsignorAddress = (AutoCompleteTextView) findViewById(R.id.input_lr_consignor_address);
        atvConsignorCity = (AutoCompleteTextView) findViewById(R.id.input_lr_consignor_city);
        atvConsignorPin = (AutoCompleteTextView) findViewById(R.id.input_lr_consignor_pin);
        atvConsignorPhone = (AutoCompleteTextView) findViewById(R.id.input_lr_consignor_phone);
        atvConsignorCstTin = (AutoCompleteTextView) findViewById(R.id.input_lr_consignor_cst_tin);

        atvConsigneeName = (AutoCompleteTextView) findViewById(R.id.input_lr_consignee_name);
        atvConsigneeAddress = (AutoCompleteTextView) findViewById(R.id.input_lr_consignee_address);
        atvConsigneeCity = (AutoCompleteTextView) findViewById(R.id.input_lr_consignee_city);
        atvConsigneePin = (AutoCompleteTextView) findViewById(R.id.input_lr_consignee_pin);
        atvConsigneePhone = (AutoCompleteTextView) findViewById(R.id.input_lr_consignee_phone);
        atvConsigneeCstTin = (AutoCompleteTextView) findViewById(R.id.input_lr_consignee_cst_tin);

        atvSourceCity = (AutoCompleteTextView) findViewById(R.id.input_lr_source_city);
        atvDestinationCity = (AutoCompleteTextView) findViewById(R.id.input_lr_destination_city);
        atvInvoiceNumber = (AutoCompleteTextView) findViewById(R.id.input_lr_invoice_number);
        atvInvoiceDate = (AutoCompleteTextView) findViewById(R.id.input_lr_invoice_date);
        atvInvoiceAmount = (AutoCompleteTextView) findViewById(R.id.input_lr_invoice_amount);
    }

}
