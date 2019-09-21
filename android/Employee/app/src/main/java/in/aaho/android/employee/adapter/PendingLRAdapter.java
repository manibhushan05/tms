package in.aaho.android.employee.adapter;

import android.support.v7.widget.CardView;
import android.support.v7.widget.RecyclerView;
import android.text.TextUtils;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.employee.R;
import in.aaho.android.employee.activity.PendingLRActivity;
import in.aaho.android.employee.common.BaseActivity;
import in.aaho.android.employee.common.Utils;
import in.aaho.android.employee.other.Role;
import in.aaho.android.employee.parser.InTransitParser;
import in.aaho.android.employee.parser.PendingLRParser;

/**
 * Created by Suraj M
 */
public class PendingLRAdapter extends RecyclerView.Adapter<PendingLRAdapter.MyViewHolder> {
    private final BaseActivity activity;
    private List<PendingLRParser> dataList;
    private String roles;
    private IOnPendingLRItemSelectionListener mIOnPendingLRItemSelectionListener;

    public interface IOnPendingLRItemSelectionListener {
        void onPendingLRItemSelected(PendingLRParser pendingLRParser);
    }

    public PendingLRAdapter(BaseActivity activity, List<PendingLRParser> myLoadRequests,
                            String roles,IOnPendingLRItemSelectionListener iOnPendingLRItemSelectionListener) {
        this.activity = activity;
        this.dataList = myLoadRequests;
        this.roles = roles;
        this.mIOnPendingLRItemSelectionListener = iOnPendingLRItemSelectionListener;
    }

    class MyViewHolder extends RecyclerView.ViewHolder {
        TextView tvBookingId, tvCustomerName, fromCityTv, toCityTv;
        TextView vehicleTypeTv, tvVehicleNumber;
        TextView tvStatus, tvUpdateStatus, tvComment, tvCallDriver;
        CardView cardView;

        MyViewHolder(View view) {
            super(view);
            tvBookingId = view.findViewById(R.id.tvBookingId);
            tvCustomerName = view.findViewById(R.id.tvCustomerName);
            fromCityTv = view.findViewById(R.id.from_city_tv);
            toCityTv = view.findViewById(R.id.to_city_tv);
            vehicleTypeTv = view.findViewById(R.id.vehicle_type_tv);
            tvVehicleNumber = view.findViewById(R.id.tvVehicleNumber);
            tvStatus = view.findViewById(R.id.tvStatus);
            tvCallDriver = view.findViewById(R.id.tvCallDriver);
            tvUpdateStatus = view.findViewById(R.id.tvUpdateStatus);
            tvComment = view.findViewById(R.id.tvComment);
            cardView = view.findViewById(R.id.card_view);

            tvUpdateStatus.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    PendingLRParser pendingLRParser = dataList.get(getAdapterPosition());
                    // make interface which will interact with activity from here
                    mIOnPendingLRItemSelectionListener.onPendingLRItemSelected(pendingLRParser);
                }
            });

            tvCallDriver.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    // make call to driver
                    PendingLRParser pendingLRParser = dataList.get(getAdapterPosition());
                    String driverPhone = String.valueOf(pendingLRParser.driverPhone);
                    if(TextUtils.isEmpty(driverPhone) || driverPhone.equalsIgnoreCase("null")) {
                        Utils.toast("Driver phone is not available!");
                    } else {
                        if(driverPhone.length() > 10) {
                            driverPhone = "+91"+driverPhone.substring(driverPhone.length()-10,driverPhone.length());
                        } else {
                            driverPhone = "+91"+driverPhone;
                        }
                        Utils.launchDialer(v.getContext(), driverPhone);
                    }
                }
            });
        }

    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.row_pending_lr, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        PendingLRParser pendingLRParser = dataList.get(position);

        /* Update status will be available only to the Traffic & OPS exec */
        if(roles.contains(Role.TRAFFIC) || roles.contains(Role.OPS_EXECUTIVE)
                || roles.contains(Role.TECHNOLOGY) || roles.contains(Role.MANAGEMENT)
                || roles.contains(Role.CITY_HEAD)) {
            holder.tvUpdateStatus.setVisibility(View.VISIBLE);
        } else {
            holder.tvUpdateStatus.setVisibility(View.GONE);
        }

        holder.fromCityTv.setText(Utils.def(pendingLRParser.fromCity, ""));
        holder.toCityTv.setText(Utils.def(pendingLRParser.toCity, ""));

        // set booking Id field
        String bookingId = String.valueOf(pendingLRParser.bookingId);
        if(TextUtils.isEmpty(bookingId) || bookingId.equalsIgnoreCase("null")) {
            bookingId = "-";
        }
        holder.tvBookingId.setText(bookingId);

        // set customer Name field
        String customerName = String.valueOf(pendingLRParser.customerName);
        if(TextUtils.isEmpty(customerName) || customerName.equalsIgnoreCase("null")) {
            customerName = "-";
        }
        holder.tvCustomerName.setText(customerName);

        // set vehicle type field
        String typeOfVehicle = String.valueOf(pendingLRParser.vehicleType);
        if(TextUtils.isEmpty(typeOfVehicle) || typeOfVehicle.equalsIgnoreCase("null")) {
            typeOfVehicle = "-";
        }
        holder.vehicleTypeTv.setText(typeOfVehicle);

        // set vehicle number field
        String vehicleNumber = String.valueOf(pendingLRParser.vehicleNumber);
        if(TextUtils.isEmpty(vehicleNumber) || vehicleNumber.equalsIgnoreCase("null")) {
            vehicleNumber = "-";
        }
        holder.tvVehicleNumber.setText(vehicleNumber);

        // set booking status field
        String status = String.valueOf(pendingLRParser.bookingStatusCurrent);
        if(TextUtils.isEmpty(status) || status.equalsIgnoreCase("null")) {
            status = "-";
        }
        holder.tvStatus.setText(status);

        // set latest comment & comment created on field
        String comment = String.valueOf(pendingLRParser.bookingStatusComment);
        if(TextUtils.isEmpty(comment) || comment.equalsIgnoreCase("null")) {
            comment = "-";
        } else {
            String bookingStatusCommentCreatedOn = pendingLRParser.bookingStatusCommentCreatedOn;
            if(TextUtils.isEmpty(bookingStatusCommentCreatedOn) || bookingStatusCommentCreatedOn.equalsIgnoreCase("null")) {
                comment = "-";
            } else {
                comment = comment + "\n"+bookingStatusCommentCreatedOn;
            }
        }
        holder.tvComment.setText(comment);

        // set move to top visibility
        ((PendingLRActivity)activity).setMoveToTopVisibility(position);
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }


}

