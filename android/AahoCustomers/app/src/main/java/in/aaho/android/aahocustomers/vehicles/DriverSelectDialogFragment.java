package in.aaho.android.aahocustomers.vehicles;

import android.os.Bundle;
import android.support.annotation.Nullable;
import android.support.v7.widget.DefaultItemAnimator;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

import in.aaho.android.aahocustomers.R;
import in.aaho.android.aahocustomers.common.BaseActivity;
import in.aaho.android.aahocustomers.common.BaseDialogFragment;

/**
 * Created by shobhit on 8/8/16.
 */

public class DriverSelectDialogFragment extends BaseDialogFragment {

    private RecyclerView driverDialogContainer;
    private Button addDriverBtn, cancelBtn;
    private View dialogView;

    private DriverChangeListener listener;

    private DriverDialogAdapter driverDialogAdapter;
    private TextView emptyView;

    public static void showNewDialog(BaseActivity activity, DriverChangeListener listener) {
        DriverSelectDialogFragment dialog = new DriverSelectDialogFragment();
        dialog.setChangeListener(listener);
        dialog.setActivity(activity);
        dialog.show(activity.getSupportFragmentManager(), "driver_select_fragment");
    }

    public void setChangeListener(DriverChangeListener listener) {
        this.listener = listener;
    }

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        driverDialogAdapter = new DriverDialogAdapter(this, listener);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        dialogView = inflater.inflate(R.layout.vehicle_driver_select_dialog, container, false);

        setViewVariables();
        setClickListeners();
        setupAdapters();

        if (VehicleDriver.driverList.size() == 0) {
            emptyView.setVisibility(View.VISIBLE);
        } else {
            emptyView.setVisibility(View.GONE);
        }

        return dialogView;
    }

    private void setupAdapters() {
        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getActivity().getApplicationContext());
        driverDialogContainer.setLayoutManager(mLayoutManager);
        driverDialogContainer.setItemAnimator(new DefaultItemAnimator());
        driverDialogContainer.setAdapter(driverDialogAdapter);

        driverDialogAdapter.notifyDataSetChanged();
    }

    private void setClickListeners() {
        addDriverBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                launchAddDriverDialog();
            }
        });
        cancelBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dismiss();
            }
        });
    }

    private void launchAddDriverDialog() {
        DriverAddDialogFragment.showNewDialog(getBaseActivity(), new DriverAddDialogFragment.DriverAddListener() {

            @Override
            public void onDriverAdd(VehicleDriver driver) {
                if (driver != null) {
                    VehicleDriver.driverList.add(driver);
                    driverDialogAdapter.notifyDataSetChanged();
                }
            }
        });
    }

    private void setViewVariables() {
        driverDialogContainer = dialogView.findViewById(R.id.select_owner_dialog_container);
        addDriverBtn = dialogView.findViewById(R.id.select_owner_dialog_add_btn);
        cancelBtn = dialogView.findViewById(R.id.select_owner_dialog_cancel_btn);
        emptyView = dialogView.findViewById(R.id.empty_view);
    }

    public interface DriverChangeListener {
        void onChange(VehicleDriver vehicleDriver);
    }

}