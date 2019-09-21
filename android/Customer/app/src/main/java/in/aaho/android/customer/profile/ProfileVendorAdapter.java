package in.aaho.android.customer.profile;

/**
 * Created by shobhit on 6/8/16.
 */

import android.content.DialogInterface;
import android.support.v7.app.AlertDialog;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageButton;
import android.widget.TextView;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.List;

import in.aaho.android.customer.common.ApiResponseListener;
import in.aaho.android.customer.common.ListItemListerner;
import in.aaho.android.customer.common.Utils;
import in.aaho.android.customer.R;
import in.aaho.android.customer.booking.Vendor;
import in.aaho.android.customer.requests.VendorDeleteRequest;


public class ProfileVendorAdapter extends RecyclerView.Adapter<ProfileVendorAdapter.MyViewHolder> {

    private ProfileActivity profileActivity;
    private List<Vendor> vendorList;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        public TextView name, phone;
        public ImageButton delete;

        public DelClickListener delClickListener;

        public MyViewHolder(View view) {
            super(view);
            name = (TextView) view.findViewById(R.id.profile_vendor_name_textview);
            phone = (TextView) view.findViewById(R.id.profile_vendor_phone_textview);
            delete = (ImageButton) view.findViewById(R.id.profile_vendor_delete_btn);

            delClickListener = new DelClickListener();

            delete.setOnClickListener(delClickListener);
        }

        public void updateListenerPositions(int position) {
            delClickListener.updatePosition(position);
        }
    }

    public ProfileVendorAdapter(List<Vendor> vendorList, ProfileActivity profileActivity) {
        this.vendorList = vendorList;
        this.profileActivity = profileActivity;
    }

    private class DelClickListener extends ListItemListerner implements View.OnClickListener {

        @Override
        public void onClick(View v) {
            showDelAlertDialog(position);
        }
    }

    private void showDelAlertDialog(final int position) {
        AlertDialog.Builder builder = new AlertDialog.Builder(profileActivity);

        builder.setTitle("Delete Vendor?");
        builder.setMessage("Are you sure you wan't to delete this vendor?");
        builder.setPositiveButton("Cancel", new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int id) {

            }
        });
        builder.setNegativeButton("Delete", new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int id) {
                makeDeleteVendorRequest(position);
            }
        });
        builder.show();
    }


    private void makeDeleteVendorRequest(int position) {
        long id = vendorList.get(position).getId();
        VendorDeleteRequest vendorDelRequest = new VendorDeleteRequest(id, new VendorDelListener());
        profileActivity.queue(vendorDelRequest);
    }

    private class VendorDelListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            profileActivity.dismissProgress();
            try {
                Vendor.createFromJson(response.getJSONArray("vendors"));
            } catch (JSONException e) {
                e.printStackTrace();
            }
            Utils.toast("Vendor Deleted");
        }

        @Override
        public void onError() {
            profileActivity.dismissProgress();
        }
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.profile_vendor_card, parent, false);

        return new MyViewHolder(itemView);
    }


    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        Vendor vendor = vendorList.get(position);
        holder.updateListenerPositions(position);
        if (vendor.getName() != null) {
            holder.name.setText(vendor.getName());
        } else {
            holder.name.setText("");
        }
        if (vendor.phone != null) {
            holder.phone.setText(vendor.phone);
        } else {
            holder.phone.setText("");
        }
    }

    @Override
    public int getItemCount() {
        return vendorList.size();
    }
}
