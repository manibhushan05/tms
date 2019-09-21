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
import in.aaho.android.employee.activity.InvoiceConfirmationActivity;
import in.aaho.android.employee.common.BaseActivity;
import in.aaho.android.employee.common.Utils;
import in.aaho.android.employee.parser.InvoiceConfirmationParser;

/**
 * Created by Suraj M
 */
public class InvoiceConfirmationAdapter extends RecyclerView.Adapter<InvoiceConfirmationAdapter.MyViewHolder> {
    private final BaseActivity activity;
    private List<InvoiceConfirmationParser> dataList;
    private String roles;
    private IOnInvoiceConfirmationViewPODClickListener mIOnInvoiceConfirmationViewPODClickListener;

    public static final String POD_PENDING = "pending";
    /*public static final String POD_UNVERIFIED = "unverified";
    public static final String POD_DELIVERED = "completed";*/

    public interface IOnInvoiceConfirmationViewPODClickListener {
        void onDeliveredViewPODClicked(InvoiceConfirmationParser invoiceConfirmationParser);
    }

    public InvoiceConfirmationAdapter(BaseActivity activity,
                                      List<InvoiceConfirmationParser> invoiceConfirmationParserList, String roles,
                                      IOnInvoiceConfirmationViewPODClickListener iOnInvoiceConfirmationViewPODClickListener) {
        this.activity = activity;
        this.dataList = invoiceConfirmationParserList;
        this.roles = roles;
        this.mIOnInvoiceConfirmationViewPODClickListener = iOnInvoiceConfirmationViewPODClickListener;
    }

    class MyViewHolder extends RecyclerView.ViewHolder {
        TextView tvBookingId, tvCustomerName, fromCityTv, toCityTv;
        TextView tvLoadingDate, tvVehicleNumber, tvWeight, tvRate;
        TextView tvStatus, tvLocation, tvComment, tvViewPOD;
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
            tvComment = view.findViewById(R.id.tvComment);
            tvLocation = view.findViewById(R.id.tvLocation);
            tvViewPOD = view.findViewById(R.id.tvViewPOD);
            cardView = view.findViewById(R.id.card_view);

            tvViewPOD.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    InvoiceConfirmationParser parser = dataList.get(getAdapterPosition());
                    // make interface which will interact with activity from here
                    mIOnInvoiceConfirmationViewPODClickListener.onDeliveredViewPODClicked(parser);
                }
            });
        }
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.row_invoice_confirmation, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        InvoiceConfirmationParser parser = dataList.get(position);

        String podStatus = parser.podStatus;
        if (podStatus.equalsIgnoreCase(POD_PENDING)) {
            // POD not uploaded yet hide view POD button
            holder.tvViewPOD.setVisibility(View.GONE);
        } else {
            // Allow user to view pod
            holder.tvViewPOD.setVisibility(View.VISIBLE);
        }

        holder.fromCityTv.setText(Utils.def(parser.fromCity, ""));
        holder.toCityTv.setText(Utils.def(parser.toCity, ""));

        // set booking Id field
        String bookingId = String.valueOf(parser.bookingId);
        if (TextUtils.isEmpty(bookingId) || bookingId.equalsIgnoreCase("null")) {
            bookingId = "-";
        }
        holder.tvBookingId.setText(bookingId);

        // set customer Name field
        String customerName = String.valueOf(parser.customerName);
        if (TextUtils.isEmpty(customerName) || customerName.equalsIgnoreCase("null")) {
            customerName = "-";
        }
        holder.tvCustomerName.setText(customerName);

        // set vehicle number field
        String vehicleNumber = String.valueOf(parser.vehicleNumber);
        if (TextUtils.isEmpty(vehicleNumber) || vehicleNumber.equalsIgnoreCase("null")) {
            vehicleNumber = "-";
        }

        // set LR number field
        String lrNumber = String.valueOf(parser.lrNumber);
        if (TextUtils.isEmpty(lrNumber) || lrNumber.equalsIgnoreCase("null")) {
            lrNumber = " ";
        } else {
            lrNumber = " (" + lrNumber + ") ";
        }
        holder.tvVehicleNumber.setText(vehicleNumber + lrNumber);

        // set weight field
        String weight = String.valueOf(parser.weight);
        if (weight == null || weight.equalsIgnoreCase("null")) {
            weight = "-";
        }
        holder.tvWeight.setText(weight);

        // set rate field
        String rate = String.valueOf(parser.rate);
        if (rate == null || rate.equalsIgnoreCase("null")) {
            rate = "-";
        }
        holder.tvRate.setText(rate);

        // set booking status field
        String status = String.valueOf(parser.bookingStatusCurrent);
        if (TextUtils.isEmpty(status) || status.equalsIgnoreCase("null")) {
            status = "-";
        }
        holder.tvStatus.setText(status);

        // set latest comment & comment created on field
        String comment = String.valueOf(parser.bookingStatusComment);
        if (TextUtils.isEmpty(comment) || comment.equalsIgnoreCase("null")) {
            comment = "-";
        } else {
            String bookingStatusCommentCreatedOn = parser.bookingStatusCommentCreatedOn;
            if (TextUtils.isEmpty(bookingStatusCommentCreatedOn) || bookingStatusCommentCreatedOn.equalsIgnoreCase("null")) {
                comment = "-";
            } else {
                comment = comment + "\n" + bookingStatusCommentCreatedOn;
            }
        }
        holder.tvComment.setText(comment);

        // set color according to bookingStatusMappingStage,
        // if it escalated then show in red color else as usual card view
        String bookingStatusMappingStage = parser.bookingStatusMappingStage;
        if (TextUtils.isEmpty(bookingStatusMappingStage) || bookingStatusMappingStage.equalsIgnoreCase("null")
                || !bookingStatusMappingStage.equalsIgnoreCase("escalated")) {
            // means this is other than escalated booking set normal color
            holder.cardView.setCardBackgroundColor(Color.WHITE);
        } else {
            // means this is escalated booking set red color
            holder.cardView.setCardBackgroundColor(
                    ContextCompat.getColor(activity,R.color.colorLightRed));
        }

        // set move to top visibility
        ((InvoiceConfirmationActivity) activity).setMoveToTopVisibility(position);
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }


}