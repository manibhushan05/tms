package in.aaho.android.ownr.booking;

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.RelativeLayout;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.ownr.R;

/**
 * Created by mani on 19/9/17.
 */

public class CompletedBookingAdapter extends RecyclerView.Adapter<CompletedBookingAdapter.MyViewHolder> {

    private List<CompletedBookingData> dataList;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        private String bookingID;
        private TextView tvPickUpFrom;
        private TextView tvDropAt;
        private TextView tvShipmentDate;
        private TextView tvLrNumber;
        private TextView tvTotalAmount;
        private TextView tvLastPaymentDate;
        private TextView tvVehicleNumber;

        public MyViewHolder(View view) {
            super(view);
            tvPickUpFrom = view.findViewById(R.id.tvNumberOfBookingsValue);
            tvDropAt = view.findViewById(R.id.tvTotalAmountValue);
            tvShipmentDate = view.findViewById(R.id.tvInTransitShipmentDate);
            tvLrNumber = view.findViewById(R.id.tvInTransitLrNumbers);
            tvTotalAmount = view.findViewById(R.id.tvInTransitAmount);
            tvLastPaymentDate = view.findViewById(R.id.tvInTransitBalance);
            tvVehicleNumber = view.findViewById(R.id.tvInTransitVehicleNumber);
            RelativeLayout relativeLayout = view.findViewById(R.id.rlInTransitMainContent);
            relativeLayout.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
//                    CompleteTripDetails.getCompleteTripDetails(v, tvTransactionId.getText().toString());
                }
            });
        }
    }


    public CompletedBookingAdapter(List<CompletedBookingData> dataList) {
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
        CompletedBookingData completedBookingData = dataList.get(position);
        holder.bookingID = completedBookingData.getBookingId();
        holder.tvPickUpFrom.setText(completedBookingData.getPickupFrom());
        holder.tvDropAt.setText(completedBookingData.getDropAt());
        holder.tvShipmentDate.setText(completedBookingData.getShipmentDate());
        holder.tvLrNumber.setText(completedBookingData.getLrNumber());
        holder.tvTotalAmount.setText(completedBookingData.getTotalAmount());
        holder.tvLastPaymentDate.setText(completedBookingData.getLastPaymentDate());
        holder.tvVehicleNumber.setText(completedBookingData.getVehicleNumber());
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }
}
