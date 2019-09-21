package in.aaho.android.employee.support;

import android.content.Context;
import android.os.Bundle;
import android.view.View;
import android.widget.ImageView;

import in.aaho.android.employee.R;
import in.aaho.android.employee.common.BaseActivity;
import in.aaho.android.employee.common.Utils;

public class ContactUsActivity extends BaseActivity {

    private ImageView imgContactUs,imgEmailUs;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_contact_us);
        setToolbarTitle("Support Details");

        findViews();
        setClickListeners();
    }

    private void setClickListeners() {
        imgContactUs.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                String contactNo = getResources().getString(R.string.support_phone);
                Utils.launchDialer(ContactUsActivity.this,contactNo);
            }
        });

        imgEmailUs.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                String emailId = getResources().getString(R.string.support_email);
                Utils.sendEmail(ContactUsActivity.this,emailId);
            }
        });
    }

    private void findViews() {
        imgContactUs = findViewById(R.id.imgContactUs);
        imgEmailUs = findViewById(R.id.imgEmailUs);
    }
}
