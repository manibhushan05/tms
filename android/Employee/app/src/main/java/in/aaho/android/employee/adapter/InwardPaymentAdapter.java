package in.aaho.android.employee.adapter;

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.employee.R;
import in.aaho.android.employee.models.InwardPaymentData;
import in.aaho.android.employee.models.OutwardPaymentData;

/**
 * Created by Suraj.M
 */
public class InwardPaymentAdapter extends RecyclerView.Adapter<InwardPaymentAdapter.MyViewHolder> {
    private List<InwardPaymentData> dataList;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        private TextView tvPaymentDate;
        private TextView tvAmount,tvPaidTo;
        private TextView tvModeOfPayment,tvTDS;


        public MyViewHolder(View view) {
            super(view);
            tvPaidTo = view.findViewById(R.id.tvPaidToValue);
            tvPaymentDate = view.findViewById(R.id.tvPaymentDate);
            tvModeOfPayment = view.findViewById(R.id.tvPaymentModeValue);
            tvAmount = view.findViewById(R.id.tvAmount);
            tvTDS = view.findViewById(R.id.tvTDS);
        }
    }

    public InwardPaymentAdapter(List<InwardPaymentData> dataList) {
        this.dataList = dataList;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.row_inward_payment, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        InwardPaymentData inwardPaymentData = dataList.get(position);
        holder.tvPaymentDate.setText(inwardPaymentData.getPaymentDate());
        holder.tvAmount.setText(inwardPaymentData.getAmount());
        holder.tvPaidTo.setText(inwardPaymentData.getReceivedFrom());
        holder.tvModeOfPayment.setText(inwardPaymentData.getModeOfPayment());
        holder.tvTDS.setText(inwardPaymentData.getTds());
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }
}
