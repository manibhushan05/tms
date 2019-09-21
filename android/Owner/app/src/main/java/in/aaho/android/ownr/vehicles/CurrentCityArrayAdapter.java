package in.aaho.android.ownr.vehicles;

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

/**
 * Created by shobhit on 11/8/16.
 */

public class CurrentCityArrayAdapter extends ArrayAdapter<City> implements AdapterView.OnItemSelectedListener, AdapterView.OnItemClickListener {

    private static final int MAX_RESULTS = 20;

    private Context context;
    private CitySelectListener listener;

    private int resource, textViewResourceId;
    private List<City> items, tempItems, suggestions;
    private CityFilter cityFilter = new CityFilter(MAX_RESULTS);

    public interface CitySelectListener {
        void onCitySelect(City city);
    }

    public static CurrentCityArrayAdapter getNew(Context context, List<City> items, CitySelectListener listener) {
        return new CurrentCityArrayAdapter(context, new ArrayList<>(items), listener);
    }


    private CurrentCityArrayAdapter(Context context, List<City> items, CitySelectListener listener) {
        super(context, R.layout.autocomplete_list_item, R.id.autocomplete_list_text, items);
        this.listener = listener;
        this.context = context;
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
        City city = items.get(position);
        if (city != null) {
            TextView lblName = view.findViewById(textViewResourceId);
            if (lblName != null)
                lblName.setText(city.getAutocompleteText());
        }
        return view;
    }

    @Override
    public Filter getFilter() {
        return cityFilter;
    }

    @Override
    public void onItemSelected(AdapterView<?> adapterView, View view, int position, long id) {
        if (listener != null) {
            listener.onCitySelect(items.get(position));
        }
    }

    @Override
    public void onNothingSelected(AdapterView<?> adapterView) {
        if (listener != null) {
            listener.onCitySelect(null);
        }
    }

    @Override
    public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
        if (listener != null) {
            listener.onCitySelect(items.get(position));
        }
    }



    /**
     * Custom Filter implementation for custom suggestions we provide.
     */
    private class CityFilter extends Filter {

        private int maxResults;

        public CityFilter(int maxResults) {
            this.maxResults = maxResults;
        }

        @Override
        public CharSequence convertResultToString(Object resultValue) {
            String str = ((City) resultValue).getFullName();
            return str;
        }

        private void resetSuggestions(String query) {
            suggestions.clear();

            if (query == null || query.trim().length() == 0) {
                List<Long> rankedCities = City.getRankedCities();
                int resultCount = Math.min(maxResults, rankedCities.size());
                for (int i = 0; i < resultCount; i++) {
                    City city = City.get(rankedCities.get(i));
                    city.setQuery(null);
                    suggestions.add(city);
                }
                return;
            }

            for (City city : tempItems) {
                if (city.name.toLowerCase().startsWith(query)) {
                    city.setQuery(query);
                    suggestions.add(city);
                }
            }
            City.sortCities(suggestions);
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
            List<City> filterList = (ArrayList<City>) results.values;
            if (filterList != null && results.count > 0) {
                clear();
                for (City city : filterList) {
                    add(city);
                }
                notifyDataSetChanged();
            }
        }
    }
}