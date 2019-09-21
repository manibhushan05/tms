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

public class OwnerSelectDialogFragment extends BaseDialogFragment {

    private RecyclerView ownerDialogContainer;
    private Button addOwnerBtn, cancelBtn;
    private View dialogView;

    private OwnerChangeListener listener;

    private OwnerDialogAdapter ownerDialogAdapter;
    private TextView emptyView;

    public static void showNewDialog(BaseActivity activity, OwnerChangeListener listener) {
        OwnerSelectDialogFragment dialog = new OwnerSelectDialogFragment();
        dialog.setChangeListener(listener);
        dialog.setActivity(activity);
        dialog.show(activity.getSupportFragmentManager(), "owner_select_fragment");
    }

    public void setChangeListener(OwnerChangeListener listener) {
        this.listener = listener;
    }

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        ownerDialogAdapter = new OwnerDialogAdapter(this, listener);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        dialogView = inflater.inflate(R.layout.vehicle_owner_select_dialog, container, false);

        setViewVariables();
        setClickListeners();
        setupAdapters();

        if (VehicleOwner.ownerList.size() == 0) {
            emptyView.setVisibility(View.VISIBLE);
        } else {
            emptyView.setVisibility(View.GONE);
        }

        return dialogView;
    }

    private void setupAdapters() {
        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getActivity().getApplicationContext());
        ownerDialogContainer.setLayoutManager(mLayoutManager);
        ownerDialogContainer.setItemAnimator(new DefaultItemAnimator());
        ownerDialogContainer.setAdapter(ownerDialogAdapter);

        ownerDialogAdapter.notifyDataSetChanged();
    }

    private void setClickListeners() {
        addOwnerBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                launchAddOwnerDialog();
            }
        });
        cancelBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dismiss();
            }
        });
    }

    private void launchAddOwnerDialog() {
        OwnerAddDialogFragment.showNewDialog(getBaseActivity(), new OwnerAddDialogFragment.OwnerAddListener() {

            @Override
            public void onOwnerAdd(VehicleOwner owner) {
                if (owner != null) {
                    VehicleOwner.ownerList.add(owner);
                    ownerDialogAdapter.notifyDataSetChanged();
                }
            }
        });
    }

    private void setViewVariables() {
        // scrollView = (NestedScrollView) dialogView.findViewById(R.id.ship_dialog_scroll_view);
        ownerDialogContainer = dialogView.findViewById(R.id.select_owner_dialog_container);
        addOwnerBtn = dialogView.findViewById(R.id.select_owner_dialog_add_btn);
        cancelBtn = dialogView.findViewById(R.id.select_owner_dialog_cancel_btn);
        emptyView = dialogView.findViewById(R.id.empty_view);
    }

    public interface OwnerChangeListener {
        void onChange(VehicleOwner vehicleOwner);
    }

}