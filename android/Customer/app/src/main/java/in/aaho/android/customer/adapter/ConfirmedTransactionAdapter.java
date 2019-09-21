package in.aaho.android.customer.adapter;

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.RelativeLayout;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.customer.R;
import in.aaho.android.customer.data.ConfirmedTransactionData;
import in.aaho.android.customer.requests.CompleteTripDetails;

/**
 * Created by mani on 21/7/16.
 */
public class ConfirmedTransactionAdapter extends RecyclerView.Adapter<ConfirmedTransactionAdapter.MyViewHolder> {

    private List<ConfirmedTransactionData> dataList;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        public TextView tvTransactionId;
        public TextView tvpickupFrom;
        public TextView tvdropAt;
        public TextView tvShipmentDate;
        public TextView tvNumberOfVehicle;
        public TextView tvTotalAmount;
        public TextView tvMaterial;

        public MyViewHolder(View view) {
            super(view);
            tvTransactionId = (TextView) view.findViewById(R.id.tvCnfTransactionID);
            tvpickupFrom = (TextView) view.findViewById(R.id.tvQRPickupFrom);
            tvdropAt = (TextView) view.findViewById(R.id.tvQRDropAt);
            tvShipmentDate = (TextView) view.findViewById(R.id.tvCnfShipmentDate);
            tvNumberOfVehicle = (TextView) view.findViewById(R.id.tvCnfNumberOfTrucks);
            tvTotalAmount = (TextView) view.findViewById(R.id.tvConfirmAmount);
            RelativeLayout  relativeLayout = (RelativeLayout)view.findViewById(R.id.rlCnfMainContent);
            relativeLayout.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    CompleteTripDetails.getCompleteTripDetails(v, tvTransactionId.getText().toString());
                }
            });
        }
    }


    public ConfirmedTransactionAdapter(List<ConfirmedTransactionData> dataList) {
        this.dataList = dataList;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.confirmed_transaction_rows, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        ConfirmedTransactionData confirmedTransactionData = dataList.get(position);
        holder.tvTransactionId.setText(confirmedTransactionData.getTransactionId());
        holder.tvpickupFrom.setText(confirmedTransactionData.getpickupFrom());
        holder.tvdropAt.setText(confirmedTransactionData.getdropAt());
        holder.tvShipmentDate.setText(confirmedTransactionData.getShipmentDate());
        holder.tvNumberOfVehicle.setText(confirmedTransactionData.getNumberOfVehicle());
        holder.tvTotalAmount.setText(confirmedTransactionData.getTotalAmount());
//        holder.tvMaterial.setText(confirmedTransactionData.getMaterial());
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }
}