package in.aaho.android.ownr.adapter;

import android.support.v7.widget.RecyclerView;
import android.text.TextUtils;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.model.DebitNoteSupplierData;

/**
 * Created by Suraj.M
 */
public class DebitNoteSupplierAdapter extends RecyclerView.Adapter<DebitNoteSupplierAdapter.MyViewHolder> {
    private List<DebitNoteSupplierData> dataList;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        private TextView tvDate;
        private TextView tvAmount,tvPaidTo;
        private TextView tvStatus,tvDebitNoteNo;


        public MyViewHolder(View view) {
            super(view);
            tvPaidTo = view.findViewById(R.id.tvPaidToValue);
            tvAmount = view.findViewById(R.id.tvAmount);
            tvDate = view.findViewById(R.id.tvDate);
            tvStatus = view.findViewById(R.id.tvStatus);
            tvDebitNoteNo = view.findViewById(R.id.tvDebitNoteNo);
        }
    }

    public DebitNoteSupplierAdapter(List<DebitNoteSupplierData> dataList) {
        this.dataList = dataList;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.row_debit_note_supplier, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        DebitNoteSupplierData data = dataList.get(position);
        // set paid to Name field
        String paidTo = String.valueOf(data.getPaidTo());
        if(TextUtils.isEmpty(paidTo) || paidTo.equalsIgnoreCase("null")) {
            paidTo = "-";
        }
        holder.tvPaidTo.setText(paidTo);
        // set amount field
        String amount = String.valueOf(data.getAmount());
        if(TextUtils.isEmpty(amount) || amount.equalsIgnoreCase("null")) {
            amount = "-";
        }
        holder.tvAmount.setText(amount);
        // set date field
        String date = String.valueOf(data.getDate());
        if(TextUtils.isEmpty(date) || date.equalsIgnoreCase("null")) {
            date = "-";
        }
        holder.tvDate.setText(date);
        // set status field
        String status = String.valueOf(data.getStatus());
        if(TextUtils.isEmpty(status) || status.equalsIgnoreCase("null")) {
            status = "-";
        }
        holder.tvStatus.setText(status);
        // set debit Note No field
        String debitNoteNo = String.valueOf(data.getDebitNoteNo());
        if(TextUtils.isEmpty(debitNoteNo) || debitNoteNo.equalsIgnoreCase("null")) {
            debitNoteNo = "-";
        }
        holder.tvDebitNoteNo.setText(debitNoteNo);
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }
}
