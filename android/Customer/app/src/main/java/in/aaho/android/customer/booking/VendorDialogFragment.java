package in.aaho.android.customer.booking;

import android.os.Bundle;
import android.support.annotation.Nullable;
import android.support.v7.widget.DefaultItemAnimator;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.CompoundButton;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.List;

import in.aaho.android.customer.common.BaseDialogFragment;
import in.aaho.android.customer.R;
import in.aaho.android.customer.profile.VendorAddDialogFragment;

/**
 * Created by shobhit on 8/8/16.
 */

public class VendorDialogFragment extends BaseDialogFragment {

    private RecyclerView vendorDialogContainer;
    private Button sendButton;
    private Button cancelButton;
    private TextView vendorCountTextView;
    private CheckBox selectAllCheckBox;
    private View dialogView;

    private TextView noVendorsTextView;
    private TextView addVendorButton;

    private BookingActivity bookingActivity;

    private VendorDialogAdapter vendorDialogAdapter;
    private List<Vendor> vendorList = new ArrayList<>();
    private CompoundButton.OnCheckedChangeListener selectAllChangeListener;
    private AddVendorClickListener addVendorClickListener;
    private long bookingId;

    public void setVendors(List<Vendor> vendors) {
        this.vendorList = vendors;
    }

    public void setBookingActivity(BookingActivity bookingActivity) {
        this.bookingActivity = bookingActivity;
    }

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        vendorDialogAdapter = new VendorDialogAdapter(vendorList, this);

        selectAllChangeListener = new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                setAllVendorSelected(isChecked);
            }
        };
        addVendorClickListener = new AddVendorClickListener();
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        dialogView = inflater.inflate(R.layout.booking_vendor_dialog, container, false);

        setViewVariables();
        setClickListeners();
        setupAdapters();

        return dialogView;
    }


    private void setupAdapters() {
        setupVendorDialogAdapter();
    }

    private void setupVendorDialogAdapter() {
        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getActivity().getApplicationContext());
        vendorDialogContainer.setLayoutManager(mLayoutManager);
        vendorDialogContainer.setItemAnimator(new DefaultItemAnimator());
        vendorDialogContainer.setAdapter(vendorDialogAdapter);

        vendorDialogAdapter.notifyDataSetChanged();
    }

    public void setSelectAll(boolean selected) {
        if (selectAllCheckBox.isChecked() != selected) {
            selectAllCheckBox.setOnCheckedChangeListener(null);
            selectAllCheckBox.setChecked(selected);
            selectAllCheckBox.setOnCheckedChangeListener(selectAllChangeListener);
        }
    }

    private void setClickListeners() {
        sendButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                bookingActivity.submitVendorRequestForm(bookingId);
                VendorDialogFragment.this.dismiss();
            }
        });
        cancelButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                VendorDialogFragment.this.dismiss();
            }
        });
        selectAllCheckBox.setOnCheckedChangeListener(selectAllChangeListener);
        addVendorButton.setOnClickListener(addVendorClickListener);
    }

    private void setAllVendorSelected(boolean selected) {
        for (Vendor v : vendorList) {
            v.setSelected(selected);
        }
        vendorDialogAdapter.notifyDataSetChanged();
    }

    private void setViewVariables() {
        vendorDialogContainer = (RecyclerView) dialogView.findViewById(R.id.vendor_dialog_container);
        vendorCountTextView = (TextView) dialogView.findViewById(R.id.vendor_dialog_vendor_msg_count);
        sendButton = (Button) dialogView.findViewById(R.id.vendor_dialog_send_btn);
        cancelButton = (Button) dialogView.findViewById(R.id.vendor_dialog_cancel_btn);
        selectAllCheckBox = (CheckBox) dialogView.findViewById(R.id.vendor_dialog_select_all_checkbox);

        noVendorsTextView = (TextView) dialogView.findViewById(R.id.vendor_dialog_no_vendors_message);
        addVendorButton = (TextView) dialogView.findViewById(R.id.vendor_dialog_add_vendor_btn);
    }

    public void updateVendorCount(int count) {
        if (vendorCountTextView != null) {
            vendorCountTextView.setText(String.valueOf(count));
        }
    }

    private class AddVendorClickListener implements View.OnClickListener {
        @Override
        public void onClick(View v) {
            showAddVendorDialog();
        }
    }

    private void showAddVendorDialog() {
        VendorAddDialogFragment.showNewDialog(bookingActivity, new VendorAddDialogFragment.UpdateVendorListener() {
            @Override
            public void onVendorUpdate() {
                updateVendorUI();
            }
        });
    }

    public void setBookingId(long bookingId) {
        this.bookingId = bookingId;
    }

    public void updateVendorUI() {
        vendorDialogAdapter.notifyDataSetChanged();
        if (vendorDialogAdapter.getItemCount() == 0) {
            noVendorsTextView.setVisibility(View.VISIBLE);
        } else {
            noVendorsTextView.setVisibility(View.GONE);
        }
    }
}