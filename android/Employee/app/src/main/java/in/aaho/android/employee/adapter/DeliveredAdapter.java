package in.aaho.android.employee.adapter;

import android.app.DatePickerDialog;
import android.content.Intent;
import android.graphics.Color;
import android.support.v4.content.ContextCompat;
import android.support.v7.widget.CardView;
import android.support.v7.widget.RecyclerView;
import android.text.TextUtils;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.DatePicker;
import android.widget.TextView;

import java.util.Calendar;
import java.util.List;

import in.aaho.android.employee.R;
import in.aaho.android.employee.RequirementActivity;
import in.aaho.android.employee.activity.BookingDetailsActivity;
import in.aaho.android.employee.activity.DeliveredActivity;
import in.aaho.android.employee.common.BaseActivity;
import in.aaho.android.employee.common.Utils;
import in.aaho.android.employee.other.Role;
import in.aaho.android.employee.parser.DeliveredParser;

/**
 * Created by Suraj M
 */
public class DeliveredAdapter extends RecyclerView.Adapter<DeliveredAdapter.MyViewHolder> {
    private final BaseActivity activity;
    private List<DeliveredParser> dataList;
    private String roles;
    private IOnDeliveredItemSelectionListener mIOnDeliveredItemSelectionListener;
    private IOnDeliveredUploadPODClickListener mIOnDeliveredUploadPODClickListener;
    private IOnDeliveredViewPODClickListener mIOnDeliveredViewPODClickListener;
    private IOnDeliveredSetDueDateListener mIOnDeliveredSetDueDateListener;

    public static final String POD_PENDING = "pending";
    public static final String POD_REJECTED = "rejected";
    /*public static final String POD_UNVERIFIED = "unverified";
    public static final String POD_DELIVERED = "completed";*/

    public interface IOnDeliveredItemSelectionListener {
        void onDeliveredItemSelected(DeliveredParser deliveredParser);
    }

    public interface IOnDeliveredUploadPODClickListener {
        void onDeliveredUploadPODClicked(DeliveredParser deliveredParser);
    }

    public interface IOnDeliveredViewPODClickListener {
        void onDeliveredViewPODClicked(DeliveredParser deliveredParser);
    }

    public interface IOnDeliveredSetDueDateListener {
        void onDeliveredSetDateClicked(DeliveredParser deliveredParser, String date);
    }

    public DeliveredAdapter(BaseActivity activity, List<DeliveredParser> deliveredParserList,
                            String roles, IOnDeliveredItemSelectionListener iOnDeliveredItemSelectionListener,
                            IOnDeliveredUploadPODClickListener iOnDeliveredUploadPODClickListener,
                            IOnDeliveredViewPODClickListener iOnDeliveredViewPODClickListener,
                            IOnDeliveredSetDueDateListener iOnDeliveredSetDateListener) {
        this.activity = activity;
        this.dataList = deliveredParserList;
        this.roles = roles;
        this.mIOnDeliveredItemSelectionListener = iOnDeliveredItemSelectionListener;
        this.mIOnDeliveredUploadPODClickListener = iOnDeliveredUploadPODClickListener;
        this.mIOnDeliveredViewPODClickListener = iOnDeliveredViewPODClickListener;
        this.mIOnDeliveredSetDueDateListener = iOnDeliveredSetDateListener;
    }

    class MyViewHolder extends RecyclerView.ViewHolder {
        TextView tvBookingId, tvCustomerName, fromCityTv, toCityTv;
        TextView tvLoadingDate, tvVehicleNumber, tvWeight, tvRate;
        TextView tvStatus,tvLocation,tvComment,tvDueDate, tvDueDateLabel;
        TextView tvViewPOD,tvUploadPOD,tvUpdateStatus,tvCallSupplier,tvSetDate;
        CardView cardView;

        MyViewHolder(View view) {
            super(view);
            tvBookingId = view.findViewById(R.id.tvBookingId);
            tvCustomerName = view.findViewById(R.id.tvCustomerName);
            fromCityTv = view.findViewById(R.id.from_city_tv);
            toCityTv = view.findViewById(R.id.to_city_tv);
            tvLoadingDate = view.findViewById(R.id.loading_date_tv);
            tvVehicleNumber = view.findViewById(R.id.tvVehicleNumber);
            tvWeight = view.findViewById(R.id.tvWeight);
            tvRate = view.findViewById(R.id.tvRate);
            tvStatus = view.findViewById(R.id.tvStatus);
            tvDueDate = view.findViewById(R.id.tvDueDate);
            tvDueDateLabel = view.findViewById(R.id.tvDueDateLabel);
            tvComment = view.findViewById(R.id.tvComment);
            tvLocation = view.findViewById(R.id.tvLocation);
            tvViewPOD = view.findViewById(R.id.tvViewPOD);
            tvUploadPOD = view.findViewById(R.id.tvUploadPOD);
            tvSetDate = view.findViewById(R.id.tvSetDate);
            tvUpdateStatus = view.findViewById(R.id.tvUpdateStatus);
            tvCallSupplier = view.findViewById(R.id.tvCallSupplier);
            cardView = view.findViewById(R.id.card_view);

            tvViewPOD.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    DeliveredParser deliveredParser = dataList.get(getAdapterPosition());
                    // make interface which will interact with activity from here
                    mIOnDeliveredViewPODClickListener.onDeliveredViewPODClicked(deliveredParser);
                }
            });

            tvUploadPOD.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    DeliveredParser deliveredParser = dataList.get(getAdapterPosition());
                    // make interface which will interact with activity from here
                    mIOnDeliveredUploadPODClickListener.onDeliveredUploadPODClicked(deliveredParser);
                }
            });

            tvUpdateStatus.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    DeliveredParser deliveredParser = dataList.get(getAdapterPosition());
                    // make interface which will interact with activity from here
                    mIOnDeliveredItemSelectionListener.onDeliveredItemSelected(deliveredParser);
                }
            });

            tvSetDate.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    DeliveredParser deliveredParser = dataList.get(getAdapterPosition());
                    Calendar c = Calendar.getInstance();
                    int mYear = c.get(Calendar.YEAR);
                    int mMonth = c.get(Calendar.MONTH);
                    int mDay = c.get(Calendar.DAY_OF_MONTH);
                    ValiditySetDateListener dateSetListener = new ValiditySetDateListener(deliveredParser);
                    DatePickerDialog datePickerDialog = new DatePickerDialog(activity, dateSetListener, mYear, mMonth, mDay);
                    datePickerDialog.show();
                    datePickerDialog.getDatePicker().setMinDate(System.currentTimeMillis() - 1000);
                }
            });

            tvCallSupplier.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    // make call to driver
                    DeliveredParser deliveredParser = dataList.get(getAdapterPosition());
                    String driverPhone = String.valueOf(deliveredParser.supplierPhone);
                    if(TextUtils.isEmpty(driverPhone) || driverPhone.equalsIgnoreCase("null")) {
                        Utils.toast("Supplier phone is not available!");
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

            cardView.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    Intent intent = new Intent(v.getContext(), BookingDetailsActivity.class);
                    intent.putExtra("id", dataList.get(getAdapterPosition()).id);
                    v.getContext().startActivity(intent);
                }
            });

        }

    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.row_delivered, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        DeliveredParser deliveredParser = dataList.get(position);

        /* Update status will be available only to the Traffic & OPS exec & for super users*/
        if(roles.contains(Role.TRAFFIC) || roles.contains(Role.OPS_EXECUTIVE)
                || roles.contains(Role.TECHNOLOGY) || roles.contains(Role.MANAGEMENT)
                || roles.contains(Role.CITY_HEAD)) {
            holder.tvUpdateStatus.setVisibility(View.VISIBLE);
        } else {
            holder.tvUpdateStatus.setVisibility(View.GONE);
        }

        /* TODO: NOTE: As discussed we are hiding update status functionality for now */
        holder.tvUpdateStatus.setVisibility(View.GONE);

        String podStatus = deliveredParser.podStatus;
        if(podStatus == null || podStatus.equalsIgnoreCase(POD_PENDING)) {
            // POD not uploaded yet hide view POD button
            holder.tvViewPOD.setVisibility(View.GONE);
            holder.tvSetDate.setVisibility(View.VISIBLE);
            holder.tvDueDate.setVisibility(View.VISIBLE);
            holder.tvDueDateLabel.setVisibility(View.VISIBLE);
        } else {
            // Allow user to view pod
            holder.tvViewPOD.setVisibility(View.VISIBLE);
            holder.tvSetDate.setVisibility(View.GONE);
            holder.tvDueDate.setVisibility(View.GONE);
            holder.tvDueDateLabel.setVisibility(View.GONE);
        }

        holder.fromCityTv.setText(Utils.def(deliveredParser.fromCity, ""));
        holder.toCityTv.setText(Utils.def(deliveredParser.toCity, ""));

        // set booking Id field
        String bookingId = String.valueOf(deliveredParser.bookingId);
        if(TextUtils.isEmpty(bookingId) || bookingId.equalsIgnoreCase("null")) {
            bookingId = "-";
        }
        holder.tvBookingId.setText(bookingId);

        // set customer Name field
        String customerName = String.valueOf(deliveredParser.customerName);
        if(TextUtils.isEmpty(customerName) || customerName.equalsIgnoreCase("null")) {
            customerName = "-";
        }
        holder.tvCustomerName.setText(customerName);

        // set vehicle number field
        String vehicleNumber = String.valueOf(deliveredParser.vehicleNumber);
        if(TextUtils.isEmpty(vehicleNumber) || vehicleNumber.equalsIgnoreCase("null")) {
            vehicleNumber = "-";
        }

        // set LR number field
        String lrNumber = String.valueOf(deliveredParser.lrNumber);
        if(TextUtils.isEmpty(lrNumber) || lrNumber.equalsIgnoreCase("null")) {
            lrNumber = " ";
        } else {
            lrNumber = " ("+ lrNumber +") ";
        }
        holder.tvVehicleNumber.setText(vehicleNumber + lrNumber);

        // set weight field
        String weight = String.valueOf(deliveredParser.weight);
        if(weight == null || weight.equalsIgnoreCase("null")) {
            weight = "-";
        }
        holder.tvWeight.setText(weight);

        // set rate field
        String rate = String.valueOf(deliveredParser.rate);
        if(rate == null || rate.equalsIgnoreCase("null")) {
            rate = "-";
        }
        holder.tvRate.setText(rate);

        // set booking status field
        String status = String.valueOf(deliveredParser.bookingStatusCurrent);
        if(TextUtils.isEmpty(status) || status.equalsIgnoreCase("null")) {
            status = "-";
        }
        holder.tvStatus.setText(status);


        // set Due date field
        String due_date = String.valueOf(deliveredParser.dueDate);
        if(due_date == null || due_date.equalsIgnoreCase("null")) {
            due_date = "-";
        }
        holder.tvDueDate.setText(due_date);

        // set latest comment & comment created on field
        String comment = String.valueOf(deliveredParser.bookingStatusComment);
        if(TextUtils.isEmpty(comment) || comment.equalsIgnoreCase("null")) {
            comment = "-";
        } else {
            String bookingStatusCommentCreatedOn = deliveredParser.bookingStatusCommentCreatedOn;
            if(TextUtils.isEmpty(bookingStatusCommentCreatedOn) || bookingStatusCommentCreatedOn.equalsIgnoreCase("null")) {
                comment = "-";
            } else {
                comment = comment + "\n"+bookingStatusCommentCreatedOn;
            }
        }
        holder.tvComment.setText(comment);

        if(status.equalsIgnoreCase("pod_uploaded")){
            if(podStatus.equalsIgnoreCase(POD_PENDING) || podStatus.equalsIgnoreCase(POD_REJECTED)) {
                holder.cardView.setCardBackgroundColor(
                        ContextCompat.getColor(activity,R.color.colorLightRed));
            }else {
                holder.cardView.setCardBackgroundColor(
                        ContextCompat.getColor(activity, R.color.colorLightGreen));
            }
        }else if(deliveredParser.bookingStatusCurrentOverdue){
            holder.cardView.setCardBackgroundColor(
                    ContextCompat.getColor(activity,R.color.colorLightRed));
        }else{
            holder.cardView.setCardBackgroundColor(Color.WHITE);
        }

        // set move to top visibility
        ((DeliveredActivity)activity).setMoveToTopVisibility(position);
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }


    private class ValiditySetDateListener implements DatePickerDialog.OnDateSetListener {
        private DeliveredParser deliveredParser;
        private ValiditySetDateListener(DeliveredParser deliveredparser){
            this.deliveredParser = deliveredparser;
        }

        @Override
        public void onDateSet(DatePicker view, int year, int monthOfYear, int dayOfMonth) {
            // make interface which will interact with activity from here
            mIOnDeliveredSetDueDateListener.onDeliveredSetDateClicked(this.deliveredParser,
                    Integer.toString(year)+"-"+Integer.toString(monthOfYear+1)+"-"+Integer.toString(dayOfMonth));
//            Utils.toast("Set Date: "+Integer.toString(year)+"-"+Integer.toString(monthOfYear+1)+"-"+Integer.toString(dayOfMonth));
        }
    }


}