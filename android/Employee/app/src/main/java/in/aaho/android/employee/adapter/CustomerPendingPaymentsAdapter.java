package in.aaho.android.employee.adapter;

import android.app.DatePickerDialog;
import android.support.v7.widget.CardView;
import android.support.v7.widget.RecyclerView;
import android.text.TextUtils;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.DatePicker;
import android.widget.TextView;

import java.text.DecimalFormat;
import java.util.Calendar;
import java.util.List;

import in.aaho.android.employee.R;
import in.aaho.android.employee.activity.CustomerPendingPaymentActivity;
import in.aaho.android.employee.activity.PendingPaymentsActivity;
import in.aaho.android.employee.common.BaseActivity;
import in.aaho.android.employee.common.Utils;
import in.aaho.android.employee.parser.CustomerPendingPaymentsParser;
import in.aaho.android.employee.parser.DeliveredParser;

/**
 * Created by Suraj M
 */
public class CustomerPendingPaymentsAdapter extends RecyclerView.Adapter<CustomerPendingPaymentsAdapter.MyViewHolder> {
    private final BaseActivity activity;
    private List<CustomerPendingPaymentsParser> dataList;
    private IOnCustPendingPaymentsRowListener mIOnCustPendingPaymentsRowListener;
    private IOnCustPendingPaymentsSetDueDateListener mIOnCustPendingPaymentsSetDueDateListener;
    private IOnCustPendingPaymentsCommentsListener mIOnCustPendingPaymentsCommentsListener;

    public interface IOnCustPendingPaymentsRowListener {
        void onPendingPaymentsItemClicked(CustomerPendingPaymentsParser customerPendingPaymentsParser);
    }

    public interface IOnCustPendingPaymentsSetDueDateListener {
        void onPendingPaymentsSetDueDateItemClicked(CustomerPendingPaymentsParser customerPendingPaymentsParser, String date);
    }

    public interface IOnCustPendingPaymentsCommentsListener {
        void onPendingPaymentsCommentsItemClicked(CustomerPendingPaymentsParser customerPendingPaymentsParser);
    }

    public CustomerPendingPaymentsAdapter(BaseActivity activity,
                                          List<CustomerPendingPaymentsParser> myLoadRequests,
                                          IOnCustPendingPaymentsRowListener iOnCustPendingPaymentsRowListener,
                                          IOnCustPendingPaymentsCommentsListener iIOnCustPendingPaymentsCommentsListener,
                                          IOnCustPendingPaymentsSetDueDateListener iOnCustPendingPaymentsSetDueDateListener) {
        this.activity = activity;
        this.dataList = myLoadRequests;
        this.mIOnCustPendingPaymentsRowListener = iOnCustPendingPaymentsRowListener;
        this.mIOnCustPendingPaymentsSetDueDateListener = iOnCustPendingPaymentsSetDueDateListener;
        this.mIOnCustPendingPaymentsCommentsListener = iIOnCustPendingPaymentsCommentsListener;
    }

    class MyViewHolder extends RecyclerView.ViewHolder {
        TextView tvCustomerName, tvSetPPDate, tvSetPPComments;
        TextView tvPendingInvoices, tvPendingAmount, tvOverdueInvoices;
        TextView tvOverdueAmount,tvPendingInvoicesAdjustment,tvPpDueDate;
        CardView cardView;

        MyViewHolder(View view) {
            super(view);
            tvCustomerName = view.findViewById(R.id.tvCustomerName);
            tvPendingInvoices = view.findViewById(R.id.tvPendingInvoices);
            tvPendingAmount = view.findViewById(R.id.tvPendingAmount);
            tvOverdueInvoices = view.findViewById(R.id.tvOverdueInvoices);
            tvOverdueAmount = view.findViewById(R.id.tvOverdueAmount);
            tvPendingInvoicesAdjustment = view.findViewById(R.id.tvPendingInvoicesAdjustment);
            tvPpDueDate = view.findViewById(R.id.tvPpDueDate);
            cardView = view.findViewById(R.id.card_view);
            tvSetPPDate = view.findViewById(R.id.tvSetPPDate);
            tvSetPPComments = view.findViewById(R.id.tvSetPPComments);

            cardView.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    CustomerPendingPaymentsParser customerPendingPaymentsParser = dataList.get(getAdapterPosition());
                    // make interface which will interact with activity from here
                    mIOnCustPendingPaymentsRowListener.onPendingPaymentsItemClicked(customerPendingPaymentsParser);
                }
            });

            tvSetPPDate.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    CustomerPendingPaymentsParser customerPendingPaymentsParser = dataList.get(getAdapterPosition());
                    Calendar c = Calendar.getInstance();
                    int mYear = c.get(Calendar.YEAR);
                    int mMonth = c.get(Calendar.MONTH);
                    int mDay = c.get(Calendar.DAY_OF_MONTH);
                    ValiditySetDateListener dateSetListener = new ValiditySetDateListener(customerPendingPaymentsParser);
                    DatePickerDialog datePickerDialog = new DatePickerDialog(activity, dateSetListener, mYear, mMonth, mDay);
                    datePickerDialog.show();
                    datePickerDialog.getDatePicker().setMinDate(System.currentTimeMillis() - 1000);
                }
            });

            tvSetPPComments.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    CustomerPendingPaymentsParser customerPendingPaymentsParser = dataList.get(getAdapterPosition());
                    mIOnCustPendingPaymentsCommentsListener.onPendingPaymentsCommentsItemClicked(customerPendingPaymentsParser);
                }
            });
        }

    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.row_customer_pending_payments, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        CustomerPendingPaymentsParser customerPendingPaymentsParser = dataList.get(position);

        // set customer Name field
        String customerName = String.valueOf(customerPendingPaymentsParser.customerName);
        if(TextUtils.isEmpty(customerName) || customerName.equalsIgnoreCase("null")) {
            customerName = "-";
        }
        holder.tvCustomerName.setText(customerName);

        // set pending Invoices field
        String pendingInvoices = String.valueOf(customerPendingPaymentsParser.pendingInvoices);
        if(TextUtils.isEmpty(pendingInvoices) || pendingInvoices.equalsIgnoreCase("null")) {
            pendingInvoices = "-";
        }
        holder.tvPendingInvoices.setText(pendingInvoices);

        // set overdue Invoices field
        String overdueInvoices = String.valueOf(customerPendingPaymentsParser.overdueInvoices);
        if(TextUtils.isEmpty(overdueInvoices) || overdueInvoices.equalsIgnoreCase("null")) {
            overdueInvoices = "-";
        }
        holder.tvOverdueInvoices.setText(overdueInvoices);

        // set pending Amount field
        DecimalFormat df = new DecimalFormat("#");
        df.setMaximumFractionDigits(2);
//        String pendingAmount = String.valueOf(customerPendingPaymentsParser.pendingAmount);
        String pendingAmount = df.format(customerPendingPaymentsParser.pendingAmount);
        if(TextUtils.isEmpty(pendingAmount) || pendingAmount.equalsIgnoreCase("null")) {
            pendingAmount = "-";
        }
        holder.tvPendingAmount.setText(pendingAmount);

        // set overdue Amount field
//        String overdueAmount = String.valueOf(customerPendingPaymentsParser.overdueAmount);
        String overdueAmount = df.format(customerPendingPaymentsParser.overdueAmount);
        if(TextUtils.isEmpty(overdueAmount) || overdueAmount.equalsIgnoreCase("null")) {
            overdueAmount = "-";
        }
        holder.tvOverdueAmount.setText(overdueAmount);

        // set pending Inward Adjustment Amount field
//        String pendingInwardAdjustment = String.valueOf(customerPendingPaymentsParser.pendingInwardAdjustment);
        String pendingInwardAdjustment = df.format(customerPendingPaymentsParser.pendingInwardAdjustment);
        if(TextUtils.isEmpty(pendingInwardAdjustment) || pendingInwardAdjustment.equalsIgnoreCase("null")) {
            pendingInwardAdjustment = "-";
        }
        holder.tvPendingInvoicesAdjustment.setText(pendingInwardAdjustment);

        // set Due date field
        String sme_due_date = String.valueOf(customerPendingPaymentsParser.smeDueDate);
        if(sme_due_date == null || sme_due_date.equalsIgnoreCase("null")) {
            sme_due_date = "-";
        }
        holder.tvPpDueDate.setText(sme_due_date);


        // set move to top visibility
        ((CustomerPendingPaymentActivity)activity).setMoveToTopVisibility(position);
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }

    private class ValiditySetDateListener implements DatePickerDialog.OnDateSetListener {
        private CustomerPendingPaymentsParser customerPendingPaymentsParser;
        private ValiditySetDateListener(CustomerPendingPaymentsParser customerPendingPaymentsParser){
            this.customerPendingPaymentsParser = customerPendingPaymentsParser;
        }

        @Override
        public void onDateSet(DatePicker view, int year, int monthOfYear, int dayOfMonth) {
            // make interface which will interact with activity from here
            mIOnCustPendingPaymentsSetDueDateListener.onPendingPaymentsSetDueDateItemClicked(this.customerPendingPaymentsParser,
                    Integer.toString(year)+"-"+Integer.toString(monthOfYear+1)+"-"+Integer.toString(dayOfMonth));
//            Utils.toast("Set Date: "+Integer.toString(year)+"-"+Integer.toString(monthOfYear+1)+"-"+Integer.toString(dayOfMonth));
        }
    }


}

