package in.aaho.android.customer.booking;

import android.text.Editable;
import android.text.TextWatcher;

import in.aaho.android.customer.common.ListItemListerner;

/**
 * Created by shobhit on 6/8/16.
 */
public abstract class ListEditTextWatcher extends ListItemListerner implements TextWatcher {

    @Override
    public void beforeTextChanged(CharSequence s, int start, int count, int after) {
    }

    @Override
    public void afterTextChanged(Editable s) {
    }
}
