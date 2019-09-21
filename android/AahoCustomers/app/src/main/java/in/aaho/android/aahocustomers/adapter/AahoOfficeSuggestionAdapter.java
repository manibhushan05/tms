package in.aaho.android.aahocustomers.adapter;

import android.app.Activity;
import android.widget.ArrayAdapter;
import android.widget.Filter;

import java.util.ArrayList;

import in.aaho.android.aahocustomers.parser.AahoOfficeParser;

/**
 * Created by aaho on 23/04/18.
 */

public class AahoOfficeSuggestionAdapter extends ArrayAdapter<AahoOfficeParser> {

    protected static final String TAG = "SuggestionAdapter";
    private ArrayList<AahoOfficeParser> suggestions;

    public AahoOfficeSuggestionAdapter(Activity context, String nameFilter) {
        super(context, android.R.layout.simple_dropdown_item_1line);
        suggestions = new ArrayList<>();
    }

    @Override
    public int getCount() {
        return suggestions.size();
    }

    @Override
    public AahoOfficeParser getItem(int index) {
        return suggestions.get(index);
    }

    @Override
    public Filter getFilter() {
        Filter myFilter = new Filter() {
            @Override
            protected FilterResults performFiltering(CharSequence constraint) {
                FilterResults filterResults = new FilterResults();

                try {
                    AahoOfficeParser aahoOfficeParser = new AahoOfficeParser();
                    if (constraint != null) {
                        // A class that queries a web API, parses the data and
                        // returns an ArrayList
                        ArrayList<AahoOfficeParser> new_suggestions = aahoOfficeParser
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

