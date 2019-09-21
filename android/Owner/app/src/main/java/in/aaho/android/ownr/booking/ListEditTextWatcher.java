package in.aaho.android.ownr.booking;

import android.text.Editable;
import android.text.TextWatcher;

import in.aaho.android.ownr.common.ListItemListerner;

/**
 * Created by mani on 6/8/16.
 */
public abstract class ListEditTextWatcher extends ListItemListerner implements TextWatcher {

    @Override
    public void beforeTextChanged(CharSequence s, int start, int count, int after) {
    }

    @Override
    public void afterTextChanged(Editable s) {
    }
}
