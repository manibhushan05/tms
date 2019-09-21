package in.aaho.android.driver.common;

import android.view.View;

/**
 * Created by shobhit on 13/9/16.
 */
public class InstantFocusListener implements View.OnFocusChangeListener {

    private InstantAutoComplete view;

    public InstantFocusListener(InstantAutoComplete view) {
        this.view = view;
    }

    @Override
    public void onFocusChange(View v, boolean hasFocus) {
        if (hasFocus) {
            view.showDropDown();
        }
    }
}
