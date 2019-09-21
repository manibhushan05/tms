package in.aaho.android.customer.adapter;

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.RelativeLayout;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.customer.R;
import in.aaho.android.customer.data.DeliveredTransactionData;
import in.aaho.android.customer.requests.CompleteTripDetails;

/**
 * Created by mani on 21/7/16.
 */
public class DeliveredTransactionAdapter extends RecyclerView.Adapter<DeliveredTransactionAdapter.MyViewHolder> {

    private List<DeliveredTransactionData> dataList;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        public TextView tvTransactionId;
        public TextView tvpickupFrom;
        public TextView tvdropAt;
        public TextView tvShipmentDate;
        public TextView tvNumberOfVehicle;
        public TextView tvTotalAmount;
        public TextView tvPaidAmount;
        public TextView tvBalanceAmount;
        public TextView tvMaterial;

        public MyViewHolder(View view) {
            super(view);
            tvTransactionId = (TextView) view.findViewById(R.id.tvDeliveredTransactionId);
            tvpickupFrom = (TextView) view.findViewById(R.id.tvQRPickupFrom);
            tvdropAt = (TextView) view.findViewById(R.id.tvQRDropAt);
            tvShipmentDate = (TextView) view.findViewById(R.id.tvDeliveredShipmentDate);
            tvNumberOfVehicle = (TextView) view.findViewById(R.id.tvDeliveredNumberOfTrucks);
            tvTotalAmount = (TextView) view.findViewById(R.id.tvDeliveredAmount);
//            tvMaterial = (TextView) view.findViewById(R.id.tvDeliveredMaterial);
            tvPaidAmount = (TextView)view.findViewById(R.id.tvDeliveredPaid);
            tvBalanceAmount = (TextView)view.findViewById(R.id.tvDeliveredBalance);
            RelativeLayout relativeLayout = (RelativeLayout) view.findViewById(R.id.rlDeliveredMainContent);
            relativeLayout.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    CompleteTripDetails.getCompleteTripDetails(v, tvTransactionId.getText().toString());
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
        holder.tvpickupFrom.setText(deliveredTransactionData.getpickupFrom());
        holder.tvdropAt.setText(deliveredTransactionData.getdropAt());
        holder.tvShipmentDate.setText(deliveredTransactionData.getShipmentDate());
        holder.tvNumberOfVehicle.setText(deliveredTransactionData.getNumberOfVehicle());
        holder.tvTotalAmount.setText(deliveredTransactionData.getTotalAmount());
        holder.tvPaidAmount.setText(deliveredTransactionData.getPaidAmount());
        holder.tvBalanceAmount.setText(deliveredTransactionData.getBalanceAmount());
//        holder.tvMaterial.setText(deliveredTransactionData.getMaterial());
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }
}