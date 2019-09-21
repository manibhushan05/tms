package in.aaho.android.ownr.booking;

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

/**
 * Created by mani on 11/8/16.
 */

public class CityArrayAdapter extends ArrayAdapter<City> implements AdapterView.OnItemSelectedListener, AdapterView.OnItemClickListener {

    private static final int MAX_RESULTS = 20;

    private Context context;
    private LocationFormAdapter formAdapter;
    private int formPosition;

    private int resource, textViewResourceId;
    private List<City> items, tempItems, suggestions;
    private CityFilter cityFilter = new CityFilter(MAX_RESULTS);

    public void updatePosition(int position) {
        this.formPosition = position;
    }

    public static CityArrayAdapter getNew(Context context, List<City> items, LocationFormAdapter formAdapter) {
        return new CityArrayAdapter(context, new ArrayList<>(items), formAdapter);
    }


    private CityArrayAdapter(Context context, List<City> items, LocationFormAdapter formAdapter) {
        super(context, R.layout.autocomplete_list_item, R.id.autocomplete_list_text, items);
        this.formAdapter = formAdapter;
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
    public void onItemSelected(AdapterView<?> adapterView, View view, int i, long l) {
        formAdapter.setCityField(formPosition, items.get(i));
    }

    @Override
    public void onNothingSelected(AdapterView<?> adapterView) {
        formAdapter.setCityField(formPosition, null);
    }

    @Override
    public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
        formAdapter.setCityField(formPosition, items.get(position));
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