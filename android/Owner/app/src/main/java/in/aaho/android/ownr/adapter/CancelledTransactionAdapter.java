package in.aaho.android.ownr.adapter;

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.RelativeLayout;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.data.CancelTransactionData;

/**
 * Created by mani on 21/7/16.
 */
public class CancelledTransactionAdapter extends RecyclerView.Adapter<CancelledTransactionAdapter.MyViewHolder> {

    private List<CancelTransactionData> dataList;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        public TextView tvTransactionId;
        public TextView tvpickupFrom;
        public TextView tvdropAt;
        public TextView tvShipmentDate;
        public TextView tvNumberOfVehicle;
        public TextView tvQuoteAmount;
        public TextView tvCancellationDate;
        public TextView tvMaterial;
        public Button btnCancel;

        public MyViewHolder(View view) {
            super(view);
            tvTransactionId = view.findViewById(R.id.tvCancelTransactionId);
            tvpickupFrom = view.findViewById(R.id.tvNumberOfBookingsValue);
            tvdropAt = view.findViewById(R.id.tvTotalAmountValue);
            tvShipmentDate = view.findViewById(R.id.tvCancelShipmentDate);
            tvNumberOfVehicle = view.findViewById(R.id.tvCancelNumberOfTrucks);
            tvQuoteAmount = view.findViewById(R.id.tvCancelQuote);
//            tvMaterial = (TextView) view.findViewById(R.id.tvCancelMaterial);
            tvCancellationDate = view.findViewById(R.id.tvCancelledOn);
            RelativeLayout relativeLayout = view.findViewById(R.id.rlCancelledMainContent);
            relativeLayout.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
//                    CompleteTripDetails.getCompleteTripDetails(v, tvTransactionId.getText().toString());
                }
            });
        }
    }


    public CancelledTransactionAdapter(List<CancelTransactionData> dataList) {
        this.dataList = dataList;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.cancel_transaction_rows, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        CancelTransactionData cancelTransactionData = dataList.get(position);
        holder.tvTransactionId.setText(cancelTransactionData.getTransactionId());
        holder.tvpickupFrom.setText(cancelTransactionData.getpickupFrom());
        holder.tvdropAt.setText(cancelTransactionData.getdropAt());
        holder.tvShipmentDate.setText(cancelTransactionData.getShipmentDate());
        holder.tvNumberOfVehicle.setText(cancelTransactionData.getNumberOfVehicle());
        holder.tvQuoteAmount.setText(cancelTransactionData.getQuoteAmount());
        holder.tvCancellationDate.setText(cancelTransactionData.getCancellationDate());
//        holder.tvMaterial.setText(cancelTransactionData.getMaterial());
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }
}