package in.aaho.android.ownr.vehicles;

import android.os.Bundle;
import android.support.annotation.Nullable;
import android.text.TextUtils;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.Toast;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.ownr.common.ApiResponseListener;
import in.aaho.android.ownr.common.BaseActivity;
import in.aaho.android.ownr.common.BaseDialogFragment;
import in.aaho.android.ownr.common.InstantAutoComplete;
import in.aaho.android.ownr.common.InstantFocusListener;
import in.aaho.android.ownr.R;
import in.aaho.android.ownr.booking.City;
import in.aaho.android.ownr.booking.VehicleCategory;
import in.aaho.android.ownr.requests.VehicleAddEditRequest;

/**
 * Created by shobhit on 8/8/16.
 */

public class VehicleAddEditDialogFragment extends BaseDialogFragment {

    private Button doneButton, cancelButton;
    private EditText numberEditText, vehicleCatTypeEditText, vehicleCatCapacityEditText;
    private Spinner vehicleCategorySelect;
    private CheckBox newVehicleCategoryCheckBox;

    private CategoryArrayAdapter categoryAdapter;

    private View dialogView;

    private VehicleAddEditListener listener;

    private BrokerVehicleDetails brokerVehicleDetails;

    public static void showNewDialog(BaseActivity activity, BrokerVehicleDetails brokerVehicleDetails, VehicleAddEditListener listener) {
        VehicleAddEditDialogFragment dialog = new VehicleAddEditDialogFragment();
        dialog.setAddEditListener(listener);
        dialog.setActivity(activity);
        if (brokerVehicleDetails != null) {
            dialog.brokerVehicleDetails = BrokerVehicleDetails.copy(brokerVehicleDetails);
        } else {
            dialog.brokerVehicleDetails = new BrokerVehicleDetails();
        }
        dialog.show(activity.getSupportFragmentManager(), "vehicle_add_edit_fragment");
    }

    public void setAddEditListener(VehicleAddEditListener listener) {
        this.listener = listener;
    }

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        categoryAdapter = CategoryArrayAdapter.getNew(getActivity(), VehicleCategory.getAll(), newCategoryListener());
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        dialogView = inflater.inflate(R.layout.vehicle_add_dialog, container, false);

        setViewVariables();
        setClickListeners();
        setUpAdapters();
        updateUI();

        return dialogView;
    }

    private void setUpAdapters() {
        setUpCategorySpinner();
    }

    private CategoryArrayAdapter.CategorySelectListener newCategoryListener() {
        return new CategoryArrayAdapter.CategorySelectListener() {
            @Override
            public void onCategorySelect(VehicleCategory vehicleCategory) {
                if (vehicleCategory.id == -1) {
                    vehicleCategory = null;
                }
                brokerVehicleDetails.category = vehicleCategory;
                updateCategoryUI();
            }
        };
    }

    private void setUpCategorySpinner() {
        vehicleCategorySelect.setAdapter(categoryAdapter);
        vehicleCategorySelect.setOnItemSelectedListener(categoryAdapter);
    }

    private void updateCategoryUI() {
        if (vehicleCategorySelect != null) {
            if (brokerVehicleDetails.category != null) {
                vehicleCategorySelect.setSelection(getIndex(brokerVehicleDetails.category.id));
            } else {
                vehicleCategorySelect.setSelection(0);
            }
        }
    }

    private int getIndex(long id) {
        int index = 0;
        for (int i = 0; i < categoryAdapter.getCount(); i++) {
            VehicleCategory item = categoryAdapter.getItem(i);
            if (item == null || item.id == -1) {
                continue;
            }
            if (item.id == id) {
                index = i;
                break;
            }
        }
        return index;
    }


    private void updateNumberUI() {
        if (numberEditText != null) {
            numberEditText.setText(brokerVehicleDetails.getNumber() == null ? "" : brokerVehicleDetails.getNumber());
        }
    }


    private void updateUI() {
        updateNumberUI();
        updateCategoryUI();
    }

    private void validateAndSend() {
        String number = numberEditText.getText().toString().trim();
        String newCategoryType = vehicleCatTypeEditText.getText().toString().trim();
        String newCategoryCapacity = vehicleCatCapacityEditText.getText().toString().trim();
        boolean newCategory = newVehicleCategoryCheckBox.isChecked();

        if (number.isEmpty()) {
            numberEditText.setError("This field cannot be left blank");
            return;
        }

        if (newCategory) {
            if (newCategoryType.isEmpty()) {
                vehicleCatTypeEditText.setError("This field cannot be left blank");
                return;
            } else if(TextUtils.isEmpty(newCategoryCapacity)) {
                vehicleCatCapacityEditText.setError("This field cannot be left blank");
                return;
            }
        } else {
            int selectedItemPosition = vehicleCategorySelect.getSelectedItemPosition();
            if(selectedItemPosition == 0) {
                Toast.makeText(getActivity(), "Please select vehicle type!", Toast.LENGTH_SHORT).show();
                return;
            }
        }

        brokerVehicleDetails.setNumber(number);

        if (newCategory) {
            brokerVehicleDetails.newCategoryCapacity = newCategoryCapacity;
            brokerVehicleDetails.newCategoryType = newCategoryType;
            brokerVehicleDetails.category = null;
        } else {
            brokerVehicleDetails.newCategoryCapacity = null;
            brokerVehicleDetails.newCategoryType = null;
        }

        makeVehicleAddEditRequest();
    }

    private void setClickListeners() {
        doneButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                validateAndSend();
            }
        });
        newVehicleCategoryCheckBox.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                if (isChecked) {
                    brokerVehicleDetails.category = null;
                    vehicleCategorySelect.setSelection(0);
                    vehicleCategorySelect.setEnabled(false);

                    vehicleCatCapacityEditText.setVisibility(View.VISIBLE);
                    vehicleCatTypeEditText.setVisibility(View.VISIBLE);
                } else {
                    brokerVehicleDetails.category = null;
                    vehicleCategorySelect.setEnabled(true);
                    vehicleCategorySelect.setSelection(0);

                    vehicleCatCapacityEditText.setVisibility(View.INVISIBLE);
                    vehicleCatTypeEditText.setVisibility(View.INVISIBLE);
                }
            }
        });
        cancelButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dismiss();
            }
        });
    }

    private void setViewVariables() {
        doneButton = dialogView.findViewById(R.id.vehicle_add_dialog_add_btn);
        cancelButton = dialogView.findViewById(R.id.vehicle_add_dialog_cancel_btn);

        numberEditText = dialogView.findViewById(R.id.vehicle_no_edittext);
        vehicleCatTypeEditText = dialogView.findViewById(R.id.vehicle_cat_type_edittext);
        vehicleCatCapacityEditText = dialogView.findViewById(R.id.vehicle_cat_capacity_edittext);

        vehicleCategorySelect = dialogView.findViewById(R.id.vehicle_category_spinner);
        newVehicleCategoryCheckBox = dialogView.findViewById(R.id.vehicle_category_new_checkbox);
    }

    private void makeVehicleAddEditRequest() {
        JSONObject jsonObject;
        try {
            jsonObject = brokerVehicleDetails.toJson();
        } catch (JSONException e) {
            e.printStackTrace();
            toast("Error forming request!!");
            return;
        }
        VehicleAddEditRequest request = new VehicleAddEditRequest(
                brokerVehicleDetails.id,jsonObject,
                new VehicleRequestListener());
        queue(request);
    }

    private class VehicleRequestListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            toast("Vehicle Saved");
            if (listener != null) {
                try {
                    BrokerVehicleDetails vehicle = getVehicleDetails(response);
                    listener.onVehicleAddEdit(vehicle, brokerVehicleDetails.id == null);
                } catch (JSONException e) {
                    toast("error reading response");
                    return;
                }
            }
            dismiss();
        }

        @Override
        public void onError() {
            dismissProgress();
            dismiss();
        }
    }

    private BrokerVehicleDetails getVehicleDetails(JSONObject jsonObject) throws JSONException {
        JSONObject data = jsonObject.getJSONObject("data");
        return BrokerVehicleDetails.fromJson(data);
    }

    public interface VehicleAddEditListener {
        void onVehicleAddEdit(BrokerVehicleDetails vehicle, boolean newVehicle);
    }

}