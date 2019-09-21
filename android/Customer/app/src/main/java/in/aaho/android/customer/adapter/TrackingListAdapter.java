package in.aaho.android.customer.adapter;

import android.support.v7.widget.CardView;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.ArrayList;

import in.aaho.android.customer.R;
import in.aaho.android.customer.data.TrackingDataList;

/**
 * Created by mani on 22/7/16.
 */

public class TrackingListAdapter extends RecyclerView.Adapter<TrackingListAdapter.UserViewHolder> {
    private ArrayList<TrackingDataList> mDataSet;

    public TrackingListAdapter(ArrayList<TrackingDataList> mDataSet) {
        this.mDataSet = mDataSet;
    }

    @Override
    public UserViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View v = LayoutInflater.from(parent.getContext()).inflate(R.layout.tracking_list_row, parent, false);
        UserViewHolder userViewHolder = new UserViewHolder(v);
        return userViewHolder;
    }

    @Override
    public void onBindViewHolder(UserViewHolder holder, int position) {
        holder.tvTransactionID.setText(mDataSet.get(position).getTransactionId());
        holder.tvStatus.setText(mDataSet.get(position).getStatus());
        holder.tvPickupFrom.setText(mDataSet.get(position).getPickupFrom());
        holder.tvDropAt.setText(mDataSet.get(position).getdropAt());
        holder.tvStartedOn.setText(mDataSet.get(position).getStartedOn());
        holder.tvLastLocation.setText(mDataSet.get(position).getLastKnownLocation());
        holder.tvLastLocationTime.setText("on "+mDataSet.get(position).getCurrentDateTime());
    }

    @Override
    public int getItemCount() {
        return mDataSet.size();
    }

    public static class UserViewHolder extends RecyclerView.ViewHolder {
        CardView cardView;
        TextView tvTransactionID;
        TextView tvStatus;
        TextView tvPickupFrom;
        TextView tvDropAt;
        TextView tvStartedOn;
        TextView tvLastLocation;
        TextView tvLastLocationTime;


        UserViewHolder(View itemView) {
            super(itemView);
            cardView = (CardView) itemView.findViewById(R.id.card_view_tracking_list);
            tvTransactionID = (TextView) itemView.findViewById(R.id.transaction_id);
            tvStatus = (TextView) itemView.findViewById(R.id.status);
            tvPickupFrom = (TextView) itemView.findViewById(R.id.pickup_from);
            tvDropAt = (TextView) itemView.findViewById(R.id.drop_at);
            tvStartedOn = (TextView) itemView.findViewById(R.id.started_on);
            tvLastLocation = (TextView) itemView.findViewById(R.id.last_location);
            tvLastLocationTime = (TextView) itemView.findViewById(R.id.last_location_time);
        }
    }

    @Override
    public void onAttachedToRecyclerView(RecyclerView recyclerView) {
        super.onAttachedToRecyclerView(recyclerView);
    }
}