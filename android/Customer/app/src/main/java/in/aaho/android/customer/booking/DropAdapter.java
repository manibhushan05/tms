package in.aaho.android.customer.booking;

/**
 * Created by shobhit on 6/8/16.
 */

import android.support.v7.widget.CardView;
import android.support.v7.widget.RecyclerView;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.RelativeLayout;

import java.util.List;

import in.aaho.android.customer.common.InstantAutoComplete;
import in.aaho.android.customer.common.InstantFocusListener;
import in.aaho.android.customer.common.ListItemListerner;
import in.aaho.android.customer.R;


public class DropAdapter extends RecyclerView.Adapter<DropAdapter.MyViewHolder> implements LocationFormAdapter {

    private BookingActivity bookingActivity;
    private List<DropForm> dropList;

    @Override
    public City getCityField(int position) {
        return dropList.get(position).getCity();
    }

    @Override
    public void setCityField(int position, City city) {
        dropList.get(position).setCity(city);
        notifyItemChanged(position);
    }

    @Override
    public void setAddressField(int position, Address address) {
        dropList.get(position).setAddress(address.getFullName());
        dropList.get(position).setCity(address.city);
        notifyItemChanged(position);
    }

    @Override
    public Address getAddressField(int position) {
        return Address.get(dropList.get(position).getAddress());
    }

    public class MyViewHolder extends RecyclerView.ViewHolder {
        public CardView cardView;
        public InstantAutoComplete city, address;
        public Button addDrop, delDrop;
        public RelativeLayout addDropLayout;

        public AddressTextWatcher addrTextWatcher;
        public AddDropClickListener addDropClickListener;
        public DelDropClickListener delDropClickListener;
        public CityArrayAdapter cityArrayAdapter;
        public CityClickListener cityClickListener;
        public InstantFocusListener addressFocusListener;
        public InstantFocusListener cityFocusListener;
        public AddressArrayAdapter addressArrayAdapter;

        public MyViewHolder(View view) {
            super(view);
            cardView = (CardView) view;
            city = (InstantAutoComplete) view.findViewById(R.id.drop_city_edit_text);
            address = (InstantAutoComplete) view.findViewById(R.id.drop_addr_edit_text);
            addDrop = (Button) view.findViewById(R.id.more_drop_addr_btn);
            delDrop = (Button) view.findViewById(R.id.del_drop_addr_btn);
            addDropLayout = (RelativeLayout) view.findViewById(R.id.drop_add_layout);

            addrTextWatcher = new AddressTextWatcher();
            addDropClickListener = new AddDropClickListener();
            delDropClickListener = new DelDropClickListener();
            cityClickListener = new CityClickListener(city);
            cityFocusListener =  new InstantFocusListener(city);
            addressFocusListener = new InstantFocusListener(address);
            cityArrayAdapter = CityArrayAdapter.getNew(bookingActivity, City.getAll(), DropAdapter.this);
            addressArrayAdapter = AddressArrayAdapter.getNew(bookingActivity, Address.getAll(), DropAdapter.this);

            address.addTextChangedListener(addrTextWatcher);
            addDrop.setOnClickListener(addDropClickListener);
            delDrop.setOnClickListener(delDropClickListener);
            city.setOnClickListener(cityClickListener);

            city.setAdapter(cityArrayAdapter);
            city.setOnItemSelectedListener(cityArrayAdapter);
            city.setOnItemClickListener(cityArrayAdapter);
            city.setOnClickListener(cityClickListener);
            city.setOnFocusChangeListener(cityFocusListener);

            address.setAdapter(addressArrayAdapter);
            address.setOnItemSelectedListener(addressArrayAdapter);
            address.setOnItemClickListener(addressArrayAdapter);
            address.setOnFocusChangeListener(addressFocusListener);
        }

        public void updateListenerPositions(int position) {
            addressArrayAdapter.updatePosition(position);
            cityArrayAdapter.updatePosition(position);
            cityClickListener.updatePosition(position);
            addrTextWatcher.updatePosition(position);
            addDropClickListener.updatePosition(position);
            delDropClickListener.updatePosition(position);
        }
    }


    public DropAdapter(List<DropForm> dropList, BookingActivity bookingActivity) {
        this.dropList = dropList;
        this.bookingActivity = bookingActivity;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.booking_drop_card, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        DropForm drop = dropList.get(position);
        holder.updateListenerPositions(position);
        if (drop.getCity() != null) {
            holder.city.setText(drop.getCity().getFullName());
            holder.city.setFocusable(false);
            holder.address.requestFocus();
        } else {
            holder.city.setText("");
            holder.city.setFocusableInTouchMode(true);
            holder.city.setFocusable(true);
        }
        if (drop.getAddress() != null) {
            holder.address.setText(drop.getAddress());
        } else {
            holder.address.setText("");
        }
        if (drop.getCity() != null && holder.address.getText().length() == 0) {
            holder.address.requestFocus();
        } else {
            holder.cardView.requestFocus();
        }
        if (position == 0) {  // add visible at first position
            holder.addDropLayout.setVisibility(View.VISIBLE);
            holder.delDrop.setVisibility(View.GONE);
        } else if (position == dropList.size() - 1) {  // remove visible at last position
            holder.addDropLayout.setVisibility(View.GONE);
            holder.delDrop.setVisibility(View.VISIBLE);
        } else {  // nothing in between
            holder.addDropLayout.setVisibility(View.GONE);
            holder.delDrop.setVisibility(View.GONE);
        }
    }

    @Override
    public int getItemCount() {
        return dropList.size();
    }


    private class AddDropClickListener extends ListItemListerner implements View.OnClickListener {

        @Override
        public void onClick(View v) {
            addDropForm();
        }
    }


    private void addDropForm() {
        dropList.add(new DropForm());
        this.notifyItemInserted(dropList.size() - 1);
        if (dropList.size() - 2 >= 0) {
            this.notifyItemChanged(dropList.size() - 2);
        }
    }

    private class DelDropClickListener extends ListItemListerner implements View.OnClickListener {

        @Override
        public void onClick(View v) {
            delDropForm(position);
        }
    }

    private void delDropForm(int position) {
        dropList.remove(position);
        this.notifyItemRemoved(position);
        if (dropList.size() > 0) {
            this.notifyItemChanged(dropList.size() - 1);
        }
    }


    private class CityClickListener extends ListItemListerner implements View.OnClickListener {

        private InstantAutoComplete cityView;

        public CityClickListener(InstantAutoComplete cityView) {
            this.cityView = cityView;
        }

        @Override
        public void onClick(View v) {
            Log.e("[CityClickListener]", "onClick");
            dropList.get(position).setCity(null);
            cityView.setText("");
            cityView.setFocusableInTouchMode(true);
            cityView.setFocusable(true);
            cityView.requestFocus();
        }
    }

    private class AddressTextWatcher extends ListEditTextWatcher {

        @Override
        public void onTextChanged(CharSequence s, int start, int before, int count) {
            dropList.get(position).setAddress(s.toString());
        }
    }
}
