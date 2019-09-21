package in.aaho.android.ownr.booking;

/**
 * Created by mani on 6/8/16.
 */

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.ownr.R;


public class CustomShipAdapter extends RecyclerView.Adapter<CustomShipAdapter.MyViewHolder> {

    private List<CustomShipment> shipList;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        public TextView truck, count;

        public MyViewHolder(View view) {
            super(view);
            truck = view.findViewById(R.id.ship_truck_type);
            count = view.findViewById(R.id.ship_truck_count);
        }
    }

    public CustomShipAdapter(List<CustomShipment> shipList) {
        this.shipList = shipList;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.booking_ship_card, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        CustomShipment ship = shipList.get(position);
        if (ship.getTruck() != null) {
            holder.truck.setText(ship.getTruck());
        }
        holder.count.setText(String.valueOf(ship.getCount()));
    }

    @Override
    public int getItemCount() {
        return shipList.size();
    }

}
