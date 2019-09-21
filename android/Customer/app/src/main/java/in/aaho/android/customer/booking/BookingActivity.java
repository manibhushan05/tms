package in.aaho.android.customer.booking;

import android.content.DialogInterface;
import android.os.Bundle;
import android.support.v7.app.AlertDialog;
import android.support.v7.widget.DefaultItemAnimator;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.TextView;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import in.aaho.android.customer.common.ApiResponseListener;
import in.aaho.android.customer.common.BaseActivity;
import in.aaho.android.customer.common.ListItemListerner;
import in.aaho.android.customer.R;
import in.aaho.android.customer.requests.NewBookingRequest;
import in.aaho.android.customer.requests.VendorRequest;


public class BookingActivity extends BaseActivity {

    private Button submitButton;
    private Button resetButton;
    private Button shipAddButton;

    private EditText contactNameEditText;
    private EditText contactPhoneEditText;
    private EditText materialEditText;
    private EditText rateEditText;

    private TextView noShipTextView;

    private CheckBox termsCheckBox;
    private TextView termsOpenTextView;

    private RecyclerView pickupContainer;
    private RecyclerView dropContainer;
    private RecyclerView shipContainer;
    private RecyclerView customShipContainer;

    private List<PickupForm> pickupForms = new ArrayList<>();
    private List<DropForm> dropForms = new ArrayList<>();
    private List<Shipment> displayShipList = new ArrayList<>();
    private List<Shipment> shipments = new ArrayList<>();
    private List<Vendor> vendorList = new ArrayList<>();
    private List<CustomShipment> customShipments = new ArrayList<>();
    private List<CustomShipment> displayCustomShipList = new ArrayList<>();

    private PickupAdapter pickupAdapter;
    private DropAdapter dropAdapter;
    private ShipAdapter shipAdapter;
    private CustomShipAdapter customShipAdapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.booking_activity);

        setToolbarTitle("New Booking");

        setViewVariables();
        setClickListeners();
        setupAdapters();

        contactNameEditText.setText(App.userFullName == null ? "" : App.userFullName);
        contactPhoneEditText.setText(App.userPhone == null ? "" : App.userPhone);
        updateDisplayShipmentsTotal();
    }

    private void setupAdapters() {
        setupPickupAdapter();
        setupDropAdapter();
        setupShipAdapter();
        setupCustomShipAdapter();
        setupVendorAdapter();
    }

    private void setupPickupAdapter() {
        pickupAdapter = new PickupAdapter(pickupForms, this);
        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getApplicationContext());
        pickupContainer.setLayoutManager(mLayoutManager);
        pickupContainer.setItemAnimator(new DefaultItemAnimator());
        pickupContainer.setAdapter(pickupAdapter);
        pickupContainer.setNestedScrollingEnabled(false);

        pickupForms.add(new PickupForm());
        pickupAdapter.notifyItemInserted(pickupForms.size() - 1);
    }

    private void setupDropAdapter() {
        dropAdapter = new DropAdapter(dropForms, this);
        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getApplicationContext());
        dropContainer.setLayoutManager(mLayoutManager);
        dropContainer.setItemAnimator(new DefaultItemAnimator());
        dropContainer.setAdapter(dropAdapter);
        dropContainer.setNestedScrollingEnabled(false);

        dropForms.add(new DropForm());
        dropAdapter.notifyItemInserted(dropForms.size() - 1);
    }

    private void setupShipAdapter() {
        shipAdapter = new ShipAdapter(displayShipList);
        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getApplicationContext());
        shipContainer.setLayoutManager(mLayoutManager);
        shipContainer.setItemAnimator(new DefaultItemAnimator());
        shipContainer.setAdapter(shipAdapter);
        shipContainer.setNestedScrollingEnabled(false);

        shipments = getAllShipmentOptionsFromServer();
    }

    private void setupCustomShipAdapter() {
        customShipAdapter = new CustomShipAdapter(displayCustomShipList);
        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getApplicationContext());
        customShipContainer.setLayoutManager(mLayoutManager);
        customShipContainer.setItemAnimator(new DefaultItemAnimator());
        customShipContainer.setAdapter(customShipAdapter);
        customShipContainer.setNestedScrollingEnabled(false);

    }

    private void setupVendorAdapter() {
        vendorList = Vendor.getAll();
    }

    private List<Shipment> getAllShipmentOptionsFromServer() {
        List<Shipment> shipList = new ArrayList<>();
        List<VehicleCategory> vehicleCategoryList = VehicleCategory.getAll();

        for (VehicleCategory vehicleCategory : vehicleCategoryList) {
            shipList.add(new Shipment(vehicleCategory.id, vehicleCategory.getFullName()));
        }
        return shipList;
    }

    public void updateAllDisplayShipments() {
        updateDisplayShipments();
        updateDisplayCustomShipments();
        updateDisplayShipmentsTotal();
    }

    private void updateDisplayShipments() {
        displayShipList.clear();
        for (Shipment ship : shipments) {
            if (ship.getCount() > 0) {
                displayShipList.add(ship);
            }
        }
        shipAdapter.notifyDataSetChanged();
    }

    private void updateDisplayCustomShipments() {
        displayCustomShipList.clear();
        for (CustomShipment ship : customShipments) {
            if (ship.getCount() > 0) {
                displayCustomShipList.add(ship);
            }
        }
        customShipAdapter.notifyDataSetChanged();
    }

    private void updateDisplayShipmentsTotal() {
        int totalShips = displayShipList.size() + displayCustomShipList.size();
        noShipTextView.setVisibility(totalShips == 0 ? View.VISIBLE : View.GONE);
        shipAddButton.setText(totalShips == 0 ? R.string.add_shipment : R.string.edit_shipment);
    }

    private void setViewVariables() {
        submitButton = (Button) findViewById(R.id.submit_btn);
        resetButton = (Button) findViewById(R.id.reset_form_btn);
        shipAddButton = (Button) findViewById(R.id.more_ship_btn);
        noShipTextView = (TextView) findViewById(R.id.no_ship_message);

        contactNameEditText = (EditText) findViewById(R.id.other_details_name_edit_text);
        contactPhoneEditText = (EditText) findViewById(R.id.other_details_phone_edit_text);
        materialEditText = (EditText) findViewById(R.id.other_details_material_edit_text);
        rateEditText = (EditText) findViewById(R.id.other_details_rate_edit_text);

        pickupContainer = (RecyclerView) findViewById(R.id.pickup_container);
        dropContainer = (RecyclerView) findViewById(R.id.drop_container);
        shipContainer = (RecyclerView) findViewById(R.id.ship_container);
        customShipContainer = (RecyclerView) findViewById(R.id.custom_ship_container);

        termsCheckBox = (CheckBox) findViewById(R.id.booking_terms_checkbox);
        termsOpenTextView = (TextView) findViewById(R.id.booking_terms_open_btn);
    }

    private void setClickListeners() {
        submitButton.setOnClickListener(new SubmitClickListener());
        shipAddButton.setOnClickListener(new AddShipClickListener());
        resetButton.setOnClickListener(new ResetClickListener());
        termsOpenTextView.setOnClickListener(new OpenTermsDialogListener());
    }

    private class OpenTermsDialogListener implements View.OnClickListener {
        @Override
        public void onClick(View v) {
            showTermsDialog();
        }
    }

    void showTermsDialog() {
        TermsDialogFragment dialogFragment = new TermsDialogFragment();
        dialogFragment.show(this.getSupportFragmentManager(), "tnc_dialog");
    }

    private class ResetClickListener implements View.OnClickListener {
        @Override
        public void onClick(View v) {
            showResetAlert();
        }
    }

    private void resetFormVariables() {
        contactNameEditText.setText("");
        contactPhoneEditText.setText("");
        materialEditText.setText("");
        rateEditText.setText("");

        termsCheckBox.setChecked(false);

        pickupForms.clear();
        pickupForms.add(new PickupForm());
        pickupAdapter.notifyDataSetChanged();

        dropForms.clear();
        dropForms.add(new DropForm());
        dropAdapter.notifyDataSetChanged();

        for (Shipment ship : shipments) {
            ship.setCount(0);
        }
        customShipments.clear();
        updateAllDisplayShipments();

        for (Vendor v : vendorList) {
            v.setSelected(false);
        }
    }

    private class SubmitClickListener implements View.OnClickListener {
        @Override
        public void onClick(View v) {
            submitBookingForm();
        }
    }

    public void showVendorDialog(long bookingId) {
        VendorDialogFragment vendorDialogFragment = new VendorDialogFragment();
        vendorDialogFragment.setVendors(vendorList);
        vendorDialogFragment.setBookingActivity(this);
        vendorDialogFragment.setBookingId(bookingId);
        vendorDialogFragment.show(this.getSupportFragmentManager(), "vendor_select_dialog");
    }

    public void submitBookingForm() {
        List<PickupForm> toSubmitPickups = filteredPickups();
        List<DropForm> toSubmitDrops = filteredDrops();
        List<Shipment> toSubmitShips = filteredShipment();
        List<CustomShipment> toSubmitCustomShips = filteredCustomShipment();

        List<String> errors = checkFormValidity(toSubmitPickups, toSubmitDrops, toSubmitShips, toSubmitCustomShips);

        String personName = App.nullToBlank(contactNameEditText.getText().toString());
        String personPhone = App.nullToBlank(contactPhoneEditText.getText().toString());
        String material = App.nullToBlank(materialEditText.getText().toString());
        String rate = App.nullToBlank(rateEditText.getText().toString());
        List<String> other_errors = checkOtherDetailsValidity(personName, personPhone);

        errors.addAll(other_errors);

        if (errors.size() == 0) {
            if (!termsCheckBox.isChecked()) {
                errors.add("You must accept the Terms and Conditions to continue");
            }
        }

        if (errors.size() == 0) {
            JSONObject formData = getBookingJson(toSubmitPickups, toSubmitDrops, toSubmitShips,
                    toSubmitCustomShips, personName, personPhone, material, rate);
            sendBookingRequest(formData);
        } else {
            showBookingFormErrors(errors);
        }
    }

    private List<String> checkOtherDetailsValidity(String personName, String personPhone) {
        List<String> errors = new ArrayList<>();
        if (personName == null || personName.trim().length() == 0) {
            errors.add("Contact Person Name must be provided");
        }
        if (personPhone == null || personPhone.trim().length() == 0) {
            errors.add("Contact Person Phone Number must be provided");
        }
        return errors;
    }

    private void sendBookingRequest(JSONObject formData) {
        try {
            Log.e("[SubmitBooking - send]", formData.toString(4));
        } catch (JSONException e) {
            e.printStackTrace();
        }
        NewBookingRequest bookingRequest = new NewBookingRequest(formData, new NewBookingListener());
        queue(bookingRequest);
    }

    private void sendVendorRequest(JSONObject formData) {
        try {
            Log.e("[SubmitVendorRequest]", formData.toString(4));
        } catch (JSONException e) {
            e.printStackTrace();
        }
        VendorRequest vendorRequest = new VendorRequest(formData, new VendorRequestListener());
        queue(vendorRequest);
    }


    public void submitVendorRequestForm(long bookingId) {
        List<Vendor> toSubmitVendors = filteredVendors();
        if (toSubmitVendors.size() == 0) {
            return;
        }
        JSONObject formData = getVendorJson(bookingId, toSubmitVendors);
        sendVendorRequest(formData);
    }

    private JSONObject getVendorJson(long bookingId, List<Vendor> toSubmitVendors) {
        List<JSONObject> vendors = new ArrayList<>();

        for (Vendor v: toSubmitVendors) {
            vendors.add(v.toJson());
        }

        JSONObject data = new JSONObject();
        try {
            data.put("vendors", new JSONArray(vendors));
            data.put("booking_id", bookingId);
        } catch (JSONException e) {
            e.printStackTrace();
        }

        return data;
    }


    private void showResultDialog(long bookingId) {
        BookingResultDialogFragment resFragment = new BookingResultDialogFragment();
        resFragment.setBookingActivity(this);
        resFragment.setBookingId(bookingId);
        resFragment.show(this.getSupportFragmentManager(), "booking_result_dialog");
    }

    private JSONObject getBookingJson(List<PickupForm> toSubmitPickups, List<DropForm> toSubmitDrops,
                                      List<Shipment> toSubmitShips, List<CustomShipment> toSubmitCustomShips,
                                      String personName, String personPhone, String material, String rate) {
        List<JSONObject> pickups = new ArrayList<>();
        List<JSONObject> drops = new ArrayList<>();
        List<JSONObject> ships = new ArrayList<>();

        for (PickupForm p: toSubmitPickups) {
            pickups.add(p.toJson());
        }
        for (DropForm p: toSubmitDrops) {
            drops.add(p.toJson());
        }
        for (Shipment p: toSubmitShips) {
            ships.add(p.toJson());
        }
        for (CustomShipment p: toSubmitCustomShips) {
            ships.add(p.toJson());
        }

        Date shipDate = toSubmitPickups.get(0).getDatetime();

        JSONObject data = new JSONObject();
        try {
            data.put("pickups", new JSONArray(pickups));
            data.put("drops", new JSONArray(drops));
            data.put("vehicles", new JSONArray(ships));
            data.put("contact_person", personName == null ? JSONObject.NULL : personName);
            data.put("contact_number", personPhone == null ? JSONObject.NULL : personPhone);
            data.put("material", material == null ? JSONObject.NULL : material);
            data.put("rate", rate == null ? JSONObject.NULL : rate);
            data.put("shipment_datetime", shipDate == null ? JSONObject.NULL : shipDate);
        } catch (JSONException e) {
            e.printStackTrace();
        }

        return data;
    }

    private void showBookingFormErrors(List<String> errors) {
        String errorMsg = "";
        for (String e : errors) {
            Log.e("[BookingFormError]", e);
            errorMsg = errorMsg + " - " + e + "\n";
        }
        new AlertDialog.Builder(this)
                .setTitle("Errors")
                .setMessage(errorMsg)
                .setPositiveButton(android.R.string.ok, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                    }
                })
                .show();
    }

    private List<String> checkFormValidity(List<PickupForm> toSubmitPickups, List<DropForm> toSubmitDrops, List<Shipment> toSubmitShips, List<CustomShipment> toSubmitCustomShips) {
        List<String> errors = new ArrayList<>();
        errors.addAll(checkPickupFormValidity(toSubmitPickups));
        errors.addAll(checkDropFormValidity(toSubmitDrops));
        errors.addAll(checkShipmentValidity(toSubmitShips, toSubmitCustomShips));
        return errors;
    }

    private List<String> checkPickupFormValidity(List<PickupForm> toSubmitPickups) {
        List<String> errors = new ArrayList<>();
        if (toSubmitPickups.size() == 0) {
            errors.add("At least one pickup point is required");
        } else {
            boolean allComplete = true;
            for (PickupForm p : toSubmitPickups) {
                if (!p.isComplete()) {
                    allComplete = false;
                    break;
                }
            }
            if (toSubmitPickups.get(0).getDatetime() == null) {
                allComplete = false;
            }
            if (!allComplete) {
                errors.add("All fields in the pickup form are required");
            }
        }
        return errors;
    }

    private List<String> checkDropFormValidity(List<DropForm> toSubmitDrops) {
        List<String> errors = new ArrayList<>();
        if (toSubmitDrops.size() == 0) {
            errors.add("At least one drop point is required");
        } else {
            boolean allComplete = true;
            for (DropForm p : toSubmitDrops) {
                if (!p.isComplete()) {
                    allComplete = false;
                    break;
                }
            }
            if (!allComplete) {
                errors.add("All fields in the drop form are required");
            }
        }
        return errors;
    }

    private List<String> checkShipmentValidity(List<Shipment> toSubmitShips, List<CustomShipment> toSubmitCustomShips) {
        List<String> errors = new ArrayList<>();
        if (toSubmitShips.size() + toSubmitCustomShips.size() == 0) {
            errors.add("At least one shipment option must be selected");
        }
        return errors;
    }

    private List<Vendor> filteredVendors() {
        List<Vendor> filtered = new ArrayList<>();
        for (Vendor v : vendorList) {
            if (v.isSelected()) {
                filtered.add(v);
            }
        }
        return filtered;
    }

    private List<Shipment> filteredShipment() {
        return displayShipList;
    }

    private List<CustomShipment> filteredCustomShipment() {
        return displayCustomShipList;
    }

    private List<PickupForm> filteredPickups() {
        List<PickupForm> filtered = new ArrayList<>();
        for (PickupForm p : pickupForms) {
            if (!p.isAllBlank()) {
                filtered.add(p);
            }
        }
        return filtered;
    }

    private List<DropForm> filteredDrops() {
        List<DropForm> filtered = new ArrayList<>();
        for (DropForm p : dropForms) {
            if (!p.isAllBlank()) {
                filtered.add(p);
            }
        }
        return filtered;
    }

    private class AddShipClickListener extends ListItemListerner implements View.OnClickListener {

        @Override
        public void onClick(View v) {
            showShipDialog();
        }
    }

    void showShipDialog() {
        ShipmentDialogFragment shipmentDialog = new ShipmentDialogFragment();
        shipmentDialog.setShipments(shipments);
        shipmentDialog.setCustomShipments(customShipments);
        shipmentDialog.setBookingActivity(this);
        shipmentDialog.show(this.getSupportFragmentManager(), "shipment_dialog");
    }

    private class VendorRequestListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            Log.e("[VendorRequest success]", response.toString());
            showVendorRequestSuccessDialog();
        }

        @Override
        public void onError() {
            dismissProgress();
        }
    }

    private void showVendorRequestSuccessDialog() {
        new AlertDialog.Builder(this)
                .setTitle("Success")
                .setMessage("Successfully sent request to vendors")
                .setPositiveButton(android.R.string.ok, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                    }
                })
                .show();
    }

    private class NewBookingListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            Log.e("[booking success]", response.toString());
            try {
                long bookingId = response.getLong("booking_id");
                App.updateAppData(response);
                resetFormVariables();
                showResultDialog(bookingId);
            } catch (JSONException e) {
                e.printStackTrace();
                toast("something went wrong, no booking_id returned by server");
            }
        }

        @Override
        public void onError() {
            dismissProgress();
        }
    }

    @Override
    public void onBackPressed() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);

        builder.setTitle("Back to dashboard?");
        builder.setMessage("All the booking form information you have entered so far will be discarded");
        builder.setPositiveButton("Stay", new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int id) {

            }
        });
        builder.setNegativeButton("Discard", new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int id) {
                BookingActivity.super.onBackPressed();
            }
        });
        builder.show();
    }

    private void showResetAlert() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);

        builder.setTitle("Clear all form data?");
        builder.setMessage("All form data entered will be discarded");
        builder.setPositiveButton("Cancel", new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int id) {

            }
        });
        builder.setNegativeButton("Reset", new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int id) {
                resetFormVariables();
            }
        });
        builder.show();
    }

    @Override
    protected void onResume() {
        super.onResume();
        App.setFromSharedPreferencesIfNeeded();
    }
}
