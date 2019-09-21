package in.aaho.android.ownr.booking;

/**
 * Created by mani on 6/8/16.
 */

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.ownr.common.ListItemListerner;
import in.aaho.android.ownr.R;


public class ShipDialogAdapter extends RecyclerView.Adapter<ShipDialogAdapter.MyViewHolder> {

    private List<Shipment> shipList;
    private ShipmentDialogFragment shipmentDialogFragment;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        public TextView truck;
        public EditText count;
        public ImageButton plusBtn, minusBtn;

        public TruckCountChangeClickListener truckCountPlusListener;
        public TruckCountChangeClickListener truckCountMinusListener;

        public MyViewHolder(View view) {
            super(view);
            count = view.findViewById(R.id.ship_dialog_truck_count_edit_text);
            plusBtn = view.findViewById(R.id.ship_dialog_truck_count_plus_btn);
            minusBtn = view.findViewById(R.id.ship_dialog_truck_count_minus_btn);
            truck = view.findViewById(R.id.ship_dialog_truck_type);

            truckCountPlusListener = new TruckCountChangeClickListener(1, count);
            truckCountMinusListener = new TruckCountChangeClickListener(-1, count);

            plusBtn.setOnClickListener(truckCountPlusListener);
            minusBtn.setOnClickListener(truckCountMinusListener);
        }

        public void updateListenerPositions(int position) {
            truckCountPlusListener.updatePosition(position);
            truckCountMinusListener.updatePosition(position);
        }
    }

    public ShipDialogAdapter(List<Shipment> shipList, ShipmentDialogFragment shipmentDialogFragment) {
        this.shipList = shipList;
        this.shipmentDialogFragment = shipmentDialogFragment;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.booking_ship_dialog_card, parent, false);

        return new MyViewHolder(itemView);
    }


    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        Shipment ship = shipList.get(position);
        holder.updateListenerPositions(position);
        if (ship.getTruck() != null) {
            holder.truck.setText(ship.getTruck());
        }
        holder.count.setText(String.valueOf(ship.getCount()));
        if (ship.getCount() == 0) {
            holder.minusBtn.setEnabled(false);
        } else {
            holder.minusBtn.setEnabled(true);
        }
    }

    @Override
    public int getItemCount() {
        return shipList.size();
    }

    private class TruckCountChangeClickListener extends ListItemListerner implements View.OnClickListener {
        private EditText countEditText;
        private int value;

        public TruckCountChangeClickListener(int value, EditText countEditText) {
            this.value = value;
            this.countEditText = countEditText;
        }

        @Override
        public void onClick(View v) {
            Shipment ship = shipList.get(position);
            int newCount = ship.getCount() + value;
            if (newCount < 0) {
                return;
            }
            ship.setCount(newCount);
            countEditText.setText(String.valueOf(newCount));
            shipmentDialogFragment.updateTruckCount();
        }
    }

}
