package in.aaho.android.driver.common;

import android.app.Dialog;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.v7.app.AppCompatDialogFragment;
import android.util.Log;
import android.view.Window;
import android.view.WindowManager;

import com.android.volley.Request;

/**
 * Created by shobhit on 8/8/16.
 */

public class BaseDialogFragment extends AppCompatDialogFragment {

    private BaseActivity activity;

    public void setActivity(BaseActivity activity) {
        this.activity = activity;
    }

    protected BaseActivity getBaseActivity() {
        return activity;
    }

    protected void queue(Request<?> request) {
        queue(request, true);
    }

    protected void queue(Request<?> request, boolean progress) {
        MainApplication.queueRequest(request);
        if (progress) {
            showProgress();
        }
    }

    protected void showProgress() {
        if (activity != null) {
            activity.showProgress();
        } else {
            Log.e("[ERROR!!]", "Could not show progress, activity=null");
        }
    }

    protected void dismissProgress() {
        if (activity != null) {
            activity.dismissProgress();
        } else {
            Log.e("[ERROR!!]", "Could not dismiss progress, activity=null");
        }
    }

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @NonNull
    @Override
    public Dialog onCreateDialog(Bundle savedInstanceState) {
        Dialog dialog = super.onCreateDialog(savedInstanceState);
        dialog.getWindow().requestFeature(Window.FEATURE_NO_TITLE);
        dialog.getWindow().setBackgroundDrawableResource(android.R.color.transparent);
        return dialog;
    }

    @Override
    public void onResume(){
        super.onResume();
        Window window = getDialog().getWindow();
        window.setLayout(WindowManager.LayoutParams.MATCH_PARENT, WindowManager.LayoutParams.WRAP_CONTENT);
    }

    protected static void toast(String msg) {
        Utils.toast(msg);
    }
}