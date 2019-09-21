package in.aaho.smebooking;

import android.app.DatePickerDialog;
import android.app.Dialog;
import android.app.DialogFragment;
import android.app.ProgressDialog;
import android.app.TimePickerDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.RecoverySystem;
import android.preference.PreferenceManager;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.format.DateFormat;
import android.util.Log;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.AutoCompleteTextView;
import android.widget.Button;
import android.widget.DatePicker;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TimePicker;
import android.widget.Toast;

import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.StringRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.Calendar;

public class MainActivity extends AppCompatActivity {
    Spinner spinnerLoadingPoint;
    Spinner spinnerUnLoadingPoint;
    Spinner spinnerVehicleCategory;
    Spinner spinnerNumberOfVehicle;
    AutoCompleteTextView tvPickUpCity;
    AutoCompleteTextView tvDropCity;
    AutoCompleteTextView etPickUpLocation;
    AutoCompleteTextView etDropLocation;
    static EditText etShipmentDate;
    static EditText etShipmentTime;
    EditText etMaterial;
    EditText etContactNumber;
    Button btPlaceOrder;
    ArrayAdapter<CharSequence> numberOfLoadingPointAdapter;
    ArrayAdapter<CharSequence> numberOfUnLoadingPointAdapter;
    ArrayAdapter<CharSequence> vehicleCategoryAdapter;
    ArrayAdapter<CharSequence> numberOfVehicleAdapter;
    ArrayAdapter<String> pickUpCityAdapter;
    ArrayAdapter<String> dropCityAdapter;
    AlertDialog.Builder adbSubmitBookingData;
    AlertDialog.Builder adbConfirmation;
    ProgressDialog pdSubmit;
    private static String date;
    private static String time="00:00";

    public static String username = "";
    String JSON_URL="http://54.169.82.235:8000/sme-booking-data/";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        getID();
        username = PreferenceManager.getDefaultSharedPreferences(getBaseContext()).getString("username", "");
        if (username.isEmpty()) {
            startActivity(new Intent(MainActivity.this, LoginActivity.class));
        }
        final Calendar c = Calendar.getInstance();
        int year = c.get(Calendar.YEAR);
        int month = c.get(Calendar.MONTH);
        month = month + 1;
        int day = c.get(Calendar.DAY_OF_MONTH);
        String strDay;
        String strMonth;

        if (day <10)
            strDay ="0"+ day;
        else strDay = day+"";
        if (month < 10)
            strMonth = "0"+month;
        else strMonth = month+"";
        date = year + "-" + strMonth + "-" + strDay;
        etShipmentDate.setText(date);
        etShipmentDate.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showDatePickerDialog(v);
            }
        });

        etShipmentTime.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showTimePickerDialog(v);
            }
        });
        sendRequest();
        btPlaceOrder.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                SendData();
            }
        });

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
            date = year + "-" + month + "-" + day;
            String strMonth;
            String strDay;
            if (month < 10)
                strMonth = "0" + month;
            else strMonth = month + "";
            if (day < 10)
                strDay = "0" + day;
            else strDay = day + "";

            String dateOfDataCollection = strDay + "-" + strMonth + "-" + year;
            etShipmentDate.setText(dateOfDataCollection);
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
            time = hourOfDay+":"+minute;
            String strMinute;
            if (minute < 10)
                strMinute = "0" + minute;
            else
                strMinute = minute + "";
            if (hourOfDay < 12)
                etShipmentTime.setText(hourOfDay + ":" + strMinute + " AM");
            else
                etShipmentTime.setText((hourOfDay - 12) + ":" + strMinute + " PM");

        }
    }


    private void getID() {
        spinnerLoadingPoint = (Spinner) findViewById(R.id.select_number_of_loading_point);
        numberOfLoadingPointAdapter = ArrayAdapter.createFromResource(this,
                R.array.number_of_loading_point, android.R.layout.simple_spinner_item);
        numberOfLoadingPointAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerLoadingPoint.setAdapter(numberOfLoadingPointAdapter);
        spinnerUnLoadingPoint = (Spinner) findViewById(R.id.select_number_of_unloading_point);
        numberOfUnLoadingPointAdapter = ArrayAdapter.createFromResource(this,
                R.array.number_of_unloading_point, android.R.layout.simple_spinner_item);
        numberOfUnLoadingPointAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerUnLoadingPoint.setAdapter(numberOfUnLoadingPointAdapter);

        spinnerVehicleCategory = (Spinner) findViewById(R.id.select_vehicle_category);
        vehicleCategoryAdapter = ArrayAdapter.createFromResource(this,
                R.array.vehicle_category, android.R.layout.simple_spinner_item);
        vehicleCategoryAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerVehicleCategory.setAdapter(vehicleCategoryAdapter);

        spinnerNumberOfVehicle = (Spinner) findViewById(R.id.select_number_of_vehicle);
        numberOfVehicleAdapter = ArrayAdapter.createFromResource(this,
                R.array.number_of_vehicle, android.R.layout.simple_spinner_item);
        numberOfVehicleAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerNumberOfVehicle.setAdapter(numberOfVehicleAdapter);
        pickUpCityAdapter = new ArrayAdapter<String>(this,
                android.R.layout.simple_dropdown_item_1line, getResources().getStringArray(R.array.india_top_city));
        tvPickUpCity = (AutoCompleteTextView)
                findViewById(R.id.input_pick_city);
        tvPickUpCity.setAdapter(pickUpCityAdapter);
        dropCityAdapter = new ArrayAdapter<String>(this,
                android.R.layout.simple_dropdown_item_1line, getResources().getStringArray(R.array.india_top_city));
        tvDropCity = (AutoCompleteTextView)
                findViewById(R.id.input_drop_city);
        tvDropCity.setAdapter(dropCityAdapter);
        etPickUpLocation = (AutoCompleteTextView) findViewById(R.id.input_pick_up_location);
        etDropLocation = (AutoCompleteTextView) findViewById(R.id.input_drop_location);
        etShipmentDate = (EditText) findViewById(R.id.input_shipment_date);
        etShipmentTime = (EditText) findViewById(R.id.input_shipment_time);
        etMaterial = (EditText) findViewById(R.id.input_material);
        etContactNumber = (EditText) findViewById(R.id.input_contact_details);
        btPlaceOrder = (Button) findViewById(R.id.btn_place_order);

    }

    private String getBookingData() {
        String numberOfLoadingPoints = spinnerLoadingPoint.getSelectedItem().toString();
        String numberOfUnLoadingPoints = spinnerUnLoadingPoint.getSelectedItem().toString();
        String numberOfVehicle= spinnerNumberOfVehicle.getSelectedItem().toString();
        String vehicleType = spinnerVehicleCategory.getSelectedItem().toString();
        if (numberOfLoadingPoints == "number_of_loading_point"){
            numberOfLoadingPoints = "1";
        }
        if (numberOfUnLoadingPoints =="number_of_unloading_point"){
            numberOfUnLoadingPoints = "1";
        }
        if (numberOfVehicle == "number_of_vehicle"){
            numberOfVehicle = "1".toString();
        }
        if (vehicleType == "vehicle_category"){
            vehicleType = "Not Selected";

        }
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put("username", username);
            jsonObject.put("numberOfLoadingPoint", numberOfLoadingPoints);
            jsonObject.put("numberOfUnloadingPoint", numberOfUnLoadingPoints);
            jsonObject.put("pickUpLocation", etPickUpLocation.getText().toString());
            jsonObject.put("pickUpCity", tvPickUpCity.getText().toString());
            jsonObject.put("dropLocation", etDropLocation.getText().toString());
            jsonObject.put("dropCity", tvDropCity.getText().toString());
            jsonObject.put("vehicleType", vehicleType);
            jsonObject.put("numberOfVehicle", numberOfVehicle);
            jsonObject.put("shipmentDate", date);
            jsonObject.put("shipmentTime", time);
            jsonObject.put("material", etMaterial.getText().toString());
            jsonObject.put("contactNumber", etContactNumber.getText().toString());
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return jsonObject.toString();
    }

    private void setBlank() {
        getID();
        spinnerLoadingPoint.setSelection(1);
        spinnerUnLoadingPoint.setSelection(1);
        spinnerVehicleCategory.setSelection(0);
        spinnerNumberOfVehicle.setSelection(1);
        etPickUpLocation.getText().clear();
        tvPickUpCity.getText().clear();
        etDropLocation.getText().clear();
        tvDropCity.getText().clear();
        etShipmentDate.getText().clear();
        etShipmentTime.getText().clear();
        etMaterial.getText().clear();
        etContactNumber.getText().clear();
    }

    private void sendRequest(){

        StringRequest stringRequest = new StringRequest(JSON_URL,
                new Response.Listener<String>() {
                    @Override
                    public void onResponse(String response) {
                        getID();
                        try {
                            JSONArray jsonArray = new JSONArray(response);
                            etContactNumber.setText(String.valueOf(jsonArray.get(8)));
                            etMaterial.setText(String.valueOf(jsonArray.get(7)));
                            etShipmentTime.setText(String.valueOf(jsonArray.get(6)));
                            String loading = String.valueOf(jsonArray.get(3));
                            loading = loading.substring(1,loading.length()-1);
                            Log.e("jsonObject", String.valueOf(jsonArray.get(3)));
//                            String strArray[] = new String[]{loading};
                            String strArray[] = loading.split("//");
                            Log.e("StrArray",strArray[0]);
                        } catch (JSONException e) {
                            Log.e("Error", e.toString());
                        }
                        //Log.e("jsonResponse",response);
                    }
                },
                new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        Toast.makeText(MainActivity.this,error.getMessage(),Toast.LENGTH_LONG).show();
                    }
                });

        RequestQueue requestQueue = Volley.newRequestQueue(this);
        requestQueue.add(stringRequest);
    }
    private void SendData() {
        // Response received from the server
        Response.Listener<String> responseListener = new Response.Listener<String>() {
            @Override
            public void onResponse(String response) {
                try {
                    String success = "success";
                    Log.e("response", response + "    from server");
//                            JSONObject jsonResponse = new JSONObject(response);
//                            boolean success = jsonResponse.getBoolean("success");

                    if (response.equals(success)) {
                        pdSubmit.dismiss();
                        adbConfirmation = new AlertDialog.Builder(
                                MainActivity.this);
                        adbConfirmation.setTitle("Notification").setMessage("Thanks! Your booking request has been received. We will contact you shortly.").setPositiveButton("OK",
                                new DialogInterface.OnClickListener() {
                                    public void onClick(DialogInterface dialog,
                                                        int which) {
                                    }
                                });
                        adbConfirmation.show();
                        setBlank();

                        Log.i("SUCCESS", success);
                    } else {

//                        AlertDialog.Builder builder = new AlertDialog.Builder(LocationService.this);
//                        builder.setMessage("Login Failed")
//                                .setNegativeButton("Retry", null)
//                                .create()
//                                .show();
                    }

                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        };
        pdSubmit = new ProgressDialog(MainActivity.this);
        pdSubmit.setMessage("Waiting...");
        pdSubmit.show();
        PlaceOrderRequest gpsDataRequest = new PlaceOrderRequest(getBookingData(), responseListener);
        RequestQueue queue = Volley.newRequestQueue(MainActivity.this);
        queue.add(gpsDataRequest);
    }

}
