package in.aaho.android.ownr.booking;

/**
 * Created by mani on 6/8/16.
 */

import android.app.DatePickerDialog;
import android.app.TimePickerDialog;
import android.support.v7.widget.CardView;
import android.support.v7.widget.RecyclerView;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.DatePicker;
import android.widget.EditText;
import android.widget.RelativeLayout;
import android.widget.TimePicker;

import java.util.Calendar;
import java.util.Date;
import java.util.List;

import in.aaho.android.ownr.common.InstantAutoComplete;
import in.aaho.android.ownr.common.InstantFocusListener;
import in.aaho.android.ownr.common.ListItemListerner;
import in.aaho.android.ownr.common.Utils;
import in.aaho.android.ownr.R;


public class PickupAdapter extends RecyclerView.Adapter<PickupAdapter.MyViewHolder> implements LocationFormAdapter {

    private List<PickupForm> pickupList;
    private BookingActivity bookingActivity;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        public EditText datetime;
        public InstantAutoComplete city, address;
        public Button addPickup, delPickup;
        public RelativeLayout addPickupLayout;
        public CardView cardView;

        public AddressTextWatcher addrTextWatcher;
        public AddPickupClickListener addPickupClickListener;
        public DelPickupClickListener delPickupClickListener;
        public DatetimeClickListener datetimeClickListener;
        public CityArrayAdapter cityArrayAdapter;
        public CityClickListener cityClickListener;
        public InstantFocusListener cityFocusListener;
        public InstantFocusListener addressFocusListener;
        public AddressArrayAdapter addressArrayAdapter;

        public MyViewHolder(View view) {
            super(view);
            cardView = (CardView) view;
            city = view.findViewById(R.id.pickup_city_edit_text);
            address = view.findViewById(R.id.pickup_addr_edit_text);
            datetime = view.findViewById(R.id.pickup_datetime_edit_text);
            addPickup = view.findViewById(R.id.more_pickup_addr_btn);
            delPickup = view.findViewById(R.id.del_pickup_addr_btn);
            addPickupLayout = view.findViewById(R.id.pickup_add_layout);

            addrTextWatcher = new AddressTextWatcher();
            addPickupClickListener = new AddPickupClickListener();
            delPickupClickListener = new DelPickupClickListener();
            datetimeClickListener = new DatetimeClickListener();
            cityClickListener = new CityClickListener(city);
            cityFocusListener =  new InstantFocusListener(city);
            addressFocusListener = new InstantFocusListener(address);
            cityArrayAdapter = CityArrayAdapter.getNew(bookingActivity, City.getAll(), PickupAdapter.this);
            addressArrayAdapter = AddressArrayAdapter.getNew(bookingActivity, Address.getAll(), PickupAdapter.this);

            address.addTextChangedListener(addrTextWatcher);
            addPickup.setOnClickListener(addPickupClickListener);
            delPickup.setOnClickListener(delPickupClickListener);
            datetime.setOnClickListener(datetimeClickListener);

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
            cityClickListener.updatePosition(position);
            cityArrayAdapter.updatePosition(position);
            addrTextWatcher.updatePosition(position);
            addPickupClickListener.updatePosition(position);
            delPickupClickListener.updatePosition(position);
            datetimeClickListener.updatePosition(position);
        }

    }

    public PickupAdapter(List<PickupForm> pickupList, BookingActivity bookingActivity) {
        this.pickupList = pickupList;
        this.bookingActivity = bookingActivity;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.booking_pickup_card, parent, false);

        return new MyViewHolder(itemView);
    }


    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        PickupForm pickup = pickupList.get(position);
        holder.updateListenerPositions(position);
        if (pickup.getCity() != null) {
            holder.city.setText(pickup.getCity().getFullName());
            holder.city.setFocusable(false);
        } else {
            holder.city.setText("");
            holder.city.setFocusableInTouchMode(true);
            holder.city.setFocusable(true);
        }
        if (pickup.getAddress() != null) {
            holder.address.setText(pickup.getAddress());
        } else {
            holder.address.setText("");
        }
        if (pickup.getCity() != null && holder.address.getText().length() == 0) {
            holder.address.requestFocus();
        } else {
            holder.cardView.requestFocus();
        }
        if (pickup.getDatetime() != null) {
            holder.datetime.setText(Utils.formatDate(pickup.getDatetime()));
        } else {
            holder.datetime.setText("");
        }
        holder.datetime.setVisibility(position == 0 ? View.VISIBLE : View.GONE);
        if (position == 0) {  // add visible at first position
            holder.addPickupLayout.setVisibility(View.VISIBLE);
            holder.delPickup.setVisibility(View.GONE);
        } else if (position == pickupList.size() - 1) {  // remove visible at last position
            holder.addPickupLayout.setVisibility(View.GONE);
            holder.delPickup.setVisibility(View.VISIBLE);
        } else {  // nothing in between
            holder.addPickupLayout.setVisibility(View.GONE);
            holder.delPickup.setVisibility(View.GONE);
        }
    }

    @Override
    public int getItemCount() {
        return pickupList.size();
    }

    @Override
    public void setCityField(int position, City city) {
        pickupList.get(position).setCity(city);
        notifyItemChanged(position);
    }

    @Override
    public City getCityField(int position) {
        return pickupList.get(position).getCity();
    }

    @Override
    public void setAddressField(int position, Address address) {
        pickupList.get(position).setAddress(address.getFullName());
        pickupList.get(position).setCity(address.city);
        notifyItemChanged(position);

    }

    @Override
    public Address getAddressField(int position) {
        return Address.get(pickupList.get(position).getAddress());
    }

    private class PickupTimeSetListener implements TimePickerDialog.OnTimeSetListener {
        private int position;
        private int day;
        private int month;
        private int year;

        public PickupTimeSetListener(int position, int day, int month, int year) {
            this.position = position;
            this.day = day;
            this.month = month;
            this.year = year;
        }

        @Override
        public void onTimeSet(TimePicker view, int hourOfDay, int minute) {
            pickupList.get(position).setDatetime(Utils.getDate(year, month, day, hourOfDay, minute));
            PickupAdapter.this.notifyItemChanged(position);
        }
    }

    private class PickupDateSetListener implements DatePickerDialog.OnDateSetListener {
        private int position;
        private int currHour;
        private int currMinute;

        public PickupDateSetListener(int position, int currHour, int currMinute) {
            this.position = position;
            this.currHour = currHour;
            this.currMinute = currMinute;
        }
        @Override
        public void onDateSet(DatePicker view, int year, int monthOfYear, int dayOfMonth) {
            PickupTimeSetListener timeSetListener = new PickupTimeSetListener(position, dayOfMonth, monthOfYear, year);
            TimePickerDialog timePickerDialog = new TimePickerDialog(bookingActivity, timeSetListener, currHour, currMinute, false);
            timePickerDialog.show();
        }
    }

    private class CityClickListener extends ListItemListerner implements View.OnClickListener {

        private InstantAutoComplete cityView;

        public CityClickListener(InstantAutoComplete cityView) {
            this.cityView = cityView;
        }

        @Override
        public void onClick(View v) {
            Log.e("[Adapter]", "onClick");
            pickupList.get(position).setCity(null);
            cityView.setText("");
            cityView.setFocusableInTouchMode(true);
            cityView.setFocusable(true);
            cityView.requestFocus();
        }
    }

    private class DatetimeClickListener extends ListItemListerner implements View.OnClickListener {

        @Override
        public void onClick(View v) {
            Calendar c = Calendar.getInstance();
            Date pickedDate = pickupList.get(position).getDatetime();
            if (pickedDate != null) {
                c.setTime(pickedDate);
            }
            int mYear = c.get(Calendar.YEAR);
            int mMonth = c.get(Calendar.MONTH);
            int mDay = c.get(Calendar.DAY_OF_MONTH);
            int mHour = c.get(Calendar.HOUR_OF_DAY);
            int mMinute = c.get(Calendar.MINUTE);

            PickupDateSetListener dateSetListener = new PickupDateSetListener(position, mHour, mMinute);

            DatePickerDialog datePickerDialog = new DatePickerDialog(bookingActivity, dateSetListener, mYear, mMonth, mDay);
            datePickerDialog.show();
        }
    }


    private class AddPickupClickListener extends ListItemListerner implements View.OnClickListener {

        @Override
        public void onClick(View v) {
            addPickupForm();
        }
    }

    private void addPickupForm() {
        pickupList.add(new PickupForm());
        this.notifyItemInserted(pickupList.size() - 1);
        if (pickupList.size() - 2 >= 0) {
            this.notifyItemChanged(pickupList.size() - 2);
        }
    }


    private class DelPickupClickListener extends ListItemListerner implements View.OnClickListener {

        @Override
        public void onClick(View v) {
            delPickupForm(position);
        }
    }

    private void delPickupForm(int position) {
        pickupList.remove(position);
        this.notifyItemRemoved(position);
        if (pickupList.size() > 0) {
            this.notifyItemChanged(pickupList.size() - 1);
        }
    }

    private class AddressTextWatcher extends ListEditTextWatcher {

        @Override
        public void onTextChanged(CharSequence s, int start, int before, int count) {
            pickupList.get(position).setAddress(s.toString());
        }
    }

}
