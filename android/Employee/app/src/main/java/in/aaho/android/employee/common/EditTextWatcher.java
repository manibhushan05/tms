package in.aaho.android.employee.common;

import android.text.Editable;
import android.text.TextWatcher;

/**
 * Created by aaho on 18/04/18.
 */
public abstract class EditTextWatcher implements TextWatcher {

    @Override
    public void beforeTextChanged(CharSequence s, int start, int count, int after) {
    }

    @Override
    public void afterTextChanged(Editable s) {
    }
}
