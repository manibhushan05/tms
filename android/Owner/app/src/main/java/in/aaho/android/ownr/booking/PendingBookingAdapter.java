package in.aaho.android.ownr.booking;

import android.content.Context;
import android.content.Intent;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.RelativeLayout;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.data.ConfirmedTransactionData;
import in.aaho.android.ownr.transaction.TripDetailsActivity;

/**
 * Created by mani on 19/9/17.
 */

public class PendingBookingAdapter extends RecyclerView.Adapter<PendingBookingAdapter.MyViewHolder> {
    private List<ConfirmedTransactionData> dataList;
    private final Context context = null;


    public class MyViewHolder extends RecyclerView.ViewHolder {
        private TextView tvTransactionId;
        String trans_id;
        private TextView tvPickUpFrom;
        private TextView tvDropAt;
        private TextView tvShipmentDate;
        private TextView tvLrNumber;
        private TextView tvTotalAmount;
        private TextView tvBalance;
        private TextView tvPaid;
        private TextView tvVehicleNumber;
        public LinearLayout item;

        public MyViewHolder(View view) {
            super(view);
//            item = (LinearLayout) view;
//            tvTransactionId = (TextView) view.findViewById(R.id.tvCnfTransactionID);
            tvPickUpFrom = view.findViewById(R.id.tvNumberOfBookingsValue);
            tvDropAt = view.findViewById(R.id.tvTotalAmountValue);
            tvShipmentDate = view.findViewById(R.id.tvCnfShipmentDate);
            tvLrNumber = view.findViewById(R.id.tvCnfLrNumber);
            tvTotalAmount = view.findViewById(R.id.tvConfirmedAmount);
            tvBalance = view.findViewById(R.id.tvConfirmedBalance);
            tvPaid = view.findViewById(R.id.tvConfirmedPaid);
            tvVehicleNumber = view.findViewById(R.id.tvConfirmVehicleNumber);
            RelativeLayout relativeLayout = view.findViewById(R.id.rlCnfMainContent);
            relativeLayout.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    Intent intent = new Intent(v.getContext(), TripDetailsActivity.class);
                    intent.putExtra("trans_id", trans_id);
                    v.getContext().startActivity(intent);
                }
            });
        }
    }

    public PendingBookingAdapter(List<ConfirmedTransactionData> dataList) {
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
        holder.trans_id = confirmedTransactionData.getAllocatedVehicleId();
        holder.tvPickUpFrom.setText(confirmedTransactionData.getpickupFrom());
        holder.tvDropAt.setText(confirmedTransactionData.getdropAt());
        holder.tvShipmentDate.setText(confirmedTransactionData.getShipmentDate());
        holder.tvLrNumber.setText(confirmedTransactionData.getLrNumber());
        holder.tvTotalAmount.setText(confirmedTransactionData.getTotalAmount());
        holder.tvBalance.setText(confirmedTransactionData.getBalance());
        holder.tvPaid.setText(confirmedTransactionData.getPaid());
        holder.tvVehicleNumber.setText(confirmedTransactionData.getVehicleNumber());
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }
}
