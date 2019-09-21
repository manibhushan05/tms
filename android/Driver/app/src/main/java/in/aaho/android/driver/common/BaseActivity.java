package in.aaho.android.driver.common;

import android.app.ProgressDialog;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;

import com.android.volley.Request;

import in.aaho.android.driver.R;


/*
changes

- makeToast
- shared prefs
- toolbar
- show progress
- base activity
- base dialog fragment
- change api request, and listeners
- requestQueue

- mod base activity to include specific perms
- mod MainApplication to specific needs

 */

public abstract class BaseActivity extends AppCompatActivity {

    private ProgressDialog progress;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setUpProgressDialog();
    }

    @Override
    protected void attachBaseContext(Context base) {
        super.attachBaseContext(Lang.onAttach(base));
    }


    public void queue(Request<?> request) {
        queue(request, true);
    }

    public void queue(Request<?> request, boolean progress) {
        MainApplication.queueRequest(request);
        if (progress) {
            showProgress();
        }
    }

    private void setUpProgressDialog() {
        progress = new ProgressDialog(this);
        progress.setTitle(R.string.progress_title);
        progress.setMessage(getString(R.string.progress_msg));
    }

    private ProgressDialog getProgress() {
        if (progress == null) {
            setUpProgressDialog();
        }
        return progress;
    }

    public void showProgress() {
        getProgress().show();
    }

    public void dismissProgress() {
        getProgress().dismiss();
    }

    protected static void toast(String msg) {
        Utils.toast(msg);
    }

    public void launchDialer(String phone) {
        if (Utils.not(phone)) {
            toast("phone number is blank");
            return;
        }
        Intent intent = new Intent(Intent.ACTION_DIAL);
        intent.setData(Uri.parse("tel:" + phone.trim()));
        startActivity(intent);
    }
}