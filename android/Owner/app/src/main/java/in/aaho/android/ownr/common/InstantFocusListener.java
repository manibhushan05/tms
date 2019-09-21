package in.aaho.android.ownr.common;

import android.view.View;
import android.widget.Toast;

/**
 * Created by mani on 13/9/16.
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
