package in.aaho.android.employee.adapter;

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.employee.R;
import in.aaho.android.employee.models.OutwardPaymentData;

/**
 * Created by mani on 2/8/16.
 */
public class OutwardPaymentAdapter extends RecyclerView.Adapter<OutwardPaymentAdapter.MyViewHolder> {
    private List<OutwardPaymentData> dataList;

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

    public OutwardPaymentAdapter(List<OutwardPaymentData> dataList) {
        this.dataList = dataList;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.row_outward_payment, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        OutwardPaymentData outwardPaymentData = dataList.get(position);
        holder.tvPaymentDate.setText(outwardPaymentData.getPaymentDate());
        holder.tvAmount.setText(outwardPaymentData.getAmount());
        holder.tvPaidTo.setText(outwardPaymentData.getPaidTo());
        holder.tvModeOfPayment.setText(outwardPaymentData.getModeOfPayment());
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }
}
