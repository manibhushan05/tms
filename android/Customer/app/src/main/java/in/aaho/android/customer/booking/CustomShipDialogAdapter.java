package in.aaho.android.customer.booking;

/**
 * Created by shobhit on 6/8/16.
 */

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.EditText;
import android.widget.ImageButton;

import java.util.List;

import in.aaho.android.customer.common.ListItemListerner;
import in.aaho.android.customer.R;


public class CustomShipDialogAdapter extends RecyclerView.Adapter<CustomShipDialogAdapter.MyViewHolder> {

    private List<CustomShipment> shipList;
    private ShipmentDialogFragment shipmentDialogFragment;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        public EditText count;
        public EditText name, capacity;
        public ImageButton plusBtn, minusBtn, closeBtn;

        public TruckCountChangeClickListener truckCountPlusListener;
        public TruckCountChangeClickListener truckCountMinusListener;
        public CloseClickListener closeClickListener;

        public NameTextWatcher nameTextWatcher;
        public CapacityTextWatcher capacityTextWatcher;

        public MyViewHolder(View view) {
            super(view);
            count = (EditText) view.findViewById(R.id.custom_ship_dialog_truck_count_edit_text);
            plusBtn = (ImageButton) view.findViewById(R.id.custom_ship_dialog_truck_count_plus_btn);
            minusBtn = (ImageButton) view.findViewById(R.id.custom_ship_dialog_truck_count_minus_btn);
            closeBtn = (ImageButton) view.findViewById(R.id.custom_ship_close_btn);
            name = (EditText) view.findViewById(R.id.custom_ship_dialog_truck_name);
            capacity = (EditText) view.findViewById(R.id.custom_ship_dialog_truck_capacity);

            truckCountPlusListener = new TruckCountChangeClickListener(1, name, capacity, count);
            truckCountMinusListener = new TruckCountChangeClickListener(-1, name, capacity, count);
            closeClickListener = new CloseClickListener();
            nameTextWatcher = new NameTextWatcher(count);
            capacityTextWatcher = new CapacityTextWatcher(count);

            plusBtn.setOnClickListener(truckCountPlusListener);
            minusBtn.setOnClickListener(truckCountMinusListener);
            closeBtn.setOnClickListener(closeClickListener);
            name.addTextChangedListener(nameTextWatcher);
            capacity.addTextChangedListener(capacityTextWatcher);
        }

        public void updateListenerPositions(int position) {
            truckCountPlusListener.updatePosition(position);
            truckCountMinusListener.updatePosition(position);
            closeClickListener.updatePosition(position);
            nameTextWatcher.updatePosition(position);
            capacityTextWatcher.updatePosition(position);
        }

    }

    public CustomShipDialogAdapter(List<CustomShipment> shipList, ShipmentDialogFragment shipmentDialogFragment) {
        this.shipList = shipList;
        this.shipmentDialogFragment = shipmentDialogFragment;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.booking_custom_ship_dialog_card, parent, false);

        return new MyViewHolder(itemView);
    }


    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        CustomShipment ship = shipList.get(position);
        holder.updateListenerPositions(position);
        holder.name.setError(null);
        holder.capacity.setError(null);
        if (ship.getName() != null) {
            holder.name.setText(ship.getName());
        } else {
            holder.name.setText("");
        }
        if (ship.getCapacity() != null) {
            holder.capacity.setText(ship.getCapacity());
        } else {
            holder.capacity.setText("");
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
        private EditText nameEditText;
        private EditText capacityEditText;
        private EditText countEditText;
        private int value;

        public TruckCountChangeClickListener(int value, EditText nameEditText, EditText capacityEditText, EditText countEditText) {
            this.value = value;
            this.nameEditText = nameEditText;
            this.capacityEditText = capacityEditText;
            this.countEditText = countEditText;
        }

        @Override
        public void onClick(View v) {
            CustomShipment ship;

            try {
                ship = shipList.get(position);
            } catch (IndexOutOfBoundsException e) {
                CustomShipDialogAdapter.this.notifyDataSetChanged();
                return;
            }

            if (ship.hasNoName()) {
                nameEditText.setError("This field cannot be empty");
                return;
            }

            if (ship.hasNoCapacity()) {
                capacityEditText.setError("This field cannot be empty");
                return;
            }

            int newCount = ship.getCount() + value;
            if (newCount < 0) {
                return;
            }
            ship.setCount(newCount);
            countEditText.setText(String.valueOf(newCount));
            shipmentDialogFragment.updateTruckCount();
        }
    }

    private class CloseClickListener extends ListItemListerner implements View.OnClickListener {

        @Override
        public void onClick(View v) {
            try {
                shipList.remove(position);
            } catch (IndexOutOfBoundsException e) {
            }
            CustomShipDialogAdapter.this.notifyDataSetChanged();
            shipmentDialogFragment.updateTruckCount();
        }
    }

    private class NameTextWatcher extends ListEditTextWatcher {

        private EditText countEditText;

        public NameTextWatcher(EditText countEditText) {
            this.countEditText = countEditText;
        }

        @Override
        public void onTextChanged(CharSequence s, int start, int before, int count) {
            String newValue = s.toString();
            shipList.get(position).setName(newValue);
            updateShipCountIfRequired(position, newValue, countEditText);
        }
    }

    private class CapacityTextWatcher extends ListEditTextWatcher {

        private EditText countEditText;

        public CapacityTextWatcher(EditText countEditText) {
            this.countEditText = countEditText;
        }

        @Override
        public void onTextChanged(CharSequence s, int start, int before, int count) {
            String newValue = s.toString();
            shipList.get(position).setCapacity(newValue);
            updateShipCountIfRequired(position, newValue, countEditText);
        }
    }

    private void updateShipCountIfRequired(int position, String newValue, EditText countEditText) {
        if (newValue == null || newValue.trim().length() == 0) {
            shipList.get(position).setCount(0);
            countEditText.setText("0");
            shipmentDialogFragment.updateTruckCount();
        } else {
            countEditText.setError(null);
        }
    }

}
