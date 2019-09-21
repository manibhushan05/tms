package in.aaho.android.ownr.common;

import android.text.Editable;
import android.text.TextWatcher;

/**
 * Created by mani on 6/8/16.
 */
public abstract class EditTextWatcher implements TextWatcher {

    @Override
    public void beforeTextChanged(CharSequence s, int start, int count, int after) {
    }

    @Override
    public void afterTextChanged(Editable s) {
    }
}
