package in.aaho.android.aahocustomers.support;

import android.os.Bundle;

import in.aaho.android.aahocustomers.R;
import in.aaho.android.aahocustomers.common.BaseActivity;

public class ContactUsActivity extends BaseActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_contact_us);
        setToolbarTitle("Support Details");
    }
}
