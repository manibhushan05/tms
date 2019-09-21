package in.aaho.android.loads;

import android.Manifest;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.support.v4.app.ActivityCompat;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.FragmentTransaction;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;

/**
 * Created by aaho on 18/04/18.
 */

public class ForgotPasswordActivity extends AppCompatActivity implements
        ForgotPasswordFragment.OnForgotPasswordSubmitListener,
        ResetPasswordFragment.OnResetPasswordSubmitListener,
        OTPFragment.OnOTPSubmitListener {

    String TAG = getClass().getSimpleName();
    FragmentManager mFragmentManager;
    FragmentTransaction mFragmentTransaction;
    final int MI_FORGOT_PASSWORD_FRAG = 1;
    final int MI_OTP_FRAG = 2;
    final int MI_RESET_PASSWORD_FRAG = 3;
    final int MY_PERMISSIONS_REQUEST_READ_SMS = 101;
    private String phoneNo = "";
    private String username = "";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_forgot_password);
        mFragmentManager = getSupportFragmentManager();

        if(Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            // show dynamic permission for marshmallow and above devices
            requestPermissionIfNeeded();
        }

        // At first we load the forgot password fragment
        loadFragment(MI_FORGOT_PASSWORD_FRAG,null);
    }

    @Override
    public void onBackPressed() {
        processBackStack();
    }

    void processBackStack() {
        int count = mFragmentManager.getBackStackEntryCount();
        if(count == 2) {
            mFragmentManager.popBackStack();
        } else {
            super.onBackPressed();
        }
    }

    private void loadFragment(int id,Bundle bundle) {
        switch (id) {
            case MI_FORGOT_PASSWORD_FRAG:
                addFragment(ForgotPasswordFragment.newInstance(),
                        "frag_forgot_password", false);
                break;
            case MI_OTP_FRAG:
                if (bundle != null) {
                    phoneNo = bundle.getString(OTPFragment.PHONE_NO_KEY);
                    username = bundle.getString(OTPFragment.USERNAME_KEY);
                }
                addFragment(OTPFragment.newInstance(phoneNo,username),
                        "frag_otp", false);
                break;
            case MI_RESET_PASSWORD_FRAG:
                if (bundle != null) {
                    username = bundle.getString(OTPFragment.USERNAME_KEY);
                }
                addFragment(ResetPasswordFragment.newInstance(username),
                        "frag_reset_password", false);
                break;
            default:
                break;
        }
    }

    void addFragment(Fragment fragment, String tag, boolean isAddToBackStack) {
        mFragmentTransaction = mFragmentManager.beginTransaction();
        mFragmentTransaction.add(R.id.container,fragment,tag);
        if(isAddToBackStack)
            mFragmentTransaction.addToBackStack(tag);
        mFragmentTransaction.commit();
    }

    private void requestPermissionIfNeeded() {
        if((ContextCompat.checkSelfPermission(this,
                android.Manifest.permission.READ_SMS)
                != PackageManager.PERMISSION_GRANTED) ||
                (ContextCompat.checkSelfPermission(this,
                        Manifest.permission.RECEIVE_SMS)
                        != PackageManager.PERMISSION_GRANTED) ){

            // No explanation needed, we can request the permission.
            ActivityCompat.requestPermissions(this,
                    new String[]{android.Manifest.permission.READ_SMS,
                            Manifest.permission.RECEIVE_SMS},
                    MY_PERMISSIONS_REQUEST_READ_SMS);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode,
                                           String permissions[], int[] grantResults) {
        switch (requestCode) {
            case MY_PERMISSIONS_REQUEST_READ_SMS: {
                // If request is cancelled, the result arrays are empty.
                if (grantResults.length > 0
                        && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    // permission was granted, yay! Do the
                    // contacts-related task you need to do.
                } else {
                    // permission denied, boo! Disable the
                    // functionality that depends on this permission.
                }
                return;
            }
        }
    }


    @Override
    public void onForgotPasswordSubmit(String phoneNo, String username) {
        Bundle bundle = new Bundle();
        bundle.putString(OTPFragment.PHONE_NO_KEY,phoneNo);
        bundle.putString(OTPFragment.USERNAME_KEY,username);
        loadFragment(MI_OTP_FRAG,bundle);
    }

    @Override
    public void onOTPSubmit(String username) {
        Bundle bundle = new Bundle();
        bundle.putString(OTPFragment.USERNAME_KEY,username);
        loadFragment(MI_RESET_PASSWORD_FRAG,bundle);
    }

    @Override
    public void onResetPasswordSubmit() {
        // Nothing to do, go to login screen
        processBackStack();
    }
}

