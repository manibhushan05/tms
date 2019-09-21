package in.aaho.android.customer.adapter;

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.RelativeLayout;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.customer.R;
import in.aaho.android.customer.data.InTransitTransactionData;
import in.aaho.android.customer.requests.CompleteTripDetails;

/**
 * Created by mani on 21/7/16.
 */
public class InTransitTransactionAdapter extends RecyclerView.Adapter<InTransitTransactionAdapter.MyViewHolder> {

    private List<InTransitTransactionData> dataList;

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
            tvTransactionId = (TextView) view.findViewById(R.id.tvInTransitTransactionId);
            tvpickupFrom = (TextView) view.findViewById(R.id.tvQRPickupFrom);
            tvdropAt = (TextView) view.findViewById(R.id.tvQRDropAt);
            tvShipmentDate = (TextView) view.findViewById(R.id.tvInTransitShipmentDate);
            tvNumberOfVehicle = (TextView) view.findViewById(R.id.tvInTransitNumberOfTrucks);
            tvTotalAmount = (TextView) view.findViewById(R.id.tvInTransitAmount);
//            tvMaterial = (TextView) view.findViewById(R.id.tvInTransitMaterial);
            RelativeLayout  relativeLayout = (RelativeLayout)view.findViewById(R.id.rlInTransitMainContent);
            relativeLayout.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    CompleteTripDetails.getCompleteTripDetails(v, tvTransactionId.getText().toString());
                }
            });
        }
    }


    public InTransitTransactionAdapter(List<InTransitTransactionData> dataList) {
        this.dataList = dataList;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.intransit_transaction_rows, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        InTransitTransactionData inTransitTransactionData = dataList.get(position);
        holder.tvTransactionId.setText(inTransitTransactionData.getTransactionId());
        holder.tvpickupFrom.setText(inTransitTransactionData.getpickupFrom());
        holder.tvdropAt.setText(inTransitTransactionData.getdropAt());
        holder.tvShipmentDate.setText(inTransitTransactionData.getShipmentDate());
        holder.tvNumberOfVehicle.setText(inTransitTransactionData.getNumberOfVehicle());
        holder.tvTotalAmount.setText(inTransitTransactionData.getTotalAmount());
//        holder.tvMaterial.setText(inTransitTransactionData.getMaterial());
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }
}