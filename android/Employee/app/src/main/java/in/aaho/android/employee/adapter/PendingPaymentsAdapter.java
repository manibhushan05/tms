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
import in.aaho.android.employee.activity.PendingPaymentsActivity;
import in.aaho.android.employee.common.BaseActivity;
import in.aaho.android.employee.parser.PendingPaymentsParser;

/**
 * Created by Suraj M
 */
public class PendingPaymentsAdapter extends RecyclerView.Adapter<PendingPaymentsAdapter.MyViewHolder> {
    private final BaseActivity activity;
    private List<PendingPaymentsParser> dataList;
    private IOnPendingPaymentsUpdateListener mIOnPendingPaymentsUpdateListener;
    private IOnPendingPaymentsViewInvoiceListener mIOnPendingPaymentsViewInvoiceListener;

    public interface IOnPendingPaymentsUpdateListener {
        void onPendingPaymentsUpdateClicked(PendingPaymentsParser pendingPaymentsParser);
    }

    public interface IOnPendingPaymentsViewInvoiceListener {
        void onPendingPaymentsViewInvoiceClicked(PendingPaymentsParser pendingPaymentsParser);
    }

    public PendingPaymentsAdapter(BaseActivity activity,
                                  List<PendingPaymentsParser> myLoadRequests,
                                  IOnPendingPaymentsUpdateListener iOnPendingPaymentsUpdateListener,
                                  IOnPendingPaymentsViewInvoiceListener iOnPendingPaymentsViewInvoiceListener) {
        this.activity = activity;
        this.dataList = myLoadRequests;
        this.mIOnPendingPaymentsUpdateListener = iOnPendingPaymentsUpdateListener;
        this.mIOnPendingPaymentsViewInvoiceListener = iOnPendingPaymentsViewInvoiceListener;
    }

    class MyViewHolder extends RecyclerView.ViewHolder {
        TextView tvInvoiceNumber, tvCustomerName;
        TextView tvAmount, tvAmountToBeReceived, tvDueOn, tvInvoiceDate;
        TextView tvStatus,tvComment,tvUpdateStatus,tvViewInvoice;
        CardView cardView;

        MyViewHolder(View view) {
            super(view);
            tvInvoiceNumber = view.findViewById(R.id.tvInvoiceNumber);
            tvCustomerName = view.findViewById(R.id.tvCustomerName);
            tvAmount = view.findViewById(R.id.tvAmount);
            tvAmountToBeReceived = view.findViewById(R.id.tvAmountToBeReceived);
            tvDueOn = view.findViewById(R.id.tvDueOn);
            tvInvoiceDate = view.findViewById(R.id.tvInvoiceDate);
//            tvStatus = view.findViewById(R.id.tvStatus);
            tvComment = view.findViewById(R.id.tvComment);
            tvUpdateStatus = view.findViewById(R.id.tvUpdateStatus);
            tvViewInvoice = view.findViewById(R.id.tvViewInvoice);
            cardView = view.findViewById(R.id.card_view);

            tvUpdateStatus.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    PendingPaymentsParser pendingPaymentsParser = dataList.get(getAdapterPosition());
                    // make interface which will interact with activity from here
                    mIOnPendingPaymentsUpdateListener.onPendingPaymentsUpdateClicked(pendingPaymentsParser);
                }
            });

            tvViewInvoice.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    PendingPaymentsParser pendingPaymentsParser = dataList.get(getAdapterPosition());
                    // make interface which will interact with activity from here
                    mIOnPendingPaymentsViewInvoiceListener.onPendingPaymentsViewInvoiceClicked(pendingPaymentsParser);
                }
            });
        }

    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.row_pending_payments, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        PendingPaymentsParser pendingPaymentsParser = dataList.get(position);

        // set invoice number field
        String invoiceNumber = String.valueOf(pendingPaymentsParser.bookingId);
        if(TextUtils.isEmpty(invoiceNumber) || invoiceNumber.equalsIgnoreCase("null")) {
            invoiceNumber = "-";
        } else {
            invoiceNumber = "#"+invoiceNumber;
        }
        holder.tvInvoiceNumber.setText(invoiceNumber);

        // set customer Name field
        String customerName = String.valueOf(pendingPaymentsParser.customerName);
        if(TextUtils.isEmpty(customerName) || customerName.equalsIgnoreCase("null")) {
            customerName = "-";
        }
        holder.tvCustomerName.setText(customerName);

        // set amount field
        String amount = String.valueOf(pendingPaymentsParser.totalAmount);
        if(TextUtils.isEmpty(amount) || amount.equalsIgnoreCase("null")) {
            amount = "-";
        }
        holder.tvAmount.setText(amount);

        // set amount to be received field
        String amount_to_be_received = String.valueOf(pendingPaymentsParser.amountToBeReceived);
        if(TextUtils.isEmpty(amount_to_be_received) || amount_to_be_received.equalsIgnoreCase("null")) {
            amount_to_be_received = "-";
        }
        holder.tvAmountToBeReceived.setText(amount_to_be_received);




        // set invoice date field
        String invoice_date = String.valueOf(pendingPaymentsParser.invoiceDate);
        if(TextUtils.isEmpty(invoice_date) || invoice_date.equalsIgnoreCase("null")) {
            invoice_date = "-";
        }
        holder.tvInvoiceDate.setText(invoice_date);

        // set due on date field
        String dueOn = String.valueOf(pendingPaymentsParser.dueDate);
        if(TextUtils.isEmpty(dueOn) || dueOn.equalsIgnoreCase("null")) {
            dueOn = "-";
        }
        holder.tvDueOn.setText(dueOn);

        // set booking status field
//        String status = String.valueOf(pendingPaymentsParser.bookingStatusCurrent);
//        if(TextUtils.isEmpty(status) || status.equalsIgnoreCase("null")) {
//            status = "-";
//        }
//        holder.tvStatus.setText(status);

        // set latest comment & comment created on field
        String comment = String.valueOf(pendingPaymentsParser.bookingStatusComment);
        if(TextUtils.isEmpty(comment) || comment.equalsIgnoreCase("null")) {
            comment = "-";
        } else {
            String bookingStatusCommentCreatedOn = pendingPaymentsParser.bookingStatusCommentCreatedOn;
            if(TextUtils.isEmpty(bookingStatusCommentCreatedOn) || bookingStatusCommentCreatedOn.equalsIgnoreCase("null")) {
                comment = "-";
            } else {
                comment = comment + "\n"+bookingStatusCommentCreatedOn;
            }
        }
        holder.tvComment.setText(comment);

        // set move to top visibility
        ((PendingPaymentsActivity)activity).setMoveToTopVisibility(position);
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }


}

