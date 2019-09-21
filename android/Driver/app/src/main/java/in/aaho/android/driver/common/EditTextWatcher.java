package in.aaho.android.driver.common;

import android.text.Editable;
import android.text.TextWatcher;

/**
 * Created by shobhit on 6/8/16.
 */
public abstract class EditTextWatcher implements TextWatcher {

    @Override
    public void beforeTextChanged(CharSequence s, int start, int count, int after) {
    }

    @Override
    public void afterTextChanged(Editable s) {
    }
}
