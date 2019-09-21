package android.aaho.in.sme.Activity;

import android.aaho.in.sme.R;
import android.app.DatePickerDialog;
import android.app.Dialog;
import android.app.DialogFragment;
import android.app.TimePickerDialog;
import android.content.Intent;
import android.os.Bundle;
import android.support.design.widget.NavigationView;
import android.support.v4.view.GravityCompat;
import android.support.v4.widget.DrawerLayout;
import android.support.v7.app.ActionBarDrawerToggle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.text.format.DateFormat;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.DatePicker;
import android.widget.EditText;
import android.widget.TimePicker;

import com.weiwangcn.betterspinner.library.material.MaterialBetterSpinner;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.Calendar;

public class MainActivity extends AppCompatActivity
        implements NavigationView.OnNavigationItemSelectedListener {

    MaterialBetterSpinner vehicleCategory;
    EditText etSourceAddress;
    EditText etSourceCity;
    EditText etDestinationAddress;
    EditText etDestinationCity;
    EditText etNumberOfTruck;
    EditText etMaterial;
    EditText etWeightOfMaterial;
    static EditText etDate;
    static EditText etTime;
    Button submit;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        toolbar.setTitle("AAHO");
        setSupportActionBar(toolbar);
        getID();
        final Calendar c = Calendar.getInstance();
        int year = c.get(Calendar.YEAR);
        int month = c.get(Calendar.MONTH);
        month = month + 1;
        int day = c.get(Calendar.DAY_OF_MONTH);
        String dateOfDataCollection = year + "-" + month + "-" + day;
        etDate.setText(dateOfDataCollection);
//        int hour = c.get(Calendar.HOUR_OF_DAY);
//        int minute = c.get(Calendar.MINUTE);
//        etTime.setText(hour + ":" + minute);

        etDate.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showDatePickerDialog(v);
            }
        });
        etTime.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showTimePickerDialog(v);
            }
        });

//        startActivity(new Intent(MainActivity.this, PlaceOrderActivity.class));
        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        ActionBarDrawerToggle toggle = new ActionBarDrawerToggle(
                this, drawer, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close);
        drawer.setDrawerListener(toggle);
        toggle.syncState();

        NavigationView navigationView = (NavigationView) findViewById(R.id.nav_view);
        navigationView.setNavigationItemSelectedListener(this);
    }
    public void showDatePickerDialog(View v) {
        DialogFragment newFragment = new DatePickerFragment();
        newFragment.show(getFragmentManager(), "datePicker");
    }

    public void showTimePickerDialog(View v) {
        DialogFragment newFragment = new TimePickerFragment();
        newFragment.show(getFragmentManager(), "timePicker");
    }

    public static class DatePickerFragment extends DialogFragment
            implements DatePickerDialog.OnDateSetListener {

        @Override
        public Dialog onCreateDialog(Bundle savedInstanceState) {
            // Use the current date as the default date in the picker
            final Calendar c = Calendar.getInstance();
            int year = c.get(Calendar.YEAR);
            int month = c.get(Calendar.MONTH);
            int day = c.get(Calendar.DAY_OF_MONTH);

            // Create a new instance of DatePickerDialog and return it
            return new DatePickerDialog(getActivity(), this, year, month, day);
        }

        public void onDateSet(DatePicker view, int year, int month, int day) {
            // Do something with the date chosen by the user
            month = month + 1;
            String dateOfDataCollection = year + "-" + month + "-" + day;
            etDate.setText(dateOfDataCollection);
        }
    }

    public static class TimePickerFragment extends DialogFragment
            implements TimePickerDialog.OnTimeSetListener {

        @Override
        public Dialog onCreateDialog(Bundle savedInstanceState) {
            // Use the current time as the default values for the picker
            final Calendar c = Calendar.getInstance();
            int hour = c.get(Calendar.HOUR_OF_DAY);
            int minute = c.get(Calendar.MINUTE);

            // Create a new instance of TimePickerDialog and return it
            return new TimePickerDialog(getActivity(), this, hour, minute,
                    DateFormat.is24HourFormat(getActivity()));
        }

        public void onTimeSet(TimePicker view, int hourOfDay, int minute) {
            // Do something with the time chosen by the user
            etTime.setText(hourOfDay + ":" + minute);
        }
    }
    private void getID() {

        String[] vehicleCategoryList = getResources().getStringArray(R.array.vehicle_category);

        ArrayAdapter<String> vehicleCategoryAdapter = new ArrayAdapter<>(this,
                android.R.layout.simple_dropdown_item_1line, vehicleCategoryList);
        vehicleCategory = (MaterialBetterSpinner) findViewById(R.id.vehicle_category);
        try {
            vehicleCategory.setAdapter(vehicleCategoryAdapter);
        } catch (NullPointerException npe) {
            npe.printStackTrace();
        }

        etSourceAddress = (EditText) findViewById(R.id.input_source_address);
        etSourceCity = (EditText) findViewById(R.id.input_source_city);
        etDestinationAddress = (EditText) findViewById(R.id.input_destination_address);
        etDestinationCity = (EditText) findViewById(R.id.input_destination_city);
        etNumberOfTruck = (EditText) findViewById(R.id.input_number_of_truck);
        etMaterial = (EditText) findViewById(R.id.input_material);
        etWeightOfMaterial = (EditText) findViewById(R.id.input_weight_of_material);
        etDate = (EditText) findViewById(R.id.input_date_of_shipment);
        etTime = (EditText) findViewById(R.id.input_time_of_shipment);
        submit = (Button) findViewById(R.id.submit);
    }

    private String getData() {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put("source", etSourceAddress.getText().toString());
            jsonObject.put("sourceCity", etSourceCity.getText().toString());
            jsonObject.put("destination", etDestinationAddress.getText().toString());
            jsonObject.put("destinationCity", etDestinationCity.getText().toString());
            jsonObject.put("numberOfTruck", etNumberOfTruck.getText().toString());
            jsonObject.put("material", etMaterial.getText().toString());
            jsonObject.put("weightOfMaterial", etWeightOfMaterial.getText().toString());
            jsonObject.put("date", etDate.getText().toString());
            jsonObject.put("time", etTime.getText().toString());
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return jsonObject.toString();
    }
    private void setBlank(){
        etSourceAddress.getText().clear();
        etSourceCity.getText().clear();
        etDestinationAddress.getText().clear();
        etDestinationCity.getText().clear();
        etNumberOfTruck.getText().clear();
        etMaterial.getText().clear();
        etWeightOfMaterial.getText().clear();
        etDate.getText().clear();
        etTime.getText().clear();
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
        getMenuInflater().inflate(R.menu.main, menu);
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
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    @SuppressWarnings("StatementWithEmptyBody")
    @Override
    public boolean onNavigationItemSelected(MenuItem item) {
        // Handle navigation view item clicks here.
        int id = item.getItemId();

        if (id == R.id.nav_place_order) {
            startActivity(new Intent(MainActivity.this, PlaceOrderActivity.class));
        } else if (id == R.id.nav_track_order) {
            startActivity(new Intent(MainActivity.this, TrackOrder.class));

        } else if (id == R.id.nav_transaction) {
            startActivity(new Intent(MainActivity.this, Transaction.class));

        } else if (id == R.id.nav_contact_us) {
            startActivity(new Intent(MainActivity.this,ContactUs.class));

        }
        else if(id == R.id.logout){
            if (getIntent().getExtras() != null && getIntent().getExtras().getBoolean("EXIT", false)) {
                finish();
            }
        }
        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        drawer.closeDrawer(GravityCompat.START);
        return true;
    }
}
