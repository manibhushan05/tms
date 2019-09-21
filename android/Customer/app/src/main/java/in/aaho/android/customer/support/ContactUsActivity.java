package in.aaho.android.customer.support;

import android.os.Bundle;

import in.aaho.android.customer.common.BaseActivity;
import in.aaho.android.customer.R;

public class ContactUsActivity extends BaseActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_contact_us);
        setToolbarTitle("Support Details");
    }
}
