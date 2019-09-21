package in.aaho.android.aahocustomers.vehicles;

import android.content.DialogInterface;
import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AlertDialog;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.Spinner;
import android.widget.TextView;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.aahocustomers.R;
import in.aaho.android.aahocustomers.booking.App;
import in.aaho.android.aahocustomers.common.ApiResponseListener;
import in.aaho.android.aahocustomers.common.BaseActivity;
import in.aaho.android.aahocustomers.requests.VehicleAddEditRequest;
import in.aaho.android.aahocustomers.requests.VehicleDetailsRequest;
import in.aaho.android.aahocustomers.transaction.TransactionActivity;

/**
 * Created by mani on 10/10/16.
 */

public class VehicleDetailsActivity extends BaseActivity {
    public static final String[] VEHICLE_STATUS_LIST = new String[] {
            "unloading", "loading", "unloaded", "loaded"
    };
    private AdapterView.OnItemSelectedListener statusSelectListener;

    public static int statusIndex(String status) {
        int pos = -1;
        for (int i = 0; i < VEHICLE_STATUS_LIST.length; i++) {
            if (VEHICLE_STATUS_LIST[i].equals(status)) {
                pos = i;
                break;
            }
        }
        return pos;
    }

    private TextView vehicleNumberView, vehicleModelView, vehicleLocationView;
    private Spinner vehicleStatusView;
    private TextView vehicleOwnerView, vehicleDriverView;
    private LinearLayout vehicleOwnerBtn, vehicleDriverBtn, vehicleDocsBtn, vehicleTripsBtn;

    private Button saveButton;

    public static int position;
    public static long vehicleId;
    public static BrokerVehicle vehicle;

    public static BrokerVehicleDetails brokerVehicleDetails = null;
    private LinearLayout editButton;

    private boolean hasOwnerChanged = false;
    private boolean hasDriverChanged = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.vehicle_details_activity);

        setToolbarTitle("Vehicle Details");

        setViewVariables();
        setClickListeners();
        setupAdapters();

        updateVehicle();
        loadDataFromServer();
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        updateVehicle();
        loadDataFromServer();
    }

    @Override
    protected void onResume() {
        super.onResume();
        Log.e("Details", "onResume");
        App.setFromSharedPreferencesIfNeeded();
    }

    private void updateVehicle() {
        vehicle = VehicleListActivity.getVehicleList().get(position);
        vehicleId = vehicle.getId();
    }

    private void setupAdapters() {
        ArrayAdapter<String> adapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, VEHICLE_STATUS_LIST);
        // Specify the layout to use when the list of choices appears
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        // Apply the adapter to the spinner
        vehicleStatusView.setAdapter(adapter);
    }

    private void setClickListeners() {
        /** NOTE: Now we are not allowing user to change the owner/driver */
        /*vehicleDriverBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showDriverSelectDialog();
            }
        });*/
        /*vehicleOwnerBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showOwnerSelectDialog();
            }
        });*/
        vehicleDocsBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (brokerVehicleDetails != null) {
                    Intent intent = new Intent(VehicleDetailsActivity.this, VehicleDocumentsActivity.class);
                    startActivity(intent);
                }
            }
        });
        vehicleTripsBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                //startActivity(new Intent(VehicleDetailsActivity.this, VehicleTripActivity.class));
                Bundle bundle = new Bundle();
                bundle.putString("VehicleId", String.valueOf(vehicleId));
                Intent intent = new Intent(VehicleDetailsActivity.this, TransactionActivity.class);
                intent.putExtras(bundle);
                startActivity(intent);
            }
        });
        saveButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                sendVehicleEditRequest();

                /*String msg = "For Vehicle No. " + brokerVehicleDetails.getNumber() + " ," +
                        "\nDo you want to allocate,";
                if(hasDriverChanged) {
                    msg = msg + "\nDriver : "+brokerVehicleDetails.vehicleDriver.name;
                }
                if(hasOwnerChanged) {
                    msg = msg + "\nOwner : "+brokerVehicleDetails.vehicleOwner.name;
                }

                Utils.showAlertDialog(VehicleDetailsActivity.this,
                        "Vehicle Details",msg,
                        "Yes", "No", new Utils.AlertDialogListener() {
                            @Override
                            public void onPositiveButtonClicked() {
                                sendVehicleEditRequest();
                            }

                            @Override
                            public void onNegativeButtonClicked() {

                            }
                        });*/
            }
        });
        editButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showVehicleEditDialog();
            }
        });
        statusSelectListener = new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                String newStatus = VEHICLE_STATUS_LIST[position];
                if (brokerVehicleDetails != null) {
                    if (!newStatus.equals(brokerVehicleDetails.status)) {
                        brokerVehicleDetails.status = newStatus;
                        enableSave();
                    }
                }
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {

            }
        };
        vehicleStatusView.setOnItemSelectedListener(statusSelectListener);
    }

    private void showVehicleEditDialog() {
        VehicleAddEditDialogFragment.VehicleAddEditListener listener;
        listener = new VehicleAddEditDialogFragment.VehicleAddEditListener() {
            @Override
            public void onVehicleAddEdit(BrokerVehicleDetails vehicle, boolean newVehicle) {
                updateVehicleDetails(vehicle);
            }
        };
        VehicleAddEditDialogFragment.showNewDialog(this, brokerVehicleDetails, listener);
    }

    private void updateVehicleDetails(BrokerVehicleDetails vehicle) {
        if (vehicle == null || vehicle.id == null) {
            return;
        }
        int index = -1;
        for (int i = 0; i < VehicleListActivity.getVehicleList().size(); i++) {
            BrokerVehicle brokerVehicle = VehicleListActivity.getVehicleList().get(i);
            if (brokerVehicle.getId() == vehicle.id) {
                index = i;
                break;
            }
        }

        if (index == -1) {
            Long categoryId = vehicle.category == null ? null : vehicle.category.id;
            VehicleListActivity.getVehicleList().add(new BrokerVehicle(vehicle.id, vehicle.getNumber(), vehicle.model, categoryId));
            index = VehicleListActivity.getVehicleList().size() - 1;
        }
        position = index;
        brokerVehicleDetails = vehicle;
        vehicleId = vehicle.id;
        updateUI();
    }

    private void showOwnerSelectDialog() {
        OwnerSelectDialogFragment.showNewDialog(this, new OwnerSelectDialogFragment.OwnerChangeListener() {
            @Override
            public void onChange(VehicleOwner vehicleOwner) {
                if (brokerVehicleDetails != null) {
                    if (brokerVehicleDetails.vehicleOwner == null && vehicleOwner == null) {
                        return;
                    }
                    if (brokerVehicleDetails.vehicleOwner != null && vehicleOwner != null && vehicleOwner.id == brokerVehicleDetails.vehicleOwner.id) {
                        return;
                    }
                    brokerVehicleDetails.vehicleOwner = vehicleOwner;
                    updateOwnerUI();
                    enableSave();
                    hasOwnerChanged = true;
                }
            }
        });
    }

    private void showDriverSelectDialog() {
        DriverSelectDialogFragment.showNewDialog(this, new DriverSelectDialogFragment.DriverChangeListener() {
            @Override
            public void onChange(VehicleDriver vehicleDriver) {
                if (brokerVehicleDetails != null) {
                    if (brokerVehicleDetails.vehicleDriver == null && vehicleDriver == null) {
                        return;
                    }
                    if (brokerVehicleDetails.vehicleDriver != null && vehicleDriver != null && vehicleDriver.id == brokerVehicleDetails.vehicleDriver.id) {
                        return;
                    }
                    brokerVehicleDetails.vehicleDriver = vehicleDriver;
                    updateDriverUI();
                    enableSave();
                    hasDriverChanged = true;
                }
            }
        });
    }


    private void sendVehicleEditRequest() {
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
            VehicleAddEditRequest request = new VehicleAddEditRequest(jsonObject, new VehicleDetailsEditListener());
            queue(request);
        }
    }


    private class VehicleDetailsEditListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            hideSave();
            toast("Details Saved");
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

    private void enableSave() {
        if (saveButton != null) {
            saveButton.setVisibility(View.VISIBLE);
        }
    }

    private void setViewVariables() {
        vehicleNumberView = findViewById(R.id.vehicle_details_number_tv);
        vehicleModelView = findViewById(R.id.vehicle_details_model_tv);
        vehicleLocationView = findViewById(R.id.vehicle_details_location_tv);
        vehicleStatusView = findViewById(R.id.vehicle_details_status_spinner);
        vehicleOwnerView = findViewById(R.id.vehicle_details_owner_tv);
        vehicleDriverView = findViewById(R.id.vehicle_details_driver_tv);
        vehicleOwnerBtn = findViewById(R.id.vehicle_details_owner_btn);
        vehicleDriverBtn = findViewById(R.id.vehicle_details_driver_btn);
        vehicleDocsBtn = findViewById(R.id.vehicle_details_documents_btn);
        vehicleTripsBtn = findViewById(R.id.vehicle_details_trip_history_btn);
        editButton = findViewById(R.id.vehicle_details_vehicle_edit_btn);

        saveButton = findViewById(R.id.vehicle_details_save_btn);
    }

    private void loadDataFromServer() {
        VehicleDetailsRequest appDataRequest = new VehicleDetailsRequest(vehicleId, new VehicleDetailsResponseListener());
        queue(appDataRequest);
    }

    private void updateUI() {
        vehicleNumberView.setText(brokerVehicleDetails.getNumber() == null ? "-" : brokerVehicleDetails.getNumber());
        String type = brokerVehicleDetails.getName();
        vehicleModelView.setText(type == null ? "-" : type);
        String location = brokerVehicleDetails.city == null ? null : brokerVehicleDetails.city.name;
        vehicleLocationView.setText(location == null ? "-" : location);
        int statusPos = brokerVehicleDetails.status == null ? -1 : statusIndex(brokerVehicleDetails.status);
        if (statusPos != -1) {
            vehicleStatusView.setOnItemSelectedListener(null);
            vehicleStatusView.setSelection(statusPos);
            vehicleStatusView.setOnItemSelectedListener(statusSelectListener);
        }
        updateOwnerUI();
        updateDriverUI();
    }

    private void updateOwnerUI() {
        VehicleOwner vehicleOwner = brokerVehicleDetails.vehicleOwner;
        if (vehicleOwner != null) {
            vehicleOwnerView.setText(vehicleOwner.name == null ? "-" : vehicleOwner.name);
        } else {
            vehicleOwnerView.setText("-");
        }
    }

    private void updateDriverUI() {
        VehicleDriver vehicleDriver = brokerVehicleDetails.vehicleDriver;
        if (vehicleDriver != null) {
            vehicleDriverView.setText(vehicleDriver.name == null ? "-" : vehicleDriver.name);
        } else {
            vehicleDriverView.setText("-");
        }
    }

    private class VehicleDetailsResponseListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            String resp = response.toString();
            try {
                JSONObject jsonObject = new JSONObject(resp);
                JSONObject vehiclesData = jsonObject.getJSONObject("data");
                brokerVehicleDetails = BrokerVehicleDetails.fromJson(vehiclesData);
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
        builder.setMessage("All the vehicle you have edited so far will be discarded");
        builder.setPositiveButton("Stay", new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int id) {

            }
        });
        builder.setNegativeButton("Discard", new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int id) {
                VehicleDetailsActivity.super.onBackPressed();
            }
        });
        builder.show();
    }
}
