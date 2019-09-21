package in.aaho.android.ownr.adapter;

import android.support.v7.widget.RecyclerView;
import android.text.TextUtils;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.model.CreditNoteSupplierData;
import in.aaho.android.ownr.model.DebitNoteSupplierData;

/**
 * Created by Suraj.M
 */
public class CreditNoteSupplierAdapter extends RecyclerView.Adapter<CreditNoteSupplierAdapter.MyViewHolder> {
    private List<CreditNoteSupplierData> dataList;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        private TextView tvDate;
        private TextView tvAmount,tvPaidTo;
        private TextView tvStatus, tvCreditNoteNo;


        public MyViewHolder(View view) {
            super(view);
            tvPaidTo = view.findViewById(R.id.tvPaidToValue);
            tvAmount = view.findViewById(R.id.tvAmount);
            tvDate = view.findViewById(R.id.tvDate);
            tvStatus = view.findViewById(R.id.tvStatus);
            tvCreditNoteNo = view.findViewById(R.id.tvCreditNoteNo);
        }
    }

    public CreditNoteSupplierAdapter(List<CreditNoteSupplierData> dataList) {
        this.dataList = dataList;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.row_credit_note_supplier, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        CreditNoteSupplierData data = dataList.get(position);
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
        // set credit Note No field
        String creditNoteNo = String.valueOf(data.getCreditNoteNo());
        if(TextUtils.isEmpty(creditNoteNo) || creditNoteNo.equalsIgnoreCase("null")) {
            creditNoteNo = "-";
        }
        holder.tvCreditNoteNo.setText(creditNoteNo);
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }
}
