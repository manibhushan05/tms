package in.aaho.android.ownr.vehicles;

/**
 * Created by shobhit on 6/8/16.
 */

import android.content.Context;
import android.content.Intent;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.TextView;

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.common.ListItemListerner;
import in.aaho.android.ownr.common.Utils;


public class VehicleListAdapter extends RecyclerView.Adapter<VehicleListAdapter.MyViewHolder> {
    private final Context context;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        public TextView number, type;
        public LinearLayout item;

        public VehicleClickListener vehicleClickListener;

        public MyViewHolder(View view) {
            super(view);
            item = (LinearLayout) view;
            number = view.findViewById(R.id.text_view_first);
            type = view.findViewById(R.id.text_view_second);

            vehicleClickListener = new VehicleClickListener();

            item.setOnClickListener(vehicleClickListener);
        }

        public void updateListenerPositions(int position) {
            vehicleClickListener.updatePosition(position);
        }
    }

    public VehicleListAdapter(Context context) {
        this.context = context;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.vehicles_list_item, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        BrokerVehicle vehicle = VehicleListActivity.getVehicleList().get(position);
        holder.updateListenerPositions(position);

        /*holder.number.setText(Utils.def(vehicle.getNumber(), "-"));
        holder.type.setText(Utils.def(vehicle.getName(), "-"));*/
        holder.number.setText(Utils.def(vehicle.getNumber(), "-"));
        holder.type.setText(Utils.def(vehicle.getVehicleType(), "-"));
    }

    @Override
    public int getItemCount() {
        return VehicleListActivity.getVehicleList().size();
    }

    private class VehicleClickListener extends ListItemListerner implements View.OnClickListener {

        @Override
        public void onClick(View v) {
            VehicleDetailsActivity.position = position;
            Intent intent = new Intent(context, VehicleDetailsActivity.class);
            context.startActivity(intent);
        }
    }


}
