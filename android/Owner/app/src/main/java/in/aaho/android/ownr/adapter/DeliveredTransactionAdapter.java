package in.aaho.android.ownr.adapter;

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.RelativeLayout;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.data.DeliveredTransactionData;

/**
 * Created by mani on 21/7/16.
 */
public class DeliveredTransactionAdapter extends RecyclerView.Adapter<DeliveredTransactionAdapter.MyViewHolder> {

    private List<DeliveredTransactionData> dataList;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        private TextView tvTransactionId;
        private TextView tvPickUpFrom;
        private TextView tvDropAt;
        private TextView tvShipmentDate;
        private TextView tvLrNumber;
        private TextView tvTotalAmount;
        private TextView tvPaidAmount;
        private TextView tvBalanceAmount;
        private TextView tvVehicleNumber;

        public MyViewHolder(View view) {
            super(view);
            tvTransactionId = view.findViewById(R.id.tvDeliveredTransactionId);
            tvPickUpFrom = view.findViewById(R.id.tvNumberOfBookingsValue);
            tvDropAt = view.findViewById(R.id.tvTotalAmountValue);
            tvShipmentDate = view.findViewById(R.id.tvDeliveredShipmentDate);
            tvLrNumber = view.findViewById(R.id.tvDeliveredLrNumber);
            tvTotalAmount = view.findViewById(R.id.tvDeliveredAmount);
//            tvMaterial = (TextView) view.findViewById(R.id.tvDeliveredMaterial);
            tvPaidAmount = view.findViewById(R.id.tvDeliveredPaid);
            tvBalanceAmount = view.findViewById(R.id.tvDeliveredBalance);
            tvVehicleNumber = view.findViewById(R.id.tvDeliveredVehicleNumber);
            RelativeLayout relativeLayout = view.findViewById(R.id.rlDeliveredMainContent);
            relativeLayout.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
//                    CompleteTripDetails.getCompleteTripDetails(v, tvTransactionId.getText().toString());
                }
            });
        }
    }


    public DeliveredTransactionAdapter(List<DeliveredTransactionData> dataList) {
        this.dataList = dataList;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.delivered_transaction_rows, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        DeliveredTransactionData deliveredTransactionData = dataList.get(position);
        holder.tvTransactionId.setText(deliveredTransactionData.getTransactionId());
        holder.tvPickUpFrom.setText(deliveredTransactionData.getpickupFrom());
        holder.tvDropAt.setText(deliveredTransactionData.getdropAt());
        holder.tvShipmentDate.setText(deliveredTransactionData.getShipmentDate());
        holder.tvLrNumber.setText(deliveredTransactionData.getLrNumber());
        holder.tvTotalAmount.setText(deliveredTransactionData.getTotalAmount());
        holder.tvPaidAmount.setText(deliveredTransactionData.getPaidAmount());
        holder.tvBalanceAmount.setText(deliveredTransactionData.getBalanceAmount());
        holder.tvVehicleNumber.setText(deliveredTransactionData.getVehicleNumber());
//        holder.tvMaterial.setText(deliveredTransactionData.getMaterial());
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }
}