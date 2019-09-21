package in.aaho.android.customer;

import android.app.ProgressDialog;
import android.content.Intent;
import android.os.Bundle;
import android.support.design.widget.NavigationView;
import android.support.v4.view.GravityCompat;
import android.support.v4.widget.DrawerLayout;
import android.support.v7.app.ActionBarDrawerToggle;
import android.support.v7.widget.CardView;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.KeyEvent;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.TextView;

import com.android.volley.DefaultRetryPolicy;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.customer.common.ApiResponseListener;
import in.aaho.android.customer.common.BaseActivity;
import in.aaho.android.customer.booking.App;
import in.aaho.android.customer.booking.BookingActivity;
import in.aaho.android.customer.profile.ProfileActivity;
import in.aaho.android.customer.requests.Api;
import in.aaho.android.customer.requests.LogoutRequest;
import in.aaho.android.customer.support.ContactUsActivity;
import in.aaho.android.customer.transaction.GenerateLrActivity;
import in.aaho.android.customer.transaction.QuotationActivity;
import in.aaho.android.customer.transaction.TransactionActivity;

public class LandingActivity extends BaseActivity
        implements NavigationView.OnNavigationItemSelectedListener {
    private CardView cvPlaceOrder;
    private CardView cvTrackOrder;
    private CardView cvBookingHistory;
    private CardView cvQuotations;
    private CardView cvPayments;
    private CardView cvSupport;
    private TextView navUserNameTextView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_landing);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        getSupportActionBar().setTitle("Dashboard");

        setViewVariables();
        setClickListeners();

        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        ActionBarDrawerToggle toggle = new ActionBarDrawerToggle(
                this, drawer, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close);
        drawer.addDrawerListener(toggle);
        toggle.syncState();

        NavigationView navigationView = (NavigationView) findViewById(R.id.nav_view);
        navigationView.setNavigationItemSelectedListener(this);

        View header = navigationView.getHeaderView(0);
        navUserNameTextView = (TextView) header.findViewById(R.id.side_nav_company_name);
        updateUserName();
    }

    private void setClickListeners() {
        cvPlaceOrder.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startActivity(new Intent(LandingActivity.this, BookingActivity.class));
            }
        });

//        cvTrackOrder.setOnClickListener(new View.OnClickListener() {
//            @Override
//            public void onClick(View v) {
//                startActivity(new Intent(LandingActivity.this, TrackingListActivity.class));
//            }
//        });
        cvBookingHistory.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startActivity(new Intent(LandingActivity.this, TransactionActivity.class));
            }
        });
        cvQuotations.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                getQuotations();

            }
        });
//        cvPayments.setOnClickListener(new View.OnClickListener() {
//            @Override
//            public void onClick(View v) {
//
//            }
//        });
        cvSupport.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
//                startActivity(new Intent(LandingActivity.this, ContactUsActivity.class));
                startActivity(new Intent(LandingActivity.this, GenerateLrActivity.class));

            }
        });
    }

    public void updateUserName() {
        if (navUserNameTextView != null && App.getUserName() != null) {
            navUserNameTextView.setText(App.getUserName());
        }
    }

    public void setViewVariables() {
        cvPlaceOrder = (CardView) findViewById(R.id.card_view_place_order);
//        cvTrackOrder = (CardView) findViewById(R.id.card_view_track_order);
        cvBookingHistory = (CardView) findViewById(R.id.card_view_booking_history);
        cvQuotations = (CardView) findViewById(R.id.card_view_quotations);
//        cvPayments = (CardView) findViewById(R.id.card_view_payments);
        cvSupport = (CardView) findViewById(R.id.card_view_support);
    }

    public void getQuotations() {
        final ProgressDialog pDialog = new ProgressDialog(this);
        pDialog.setMessage("Loading...");
        pDialog.show();
        JSONObject obj = new JSONObject();
        try {
            obj.put("username", "sme");
        } catch (JSONException e) {
            e.printStackTrace();
        }

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.POST, Api.QUOTATIONS, obj,
                new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        Log.e(Api.TAG, String.valueOf(response));
//                        intentQuotation.putExtra("quotations", "mani");
//                        Log.e(Api.TAG, String.valueOf(response));
                        Intent intentQuotation = new Intent(LandingActivity.this, QuotationActivity.class);
                        intentQuotation.putExtra("quotations", String.valueOf(response));
                        startActivity(intentQuotation);
                        pDialog.dismiss();
                    }
                },
                new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        Log.e(Api.TAG, error.toString());
                        pDialog.dismiss();
                    }
                });
        RequestQueue requestQueue = Volley.newRequestQueue(this);
        requestQueue.add(jsonObjectRequest);
        jsonObjectRequest.setRetryPolicy(new DefaultRetryPolicy(10000,
                DefaultRetryPolicy.DEFAULT_MAX_RETRIES,
                DefaultRetryPolicy.DEFAULT_BACKOFF_MULT));
    }

    @Override
    public void onBackPressed() {
        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        if (drawer.isDrawerOpen(GravityCompat.START)) {
            drawer.closeDrawer(GravityCompat.START);
        } else {
            super.onBackPressed();
        }
    }

    @Override
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
    }

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
        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
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
}
