package in.aaho.android.ownr.drivers;

/**
 * Created by mani on 6/8/16.
 */

import android.content.Context;
import android.content.Intent;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.TextView;

import in.aaho.android.ownr.common.ListItemListerner;
import in.aaho.android.ownr.common.Utils;
import in.aaho.android.ownr.R;


public class DriverListAdapter extends RecyclerView.Adapter<DriverListAdapter.MyViewHolder> {
    private final Context context;

    // private List<BrokerVehicle> vehicleList;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        public TextView name, phone;
        public LinearLayout item;

        public DriverClickListener driverClickListener;

        public MyViewHolder(View view) {
            super(view);
            item = (LinearLayout) view;
            name = view.findViewById(R.id.text_view_first);
            phone = view.findViewById(R.id.text_view_second);

            driverClickListener = new DriverClickListener();

            item.setOnClickListener(driverClickListener);
        }

        public void updateListenerPositions(int position) {
            driverClickListener.updatePosition(position);
        }
    }

    public DriverListAdapter(Context context) {
        this.context = context;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.driver_list_item, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        BrokerDriver driver = ListDriversActivity.getDriverList().get(position);
        holder.updateListenerPositions(position);
        holder.phone.setText(Utils.def(driver.getPhone(), "-"));
        holder.name.setText(Utils.def(driver.getName(), "-"));
    }

    @Override
    public int getItemCount() {
        return ListDriversActivity.getDriverList().size();
    }

    private class DriverClickListener extends ListItemListerner implements View.OnClickListener {

        @Override
        public void onClick(View v) {
            DriverDetailsActivity.position = position;
            Intent intent = new Intent(context, DriverDetailsActivity.class);
            context.startActivity(intent);
        }
    }


}
