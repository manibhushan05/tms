package in.aaho.android.ownr.booking;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.WebView;
import android.widget.Button;

import in.aaho.android.ownr.common.BaseDialogFragment;
import in.aaho.android.ownr.R;

/**
 * Created by mani on 8/8/16.
 */

public class TermsDialogFragment extends BaseDialogFragment {

    private Button doneButton;
    private WebView termsWebView;
    private View dialogView;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        dialogView = inflater.inflate(R.layout.booking_terms_dialog, container, false);

        setViewVariables();
        setClickListeners();
        setUpWebView();

        return dialogView;
    }

    private void setUpWebView() {
        termsWebView.loadUrl("file:///android_asset/terms.html");
    }

    private void setClickListeners() {
        doneButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                TermsDialogFragment.this.dismiss();
            }
        });
    }

    private void setViewVariables() {
        doneButton = dialogView.findViewById(R.id.terms_dialog_done_btn);
        termsWebView = dialogView.findViewById(R.id.terms_dialog_webview);
    }
}