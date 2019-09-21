package in.aaho.android.customer.booking;

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

import in.aaho.android.customer.R;

/**
 * Created by shobhit on 11/8/16.
 */

public class AddressArrayAdapter extends ArrayAdapter<Address> implements AdapterView.OnItemSelectedListener, AdapterView.OnItemClickListener {

    private static final int MAX_RESULTS = 20;

    private Context context;
    private LocationFormAdapter formAdapter;
    private int formPosition;

    private int resource, textViewResourceId;
    private List<Address> items, tempItems, suggestions;
    private AddressFilter addressFilter = new AddressFilter(MAX_RESULTS);
    public static boolean shouldRefresh = false;

    public void updatePosition(int position) {
        this.formPosition = position;
    }

    public static AddressArrayAdapter getNew(Context context, List<Address> items, LocationFormAdapter formAdapter) {
        return new AddressArrayAdapter(context, new ArrayList<>(items), formAdapter);
    }


    private AddressArrayAdapter(Context context, List<Address> items, LocationFormAdapter formAdapter) {
        super(context, R.layout.autocomplete_list_item, R.id.autocomplete_list_text, items);
        this.formAdapter = formAdapter;
        this.context = context;
        this.resource = R.layout.autocomplete_list_item;
        this.textViewResourceId = R.id.autocomplete_list_text;
        this.items = items;
        tempItems = new ArrayList<>(items); // this makes the difference.
        suggestions = new ArrayList<>();
    }

    public void refresh(List<Address> newItems) {
        items.clear();
        items.addAll(newItems);

        tempItems.clear();
        tempItems.addAll(newItems);
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        if (shouldRefresh) {
            refresh(Address.getAll());
            shouldRefresh = false;
        }

        View view = convertView;
        if (convertView == null) {
            LayoutInflater inflater = (LayoutInflater) context.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
            view = inflater.inflate(resource, parent, false);
        }
        Address address = items.get(position);
        if (address != null) {
            TextView lblName = (TextView) view.findViewById(textViewResourceId);
            if (lblName != null)
                lblName.setText(address.getAutoCompleteText());
        }
        return view;
    }

    @Override
    public Filter getFilter() {
        return addressFilter;
    }

    @Override
    public void onItemSelected(AdapterView<?> adapterView, View view, int i, long l) {
        formAdapter.setAddressField(formPosition, items.get(i));
    }

    @Override
    public void onNothingSelected(AdapterView<?> adapterView) {
        formAdapter.setAddressField(formPosition, null);
    }

    @Override
    public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
        formAdapter.setAddressField(formPosition, items.get(position));
    }

    /**
     * Custom Filter implementation for custom suggestions we provide.
     */
    private class AddressFilter extends Filter {

        private int maxResults;

        public AddressFilter(int maxResults) {
            this.maxResults = maxResults;
        }

        @Override
        public CharSequence convertResultToString(Object resultValue) {
            String str = ((Address) resultValue).getFullName();
            return str;
        }

        private void resetSuggestions(String query) {
            suggestions.clear();
            City city = formAdapter.getCityField(formPosition);

            if (query == null || query.trim().length() == 0) {
                List<String> rankedAddress = Address.getRankedAddresses();
                int resultCount = Math.min(maxResults, rankedAddress.size());
                for (int i = 0; i < resultCount; i++) {
                    Address address = Address.get(rankedAddress.get(i));
                    address.setQuery(null);
                    if (city == null || address.city.id == city.id) {
                        suggestions.add(address);
                    }
                }
                return;
            }

            List<Address> startMatches = new ArrayList<>();
            List<Address> midMatches = new ArrayList<>();
            for (Address address : tempItems) {
                if (city == null || address.city.id == city.id) {
                    if (address.searchTerm().startsWith(query)) {
                        address.setQuery(query);
                        startMatches.add(address);
                    } else if (address.searchTerm().contains(query)) {
                        address.setQuery(query);
                        midMatches.add(address);
                    }
                }
            }
            Address.sortAddresses(startMatches);
            Address.sortAddresses(midMatches);
            suggestions.addAll(startMatches);
            suggestions.addAll(midMatches);

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
            List<Address> filterList = (ArrayList<Address>) results.values;
            if (filterList != null && results.count > 0) {
                clear();
                for (Address addr : filterList) {
                    add(addr);
                }
                notifyDataSetChanged();
            }
        }
    }
}