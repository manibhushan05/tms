package in.aaho.android.ownr;

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
import android.widget.Toast;

import com.android.volley.VolleyError;

import org.json.JSONObject;

import java.io.UnsupportedEncodingException;

import in.aaho.android.ownr.booking.App;
import in.aaho.android.ownr.common.ApiResponseListener;
import in.aaho.android.ownr.common.BaseActivity;
import in.aaho.android.ownr.common.Utils;
import in.aaho.android.ownr.drivers.ListDriversActivity;
import in.aaho.android.ownr.loads.AvailableLoadsActivity;
import in.aaho.android.ownr.map.MapActivity;
import in.aaho.android.ownr.profile.ProfileActivity;
import in.aaho.android.ownr.requests.GetNotificationCountRequest;
import in.aaho.android.ownr.requests.LogoutRequest;
import in.aaho.android.ownr.support.ContactUsActivity;
import in.aaho.android.ownr.transaction.TransactionActivity;
import in.aaho.android.ownr.transaction.TransactionNewActivity;
import in.aaho.android.ownr.vehicles.VehicleListActivity;

public class LandingActivity extends BaseActivity
        implements NavigationView.OnNavigationItemSelectedListener {
    private final String TAG = getClass().getSimpleName();
    private CardView cvMyVehicles;
    private CardView cvTrack;
    private CardView cvMyDrivers;
    private CardView cvLoads;
    private CardView cvTripHistory;
    private CardView cvSupport;
    private TextView navUserNameTextView,tvNotificationCount;
    private ImageView imgNotification;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_landing);

        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        getSupportActionBar().setTitle("Aaho Fleet Manager");

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

        new Handler().postDelayed(new Runnable() {
            @Override
            public void run() {
                //todo: uncomment once notification api is ready getNotificationCountFromServer();
            }
        },100);
    }

    private void setClickListeners() {
        cvMyVehicles.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startActivity(new Intent(LandingActivity.this, VehicleListActivity.class));
            }
        });
        cvMyDrivers.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startActivity(new Intent(LandingActivity.this, ListDriversActivity.class));
            }
        });
        cvTripHistory.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(LandingActivity.this, TransactionNewActivity.class);
                startActivity(intent);
            }
        });
        cvSupport.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startActivity(new Intent(LandingActivity.this, ContactUsActivity.class));
            }
        });
        cvTrack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startActivity(new Intent(LandingActivity.this, MapActivity.class));
            }
        });
        cvLoads.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startActivity(new Intent(LandingActivity.this, AvailableLoadsActivity.class));
            }
        });

        imgNotification.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                // call the notification api to get all the notification list
                setNotificationCount(0); // once clicked hide the count
                getNotificationList();
            }
        });
    }

    public void updateUserName() {
        if (navUserNameTextView != null && App.getUserName() != null) {
            navUserNameTextView.setText(App.getUserName());
        }
    }

    public void setViewVariables() {
        cvMyVehicles = findViewById(R.id.card_view_my_vehicles);
        cvMyDrivers = findViewById(R.id.card_view_my_drivers);
        cvTripHistory = findViewById(R.id.card_view_trip_history);
        cvSupport = findViewById(R.id.card_view_support);
        cvTrack = findViewById(R.id.card_view_track);
        cvLoads = findViewById(R.id.card_view_available_loads);
        tvNotificationCount = findViewById(R.id.tvNotificationCount);
        imgNotification = findViewById(R.id.imgNotification);
    }

    @Override
    public void onBackPressed() {
        DrawerLayout drawer = findViewById(R.id.drawer_layout);
        if (drawer.isDrawerOpen(GravityCompat.START)) {
            drawer.closeDrawer(GravityCompat.START);
        } else {
            super.onBackPressed();
        }
    }

    // commented because we already showing profile menu from drawer */
    /*@Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.landing, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            startActivity(new Intent(LandingActivity.this, ProfileActivity.class));
        }

        return super.onOptionsItemSelected(item);
    }*/

    @Override
    public boolean onNavigationItemSelected(MenuItem item) {
        // Handle navigation view item clicks here.
        int id = item.getItemId();

        if (id == R.id.profile) {
            startActivity(new Intent(LandingActivity.this, ProfileActivity.class));
        } else if (id == R.id.nav_contact_us) {
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
            App.clearAppData();
            Aaho.setToken(null);
            startActivity(new Intent(LandingActivity.this, LoginActivity.class));
            LandingActivity.this.finish();
        }

        @Override
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);

            int statusCode = Utils.getStatusCodeFromVolleyError(error);

            App.clearAppData();
            Aaho.setToken(null);
            startActivity(new Intent(LandingActivity.this,
                    LoadingActivity.class));
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


    private void setNotificationCount(int notificationCount) {
        if(notificationCount == 0) {
            tvNotificationCount.setVisibility(View.INVISIBLE);
        } else {
            tvNotificationCount.setVisibility(View.VISIBLE);
            tvNotificationCount.setText(""+notificationCount);
        }
    }

    // call api to get notification count
    private void getNotificationCountFromServer() {
        GetNotificationCountRequest request = new GetNotificationCountRequest(new ApiResponseListener() {
            @Override
            public void onResponse(JSONObject response) {
                String count = response.optString("notification_count");
                if(TextUtils.isEmpty(count)) {
                    setNotificationCount(0);
                } else {
                    setNotificationCount(Integer.valueOf(count));
                }
            }

            @Override
            public void onErrorResponse(VolleyError error) {
                super.onErrorResponse(error);
                dismissProgress();
            }
        });

        queue(request);
    }

    private void getNotificationList() {
        startActivity(new Intent(this,NotificationActivity.class));
    }



}
