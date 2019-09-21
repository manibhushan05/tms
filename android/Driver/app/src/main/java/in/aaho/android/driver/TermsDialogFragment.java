package in.aaho.android.driver;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.WebView;
import android.widget.Button;

import in.aaho.android.driver.common.BaseDialogFragment;


/**
 * Created by shobhit on 8/8/16.
 */

public class TermsDialogFragment extends BaseDialogFragment {

    private Button doneButton;
    private WebView termsWebView;
    private View dialogView;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        dialogView = inflater.inflate(R.layout.terms_dialog, container, false);

        setViewVariables();
        setClickListeners();
        setUpWebView();

        return dialogView;
    }

    private void setUpWebView() {
        termsWebView.loadUrl(getString(R.string.terms_html_file));
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
        doneButton = (Button) dialogView.findViewById(R.id.terms_dialog_done_btn);
        termsWebView = (WebView) dialogView.findViewById(R.id.terms_dialog_webview);
    }
}