package in.aaho.android.employee.adapter;

import android.graphics.Color;
import android.support.v4.content.ContextCompat;
import android.support.v7.widget.CardView;
import android.support.v7.widget.RecyclerView;
import android.text.TextUtils;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.employee.R;
import in.aaho.android.employee.activity.InTransitActivity;
import in.aaho.android.employee.common.BaseActivity;
import in.aaho.android.employee.common.Utils;
import in.aaho.android.employee.other.Role;
import in.aaho.android.employee.parser.InTransitParser;

/**
 * Created by Suraj M
 */
public class InTransitAdapter extends RecyclerView.Adapter<InTransitAdapter.MyViewHolder> {
    private final BaseActivity activity;
    private List<InTransitParser> dataList;
    private String roles;
    private IOnInTransitItemSelectionListener mIOnInTransitItemSelectionListener;

    public interface IOnInTransitItemSelectionListener {
        void onInTransitItemSelected(InTransitParser inTransitParser);
    }

    public InTransitAdapter(BaseActivity activity, List<InTransitParser> myLoadRequests,
                            String roles, IOnInTransitItemSelectionListener iOnInTransitItemSelectionListener) {
        this.activity = activity;
        this.dataList = myLoadRequests;
        this.roles = roles;
        this.mIOnInTransitItemSelectionListener = iOnInTransitItemSelectionListener;
    }

    class MyViewHolder extends RecyclerView.ViewHolder {
        TextView tvBookingId, tvCustomerName, fromCityTv, toCityTv;
        TextView tvLoadingDate, tvVehicleNumber;
        TextView tvStatus,tvComment,tvLocation,tvUpdateStatus,tvCallDriver;
        CardView cardView;

        MyViewHolder(View view) {
            super(view);
            tvBookingId = view.findViewById(R.id.tvBookingId);
            tvCustomerName = view.findViewById(R.id.tvCustomerName);
            fromCityTv = view.findViewById(R.id.from_city_tv);
            toCityTv = view.findViewById(R.id.to_city_tv);
            tvLoadingDate = view.findViewById(R.id.loading_date_tv);
            tvVehicleNumber = view.findViewById(R.id.tvVehicleNumber);
            tvStatus = view.findViewById(R.id.tvStatus);
            tvComment = view.findViewById(R.id.tvComment);
            tvLocation = view.findViewById(R.id.tvLocation);
            tvCallDriver = view.findViewById(R.id.tvCallDriver);
            tvUpdateStatus = view.findViewById(R.id.tvUpdateStatus);
            cardView = view.findViewById(R.id.card_view);

            tvUpdateStatus.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    InTransitParser inTransitParser = dataList.get(getAdapterPosition());
                    // make interface which will interact with activity from here
                    mIOnInTransitItemSelectionListener.onInTransitItemSelected(inTransitParser);
                }
            });

            tvCallDriver.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    // make call to driver
                    InTransitParser inTransitParser = dataList.get(getAdapterPosition());
                    String driverPhone = String.valueOf(inTransitParser.driverPhone);
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
                .inflate(R.layout.row_in_transit, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        InTransitParser inTransitParser = dataList.get(position);

        /* Update status will be available only to the Traffic & OPS exec & for super users*/
        if(roles.contains(Role.TRAFFIC) || roles.contains(Role.OPS_EXECUTIVE)
                || roles.contains(Role.TECHNOLOGY) || roles.contains(Role.MANAGEMENT)
                || roles.contains(Role.CITY_HEAD)) {
            holder.tvUpdateStatus.setVisibility(View.VISIBLE);
        } else {
            holder.tvUpdateStatus.setVisibility(View.GONE);
        }

        holder.fromCityTv.setText(Utils.def(inTransitParser.fromCity, ""));
        holder.toCityTv.setText(Utils.def(inTransitParser.toCity, ""));

        // set booking Id field
        String bookingId = String.valueOf(inTransitParser.bookingId);
        if(TextUtils.isEmpty(bookingId) || bookingId.equalsIgnoreCase("null")) {
            bookingId = "-";
        }
        holder.tvBookingId.setText(bookingId);

        // set customer Name field
        String customerName = String.valueOf(inTransitParser.customerName);
        if(TextUtils.isEmpty(customerName) || customerName.equalsIgnoreCase("null")) {
            customerName = "-";
        }
        holder.tvCustomerName.setText(customerName);

        // set loading date field
        String loadingDate = String.valueOf(inTransitParser.loadingDate);
        if(TextUtils.isEmpty(loadingDate) || loadingDate.equalsIgnoreCase("null")) {
            loadingDate = "-";
        }
        holder.tvLoadingDate.setText(loadingDate);

        // set vehicle number field
        String vehicleNumber = String.valueOf(inTransitParser.vehicleNumber);
        if(TextUtils.isEmpty(vehicleNumber) || vehicleNumber.equalsIgnoreCase("null")) {
            vehicleNumber = "-";
        }

        // set LR number field
        String lrNumber = String.valueOf(inTransitParser.lrNumber);
        if(TextUtils.isEmpty(lrNumber) || lrNumber.equalsIgnoreCase("null")) {
            lrNumber = " ";
        } else {
            lrNumber = " ("+ lrNumber +") ";
        }
        holder.tvVehicleNumber.setText(vehicleNumber + lrNumber);

        // set location field
        String location = String.valueOf(inTransitParser.location);
        if(TextUtils.isEmpty(location) || location.equalsIgnoreCase("null")) {
            location = "-";
        }
        holder.tvLocation.setText(location);

        // set booking status field
        String status = String.valueOf(inTransitParser.bookingStatusCurrent);
        if(TextUtils.isEmpty(status) || status.equalsIgnoreCase("null")) {
            status = "-";
        }
        holder.tvStatus.setText(status);

        // set status & booking status comment created on field
        String comment = String.valueOf(inTransitParser.bookingStatusComment);
        if(TextUtils.isEmpty(comment) || comment.equalsIgnoreCase("null")) {
            comment = "-";
        } else {
            String bookingStatusCommentCreatedOn = inTransitParser.bookingStatusCommentCreatedOn;
            if(TextUtils.isEmpty(bookingStatusCommentCreatedOn) || bookingStatusCommentCreatedOn.equalsIgnoreCase("null")) {
                comment = "-";
            } else {
                comment = comment + "\n"+bookingStatusCommentCreatedOn;
            }
        }
        holder.tvComment.setText(comment);
        if(inTransitParser.location_overdue) {
            holder.cardView.setCardBackgroundColor(
                    ContextCompat.getColor(activity, R.color.colorLightRed));
        }else{
            holder.cardView.setCardBackgroundColor(Color.WHITE);
        }

        // set move to top visibility
        ((InTransitActivity)activity).setMoveToTopVisibility(position);
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }


}

