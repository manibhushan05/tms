package in.aaho.android.ownr.booking;

/**
 * Created by mani on 6/8/16.
 */

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.CheckBox;
import android.widget.CompoundButton;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.ownr.common.ListItemListerner;
import in.aaho.android.ownr.R;


public class VendorDialogAdapter extends RecyclerView.Adapter<VendorDialogAdapter.MyViewHolder> {

    private List<Vendor> vendorList;
    private VendorDialogFragment vendorDialogFragment;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        public CheckBox selected;
        public TextView name;

        public VendorCheckChangeListener vendorCheckChangeListener;

        public MyViewHolder(View view) {
            super(view);
            selected = view.findViewById(R.id.vendor_card_selected_checkbox);
            name = view.findViewById(R.id.vendor_card_name_textview);

            vendorCheckChangeListener = new VendorCheckChangeListener();

            selected.setOnCheckedChangeListener(vendorCheckChangeListener);
        }

        public void updateListenerPositions(int position) {
            vendorCheckChangeListener.updatePosition(position);
        }
    }

    public VendorDialogAdapter(List<Vendor> vendorList, VendorDialogFragment vendorDialogFragment) {
        this.vendorList = vendorList;
        this.vendorDialogFragment = vendorDialogFragment;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.booking_vendor_card, parent, false);

        return new MyViewHolder(itemView);
    }


    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        Vendor vendor = vendorList.get(position);
        holder.updateListenerPositions(position);
        holder.selected.setChecked(vendor.isSelected());
        if (vendor.getName() != null) {
            holder.name.setText(vendor.getName());
        }
    }

    @Override
    public int getItemCount() {
        return vendorList.size();
    }

    private int getSelectedVendorCount() {
        int count = 0;
        for (Vendor vendor: vendorList) {
            if (vendor.isSelected()) {
                count = count + 1;
            }
        }
        return count;
    }

    private boolean allVendorsSelected() {
        boolean allChecked = true;
        for (Vendor v : vendorList) {
            if (!v.isSelected()) {
                allChecked = false;
                break;
            }
        }
        return allChecked;
    }

    private class VendorCheckChangeListener extends ListItemListerner implements CompoundButton.OnCheckedChangeListener {

        @Override
        public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
            vendorList.get(position).setSelected(isChecked);
            vendorDialogFragment.updateVendorCount(getSelectedVendorCount());
            vendorDialogFragment.setSelectAll(allVendorsSelected());
        }
    }

}
