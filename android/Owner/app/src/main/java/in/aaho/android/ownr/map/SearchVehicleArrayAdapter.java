package in.aaho.android.ownr.map;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Filter;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.List;

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.booking.City;
import in.aaho.android.ownr.booking.LocationFormAdapter;
import in.aaho.android.ownr.vehicles.VehicleNumber;

/**
 * Created by mani on 11/8/16.
 */

public class SearchVehicleArrayAdapter extends ArrayAdapter<TrackingData>
        implements AdapterView.OnItemSelectedListener, AdapterView.OnItemClickListener {

    private static final int MAX_RESULTS = 20;
    private TrackSelectListener listener;

    private Context context;

    private int resource, textViewResourceId;
    private List<TrackingData> items, tempItems, suggestions;
    private VehicleFilter vehicleFilter = new VehicleFilter(MAX_RESULTS);


    public SearchVehicleArrayAdapter(Context context, List<TrackingData> items, TrackSelectListener listener) {
        super(context, R.layout.autocomplete_list_item, R.id.autocomplete_list_text, items);
        this.context = context;
        this.listener = listener;
        this.resource = R.layout.autocomplete_list_item;
        this.textViewResourceId = R.id.autocomplete_list_text;
        this.items = items;
        tempItems = new ArrayList<>(items); // this makes the difference.
        suggestions = new ArrayList<>();
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        View view = convertView;
        if (convertView == null) {
            LayoutInflater inflater = (LayoutInflater) context.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
            view = inflater.inflate(resource, parent, false);
        }
        TrackingData data = items.get(position);
        if (data != null) {
            TextView lblName = view.findViewById(textViewResourceId);
            if (lblName != null)
                lblName.setText(data.getAutocompleteText());
        }
        return view;
    }

    @Override
    public Filter getFilter() {
        return vehicleFilter;
    }

    @Override
    public void onItemSelected(AdapterView<?> adapterView, View view, int i, long l) {
        listener.onSelect(items.get(i));
    }

    @Override
    public void onNothingSelected(AdapterView<?> adapterView) {
        listener.onSelect(null);
    }

    @Override
    public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
        listener.onSelect(items.get(position));
    }


    /**
     * Custom Filter implementation for custom suggestions we provide.
     */
    private class VehicleFilter extends Filter {

        private int maxResults;

        public VehicleFilter(int maxResults) {
            this.maxResults = maxResults;
        }

        @Override
        public CharSequence convertResultToString(Object resultValue) {
            String str = ((TrackingData) resultValue).getVehicleNumberSearchString();
            return str;
        }

        private void resetSuggestions(String query) {
            tempItems = MapActivity.trackListNew;
            suggestions.clear();

            if (query == null || query.trim().length() == 0) {
                int resultCount = Math.min(maxResults, items.size());
                for (int i = 0; i < resultCount; i++) {
                    suggestions.add(items.get(i));
                }
                return;
            }

            String searchQuery = VehicleNumber.compareFormat(query);
            List<TrackingData> startswithMatches = new ArrayList<>();
            List<TrackingData> containsMatches = new ArrayList<>();

            for (TrackingData data : tempItems) {
                String vehicleNoString = data.getVehicleNumberSearchString();
                if (vehicleNoString.startsWith(searchQuery)) {
                    startswithMatches.add(data);
                }
                if (vehicleNoString.contains(searchQuery)) {
                    containsMatches.add(data);
                }
            }

            //suggestions.addAll(startswithMatches);
            if (suggestions.size() < maxResults) {
                suggestions.addAll(containsMatches);
            }

            if (suggestions.size() > maxResults) {
                suggestions.subList(maxResults, suggestions.size()).clear();
            }
        }

        private FilterResults newFilterResults() {
            FilterResults filterResults = new FilterResults();
            filterResults.values = suggestions;
            filterResults.count = suggestions.size();
            return filterResults;
        }

        @Override
        protected FilterResults performFiltering(CharSequence constraint) {
            String query = constraint == null ? null : constraint.toString().trim().toLowerCase();
            resetSuggestions(query);
            return newFilterResults();
        }

        @Override
        protected void publishResults(CharSequence constraint, FilterResults results) {
            List<TrackingData> filterList = (ArrayList<TrackingData>) results.values;
            if (filterList != null && results.count > 0) {
                clear();
                for (TrackingData data : filterList) {
                    add(data);
                }
                notifyDataSetChanged();
            }
        }
    }
}