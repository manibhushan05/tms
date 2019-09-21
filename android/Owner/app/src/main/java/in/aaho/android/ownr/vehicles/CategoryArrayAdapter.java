package in.aaho.android.ownr.vehicles;

import android.content.Context;
import android.graphics.Color;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.List;

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.booking.VehicleCategory;

/**
 * Created by shobhit on 11/8/16.
 */

public class CategoryArrayAdapter extends ArrayAdapter<VehicleCategory> implements AdapterView.OnItemSelectedListener, AdapterView.OnItemClickListener {

    private Context context;
    private CategorySelectListener listener;

    private int resource, textViewResourceId;
    private List<VehicleCategory> items;

    public interface CategorySelectListener {
        void onCategorySelect(VehicleCategory vehicleCategory);
    }

    public static CategoryArrayAdapter getNew(Context context, List<VehicleCategory> items, CategorySelectListener listener) {
        List<VehicleCategory> spinnerItems = new ArrayList<>();
        spinnerItems.add(VehicleCategory.EMPTY_VEHICLE_SPINNER);
        spinnerItems.addAll(items);
        return new CategoryArrayAdapter(context, spinnerItems, listener);
    }


    private CategoryArrayAdapter(Context context, List<VehicleCategory> items, CategorySelectListener listener) {
        super(context, R.layout.spinner_list_item, R.id.spinner_list_text, items);
        this.listener = listener;
        this.context = context;
        this.resource = R.layout.spinner_list_item;
        this.textViewResourceId = R.id.spinner_list_text;
        this.items = items;
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        View view = convertView;
        if (convertView == null) {
            LayoutInflater inflater = (LayoutInflater) context.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
            view = inflater.inflate(resource, parent, false);
        }
        VehicleCategory vehicleCategory = items.get(position);
        if (vehicleCategory != null) {
            TextView lblName = view.findViewById(textViewResourceId);
            if (lblName != null) {
                if (vehicleCategory.id == -1) {
                    lblName.setTextColor(Color.parseColor("#999999"));
                } else {
                    lblName.setTextColor(Color.parseColor("#333333"));
                }
                lblName.setText(vehicleCategory.getFullName());
            }
        }
        return view;
    }

    @Override
    public void onItemSelected(AdapterView<?> adapterView, View view, int position, long id) {
        if (listener != null) {
            listener.onCategorySelect(items.get(position));
        }
    }

    @Override
    public void onNothingSelected(AdapterView<?> adapterView) {
        if (listener != null) {
            listener.onCategorySelect(null);
        }
    }

    @Override
    public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
        if (listener != null) {
            listener.onCategorySelect(items.get(position));
        }
    }

}