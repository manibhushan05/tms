package in.aaho.android.aahocustomers.adapter;

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.aahocustomers.R;
import in.aaho.android.aahocustomers.data.PaymentData;

/**
 * Created by mani on 2/8/16.
 */
public class TripPaymentInfoAdapter extends RecyclerView.Adapter<TripPaymentInfoAdapter.MyViewHolder> {
    private List<PaymentData> dataList;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        private TextView tvPaymentDate;
        private TextView tvAmount;
        private TextView tvPaidTo;
        private TextView tvModeOfPayment;
        private TextView tvRemarksLabel;
        private TextView tvRemarksValue;


        public MyViewHolder(View view) {
            super(view);
            tvPaymentDate = view.findViewById(R.id.tvAllocatedVehicleStatus);
            tvAmount = view.findViewById(R.id.tvAmount);
            tvPaidTo = view.findViewById(R.id.tvPaidToValue);
            tvModeOfPayment = view.findViewById(R.id.tvPaymentModeValue);
            tvRemarksLabel = view.findViewById(R.id.tvRemarksLabel);
            tvRemarksValue = view.findViewById(R.id.tvRemarksValue);
        }
    }


    public TripPaymentInfoAdapter(List<PaymentData> dataList) {
        this.dataList = dataList;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.payment_info_rows, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        PaymentData paymentData = dataList.get(position);
        holder.tvPaymentDate.setText(paymentData.getPaymentDate());
        holder.tvAmount.setText(paymentData.getAmount());
        holder.tvPaidTo.setText(paymentData.getPaidTo());
        holder.tvRemarksValue.setText(paymentData.getRemarks());
        holder.tvModeOfPayment.setText(paymentData.getModeOfPayment());
        holder.tvRemarksLabel.setText(paymentData.getRemarksLabel());
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }
}
