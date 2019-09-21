package in.aaho.android.loads.common;

import android.Manifest;
import android.app.ProgressDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.support.annotation.LayoutRes;
import android.support.v4.app.ActivityCompat;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.Menu;
import android.view.MenuItem;
import com.android.volley.Request;

import java.util.ArrayList;
import java.util.List;
import in.aaho.android.loads.R;

/**
 * Created by aaho on 18/04/18.
 */

public abstract class BaseActivity extends AppCompatActivity {

    private ProgressDialog progress;
    private Toolbar toolbar;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setUpProgressDialog();
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

    @Override
    public void setContentView(@LayoutRes int layoutResID) {
        super.setContentView(layoutResID);
        setupToolbar();
    }

    private void setupToolbar() {
        toolbar = (Toolbar) findViewById(R.id.toolbar);
        if (toolbar != null) {
            toolbar.setTitle(this.getLocalClassName());
            setSupportActionBar(toolbar);
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
            getSupportActionBar().setDisplayShowHomeEnabled(true);
        }
    }

    protected void setToolbarTitle(String title) {
        if (toolbar != null) {
            title = Utils.not(title) ? "Unnamed" : title.trim();
            toolbar.setTitle(title);
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
        //Utils.toast(msg);
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        int itemId = item.getItemId();
        switch (itemId) {
            case android.R.id.home:
                onBackPressed();
                break;
        }

        return super.onOptionsItemSelected(item);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String permissions[], int[] grantResults) {
        switch (requestCode) {
            case MY_PERMISSIONS_REQUEST: {
                String[] missPerms = missingPerms();
                if (missPerms.length > 0) {
                    showPermissionAlertDialog();
                } else {
                    checkingPrems = false;
                }
                return;
            }
        }
    }

    public static final int MY_PERMISSIONS_REQUEST = 8;
    public boolean checkingPrems = false;

    public static final String[] requiredPerms = new String[] {
            Manifest.permission.READ_EXTERNAL_STORAGE,
            Manifest.permission.WRITE_EXTERNAL_STORAGE,
            Manifest.permission.CAMERA
    };

    public int checkPerm(String perm) {
        return ActivityCompat.checkSelfPermission(this, perm);
    }

    public String[] missingPerms() {
        List<String> mis = new ArrayList<>();
        for (String perm : requiredPerms) {
            if (checkPerm(perm) != PackageManager.PERMISSION_GRANTED) {
                mis.add(perm);
            }
        }
        return mis.toArray(new String[mis.size()]);
    }

    public boolean checkAndGetPerms() {
        if (checkingPrems) {
            return false;
        }
        checkingPrems = true;
        String[] missPerms = missingPerms();
        if (missPerms.length > 0) {
            ActivityCompat.requestPermissions(this, missPerms, MY_PERMISSIONS_REQUEST);
            return false;
        }
        return true;
    }

    public void showPermissionAlertDialog() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);

        builder.setTitle("Permission Required");
        builder.setMessage("App requires these permissions to function");
        builder.setPositiveButton("Ok", new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int id) {
                checkingPrems = false;
                checkAndGetPerms();
            }
        });
        builder.setNegativeButton("Quit", new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int id) {
                finish();
                System.exit(0);
            }
        });
        builder.show();
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

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        return super.onCreateOptionsMenu(menu);
    }
}