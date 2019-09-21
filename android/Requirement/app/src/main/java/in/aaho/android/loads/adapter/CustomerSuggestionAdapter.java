package in.aaho.android.loads.adapter;

import android.app.Activity;
import android.widget.ArrayAdapter;
import android.widget.Filter;

import java.util.ArrayList;

import in.aaho.android.loads.parser.CustomerParser;

/**
 * Created by aaho on 22/04/18.
 */

public class CustomerSuggestionAdapter extends ArrayAdapter<CustomerParser> {

    protected static final String TAG = "SuggestionAdapter";
    private ArrayList<CustomerParser> suggestions;

    public CustomerSuggestionAdapter(Activity context, String nameFilter) {
        super(context, android.R.layout.simple_dropdown_item_1line);
        suggestions = new ArrayList<>();
    }

    @Override
    public int getCount() {
        return suggestions.size();
    }

    @Override
    public CustomerParser getItem(int index) {
        return suggestions.get(index);
    }

    @Override
    public Filter getFilter() {
        Filter myFilter = new Filter() {
            @Override
            protected FilterResults performFiltering(CharSequence constraint) {
                FilterResults filterResults = new FilterResults();

                try {
                    CustomerParser customerParser = new CustomerParser();
                    if (constraint != null) {
                        // A class that queries a web API, parses the data and
                        // returns an ArrayList
                        ArrayList<CustomerParser> new_suggestions = customerParser
                                .getCitySuggestionData(constraint.toString());
                        suggestions.clear();
                        if(new_suggestions != null)
                            suggestions.addAll(new_suggestions);

                        // Now assign the values and count to the FilterResults object
                        filterResults.values = suggestions;
                        filterResults.count = suggestions.size();
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }

                return filterResults;
            }

            @Override
            protected void publishResults(CharSequence contraint,
                                          FilterResults results) {
                if (results != null && results.count > 0) {
                    notifyDataSetChanged();
                } else {
                    notifyDataSetInvalidated();
                }
            }

        };
        return myFilter;
    }

}

