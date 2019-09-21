package in.aaho.android.ownr.transaction;

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.ownr.R;

/**
 * Created by mani on 18/09/17.
 */

public class TripDetailsAdapter extends RecyclerView.Adapter<TripDetailsAdapter.MyViewHolder> {
    public TripDetailsAdapter(List<TripBasicData> dataList) {
        this.dataList = dataList;
    }

    private List<TripBasicData> dataList;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        TextView tvLabel;
        TextView tvValue;

        public MyViewHolder(View view) {
            super(view);
            tvLabel = view.findViewById(R.id.trip_detail_content_label);
            tvValue = view.findViewById(R.id.trip_detail_content_value);
        }

    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.booking_details_row1, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        TripBasicData tripBasicData = dataList.get(position);
        holder.tvLabel.setText(tripBasicData.getDataLabel());
        holder.tvValue.setText(tripBasicData.getDataValue());

    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }
}

