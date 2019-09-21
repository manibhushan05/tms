package in.aaho.android.loads;

import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.support.design.widget.NavigationView;
import android.support.v4.view.GravityCompat;
import android.support.v4.widget.DrawerLayout;
import android.support.v7.app.ActionBarDrawerToggle;
import android.support.v7.widget.CardView;
import android.support.v7.widget.Toolbar;
import android.text.TextUtils;
import android.util.Log;
import android.view.KeyEvent;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;

import com.android.volley.VolleyError;

import org.json.JSONObject;

import in.aaho.android.loads.common.ApiResponseListener;
import in.aaho.android.loads.common.BaseActivity;
import in.aaho.android.loads.loads.AvailableLoadsActivity;
import in.aaho.android.loads.loads.MyLoadsActivity;
import in.aaho.android.loads.requests.LogoutRequest;
import in.aaho.android.loads.support.ContactUsActivity;

/**
 * Created by aaho on 07/05/18.
 */

public class LandingActivity extends BaseActivity
        implements NavigationView.OnNavigationItemSelectedListener {

    private static final String TAG = "LandingActivity";
    private CardView cvNewLoads;
    private CardView cvCustomerLoads;
    private CardView cvMyLoads;
    private TextView navUserNameTextView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_landing);

        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        getSupportActionBar().setTitle("Aaho Sales");

        setViewVariables();
        setClickListeners();

        DrawerLayout drawer = findViewById(R.id.drawer_layout);
        ActionBarDrawerToggle toggle = new ActionBarDrawerToggle(
                this, drawer, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close);
        drawer.addDrawerListener(toggle);
        toggle.syncState();

        NavigationView navigationView = findViewById(R.id.nav_view);
        navigationView.setNavigationItemSelectedListener(this);

        View header = navigationView.getHeaderView(0);
        navUserNameTextView = header.findViewById(R.id.side_nav_company_name);
        updateUserName();
    }

    private void setClickListeners() {

        cvNewLoads.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startActivity(new Intent(LandingActivity.this, RequirementActivity.class));
            }
        });

        cvCustomerLoads.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startActivity(new Intent(LandingActivity.this, AvailableLoadsActivity.class));
            }
        });

        cvMyLoads.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startActivity(new Intent(LandingActivity.this, MyLoadsActivity.class));
            }
        });
    }

    public void updateUserName() {
        if (navUserNameTextView != null && Aaho.getUsername() != null) {
            navUserNameTextView.setText(Aaho.getUsername());
        }
    }

    public void setViewVariables() {
        cvNewLoads = findViewById(R.id.card_view_new_loads);
        cvCustomerLoads = findViewById(R.id.card_view_available_loads);
        cvMyLoads = findViewById(R.id.card_view_my_loads);
    }

    @Override
    public boolean onNavigationItemSelected(MenuItem item) {
        // Handle navigation view item clicks here.
        int id = item.getItemId();

//        if (id == R.id.profile) {
//            startActivity(new Intent(LandingActivity.this, ProfileActivity.class));
//        } else
        if (id == R.id.nav_contact_us) {
            startActivity(new Intent(LandingActivity.this, ContactUsActivity.class));
        } else if (id == R.id.nav_logout) {
            logout();
        }
        DrawerLayout drawer = findViewById(R.id.drawer_layout);
        drawer.closeDrawer(GravityCompat.START);
        return true;
    }


    private void logout() {
        LogoutRequest logoutRequest = new LogoutRequest(new LogoutListener());
        queue(logoutRequest, false);
    }

    private class LogoutListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
//            App.clearAppData();
            startActivity(new Intent(LandingActivity.this, LoginActivity.class));
            LandingActivity.this.finish();
        }
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_BACK && event.getRepeatCount() == 0) {
            finish();
            return true;
        }

        return super.onKeyDown(keyCode, event);
    }

    @Override
    protected void onResume() {
        super.onResume();
        checkAndGetPerms();
    }

}

