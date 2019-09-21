package in.aaho.android.aahocustomers;

import android.graphics.Color;
import android.graphics.Typeface;
import android.location.Address;
import android.location.Geocoder;
import android.location.Location;
import android.os.Bundle;
import android.support.v4.app.FragmentActivity;
import android.support.v4.app.FragmentManager;
import android.util.Log;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.SupportMapFragment;
import com.google.android.gms.maps.model.CameraPosition;
import com.google.android.gms.maps.model.CustomCap;
import com.google.android.gms.maps.model.Dot;
import com.google.android.gms.maps.model.Gap;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.LatLngBounds;
import com.google.android.gms.maps.model.Marker;
import com.google.android.gms.maps.model.MarkerOptions;
import com.google.android.gms.maps.model.PatternItem;
import com.google.android.gms.maps.model.Polyline;
import com.google.android.gms.maps.model.PolylineOptions;
import com.google.android.gms.maps.model.RoundCap;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Calendar;
import java.util.Date;
import java.util.List;
import java.util.Locale;

import in.aaho.android.aahocustomers.common.DateTimePickerDialogFragment;
import in.aaho.android.aahocustomers.common.Utils;
import in.aaho.android.aahocustomers.map.MapActivity;
import in.aaho.android.aahocustomers.map.MapMarkers;

public class PathMapActivity extends FragmentActivity implements OnMapReadyCallback,
        View.OnClickListener {

    private GoogleMap mMap;
    private Button btnFilter;
    private ArrayList<VehicleGpsData> vehicleGpsDataList;
    private ArrayList<VehicleGpsData> vehicleGpsDataArrayList;
    private LatLngBounds.Builder builder = new LatLngBounds.Builder();
    private String MSTR_SPLIT_SEPERATOR = "&";
    private static final int POLYLINE_STROKE_WIDTH_PX = 12;
    private static final PatternItem DOT = new Dot();
    private static final PatternItem GAP = new Gap(2.0f);
    // max gps historical data set to 2 days by default
    private int max_gps_days_log = 2,totalDistance,distanceCovered,distanceRemaining;
    private String fromAddress,toAddress;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_path_map);

        btnFilter = findViewById(R.id.btnFilter);
        btnFilter.setOnClickListener(this);

        //commented because list size is too large to pass in bundle
        /*vehicleGpsDataArrayList = (ArrayList<VehicleGpsData>) getIntent().getSerializableExtra("VehicleGpsDataList");*/

        /*// read vehicleGpsData from file
        ObjectFileUtil<ArrayList<VehicleGpsData>> objectFileUtil = new ObjectFileUtil<>(
                PathMapActivity.this,"VehicleGpsData");
        vehicleGpsDataList = objectFileUtil.get();*/

//        JSONObject jsonVehiclePathData = MapActivity.getJsonVehiclePathData();
        JSONObject jsonVehiclePathData = null;
        try{
            jsonVehiclePathData = new JSONObject(getIntent().getStringExtra("vehicle_data"));
        } catch (JSONException e) {
            e.printStackTrace();
        }
        try {
            if(jsonVehiclePathData != null) {
                JSONArray jsonArray = jsonVehiclePathData.getJSONArray("gps_data");
                if(jsonArray != null && jsonArray.length() > 0) {
                    vehicleGpsDataList = VehicleGpsData.getListFromJsonArray(jsonArray);
                    vehicleGpsDataArrayList = vehicleGpsDataList;
                }

                max_gps_days_log = jsonVehiclePathData.optInt("max_gps_log_days");
                JSONObject jsonCurrentLocation = jsonVehiclePathData.getJSONObject("current_location");
                if(jsonCurrentLocation != null) {
                    fromAddress = jsonCurrentLocation.optString("from_address");
                    toAddress = jsonCurrentLocation.optString("to_address");
                    totalDistance = jsonCurrentLocation.optInt("total_distance");
                    distanceCovered = jsonCurrentLocation.optInt("distance_covered");
                    distanceRemaining = jsonCurrentLocation.optInt("distance_remaining");
                    JSONObject jsonFromGps = jsonCurrentLocation.getJSONObject("from_gps");
                    JSONObject jsonToGps = jsonCurrentLocation.getJSONObject("to_gps");
                }
            }
        } catch (JSONException e) {
            e.printStackTrace();
        }

        // Obtain the SupportMapFragment and get notified when the map is ready to be used.
        SupportMapFragment mapFragment = (SupportMapFragment) getSupportFragmentManager()
                .findFragmentById(R.id.map);
        mapFragment.getMapAsync(this);
    }


    /**
     * Manipulates the map once available.
     * This callback is triggered when the map is ready to be used.
     * This is where we can add markers or lines, add listeners or move the camera. In this case,
     * we just add a marker near Sydney, Australia.
     * If Google Play services is not installed on the device, the user will be prompted to install
     * it inside the SupportMapFragment. This method will only be triggered once the user has
     * installed Google Play services and returned to the app.
     */
    @Override
    public void onMapReady(GoogleMap googleMap) {
        mMap = googleMap;

        mMap.setOnPolylineClickListener(new GoogleMap.OnPolylineClickListener() {
            @Override
            public void onPolylineClick(Polyline polyline) {
                /*Toast.makeText(PathMapActivity.this,
                        ""+polyline.getPoints(), Toast.LENGTH_SHORT).show();*/
            }
        });

        mMap.setInfoWindowAdapter(new GoogleMap.InfoWindowAdapter() {

            @Override
            public View getInfoWindow(Marker arg0) {
                return null;
            }

            @Override
            public View getInfoContents(Marker marker) {

                LinearLayout info = new LinearLayout(PathMapActivity.this);
                info.setOrientation(LinearLayout.VERTICAL);

                TextView title = new TextView(PathMapActivity.this);
                title.setTextColor(Color.BLACK);
                title.setGravity(Gravity.CENTER);
                title.setTypeface(null, Typeface.BOLD);
                title.setText(marker.getTitle());
                String strSnippet = "";
                if(marker.getSnippet().contains(MSTR_SPLIT_SEPERATOR)) {
                    String splitLatLng[] = marker.getSnippet().split(MSTR_SPLIT_SEPERATOR);
                    strSnippet = "TimeStamp: " + splitLatLng[2] +
                            "\nAddress: " + getAddressByLatLng(
                            Double.parseDouble(splitLatLng[0]),
                            Double.parseDouble(splitLatLng[1]));
                } else {
                    strSnippet = marker.getSnippet();
                }

                TextView snippet = new TextView(PathMapActivity.this);
                snippet.setTextColor(Color.GRAY);
                snippet.setText(strSnippet);

                info.addView(title);
                info.addView(snippet);

                return info;
            }
        });

        //clear map before drawing route
        mMap.clear();
        // draw route on map
        drawRouteOnMap(mMap,getLatLngFromList());
    }


    private void drawRouteOnMap(GoogleMap map, List<LatLng> positions){
        PolylineOptions options = new PolylineOptions().width(7).color(Color.BLUE).geodesic(true);
        options.addAll(positions);
        Polyline polyline = map.addPolyline(options);
        polyline.setTag("A");
        polyline.setClickable(true);
        stylePolyline(polyline);
        /**create the bounds from latlngBuilder to set into map camera*/
        LatLngBounds bounds = builder.build();

        /**create the camera with bounds and padding to set into map
        if (areBoundsTooSmall(bounds, 300)) {
            mMap.animateCamera(CameraUpdateFactory.newLatLngZoom(bounds.getCenter(), 17));
        } else {
            mMap.animateCamera(CameraUpdateFactory.newLatLngBounds(bounds, 20));
        }*/

        //CameraUpdate cameraUpdate = CameraUpdateFactory.newLatLngBounds(bounds, 50);
        //map.animateCamera(cameraUpdate);


        // commented because we want to cover the entire route with map with bound
        CameraPosition cameraPosition = new CameraPosition.Builder()
                .target(new LatLng(positions.get(0).latitude, positions.get(0).longitude))
                .zoom(12)
                .build();
        map.animateCamera(CameraUpdateFactory.newCameraPosition(cameraPosition));
    }

    private boolean areBoundsTooSmall(LatLngBounds bounds, int minDistanceInMeter) {
        float[] result = new float[1];
        Location.distanceBetween(bounds.southwest.latitude, bounds.southwest.longitude,
                bounds.northeast.latitude, bounds.northeast.longitude, result);
        return result[0] < minDistanceInMeter;
    }

    private List<LatLng> getLatLngFromList() {
        List<LatLng> positions = new ArrayList<>();
        if(vehicleGpsDataArrayList != null && vehicleGpsDataArrayList.size() > 0) {
            LatLng latLng;
            for (int i = 0; i < vehicleGpsDataArrayList.size(); i++) {
                VehicleGpsData vehicleGpsData = vehicleGpsDataArrayList.get(i);
                //vehicleGpsData.setTimestamp(convertIsoDate(vehicleGpsData.getTimestamp()));
                vehicleGpsData.setTimestamp(vehicleGpsData.getTimestamp());
                latLng = new LatLng(Double.valueOf(vehicleGpsData.getLatitude()),
                        Double.valueOf(vehicleGpsData.getLongitude()));
                positions.add(latLng);
                builder.include(latLng);
                mMap.addMarker(new MarkerOptions()
                        .position(latLng)
                        .icon(MapMarkers.getCircleMarker())
                        .title("Vehicle Detail:")
                        .snippet(vehicleGpsData.getLatitude() +MSTR_SPLIT_SEPERATOR+
                                vehicleGpsData.getLongitude() +MSTR_SPLIT_SEPERATOR+
                                vehicleGpsData.getTimestamp()));
            }
        }

        /*Toast.makeText(this, "Size = "+positions.size(),
                Toast.LENGTH_SHORT).show();*/

        return positions;
    }

    // Create a stroke pattern of a gap followed by a dot.
    private static final List<PatternItem> PATTERN_POLYLINE_DOTTED = Arrays.asList(GAP, DOT);

    private void stylePolyline(Polyline polyline) {
        String type = "";
        // Get the data object stored with the polyline.
        if (polyline.getTag() != null) {
            type = polyline.getTag().toString();
        }

        switch (type) {
            // If no type is given, allow the API to use the default.
            case "A":
                // Use a custom bitmap as the cap at the start of the line.
                //polyline.setPattern(PATTERN_POLYLINE_DOTTED);
                polyline.setStartCap(new CustomCap(
                                MapMarkers.getLargeMarker(), 5));
                break;
            case "B":
                // Use a round cap at the start of the line.
                polyline.setStartCap(new RoundCap());
                break;
        }

        polyline.setEndCap(new RoundCap());
        polyline.setColor(Color.BLUE);
        //polyline.setJointType(JointType.ROUND);
    }

    private String convertIsoDate(String dateString) {
        String convertedDate = "";
        //Parse the string into a date variable
        Date parsedDate = null;
        try {
            parsedDate = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSSSS").parse(dateString);
            //Now reformat it using desired display pattern:
            convertedDate = new SimpleDateFormat(Utils.strDateTimeFormat).format(parsedDate);
        } catch (ParseException e) {
            e.printStackTrace();
        }

        return convertedDate;
    }

    /** filter the given list with given date range and return the filtered list
     * @param fromDate from date
     * @param toDate to date
     */
    private ArrayList<LatLng> filterListWithDateRange(ArrayList<VehicleGpsData> listToFilter,
                                                      String fromDate, String toDate) {
        ArrayList<LatLng> dataArrayList = new ArrayList<>();
        try {
            Date dtFromDate = Utils.parseDateTime(fromDate);
            Date dtToDate = Utils.parseDateTime(toDate);
            if(listToFilter != null && listToFilter.size() > 0) {
                LatLng latLng;
                for (int iCount = 0; iCount < listToFilter.size() ; iCount++) {
                    String timestamp = listToFilter.get(iCount).getTimestamp();
                    Date dateTime = Utils.parseDateTime(timestamp);
                    if( (dateTime.compareTo(dtFromDate) < 0)
                            || (dateTime.compareTo(dtToDate) > 0)) {
                        // not within range
                    } else {
                        // within range
                        latLng = new LatLng(Double.parseDouble(listToFilter.get(iCount).getLatitude()),
                                Double.parseDouble(listToFilter.get(iCount).getLongitude()));
                        dataArrayList.add(latLng);
                        mMap.addMarker(new MarkerOptions()
                                .position(latLng)
                                .icon(MapMarkers.getCircleMarker())
                                //.icon(BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_RED))
                                .title("Vehicle Detail:")
                                .snippet(listToFilter.get(iCount).getLatitude() +MSTR_SPLIT_SEPERATOR+
                                        listToFilter.get(iCount).getLongitude() +MSTR_SPLIT_SEPERATOR+
                                        listToFilter.get(iCount).getTimestamp()));
                    }
                }
            }
        } catch (Exception ex) {
            Log.e("filterListWithDateRange","Exception while filtering with date range!"+ex.getLocalizedMessage());
        }

        /*Toast.makeText(this, "Size = "+dataArrayList.size(),
                Toast.LENGTH_SHORT).show();*/

        return dataArrayList;
    }

    @Override
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.btnFilter:
                showFilterDialog();
                break;
            default:
                break;
        }
    }

    // show date time picker dialog
    private void showFilterDialog() {
        Calendar calendar = Calendar.getInstance();
        calendar.add(Calendar.DAY_OF_MONTH,-max_gps_days_log);
        long minDate = calendar.getTime().getTime(); // in milliseconds
        FragmentManager fm = getSupportFragmentManager();
        DateTimePickerDialogFragment editNameDialogFragment =
                new DateTimePickerDialogFragment(minDate,
                        new DateTimePickerDialogFragment.FilterDialogListener() {
            @Override
            public void onFinishFilterDialog(String fromDate, String toDate) {
                ArrayList<LatLng> latLngArrayList = filterListWithDateRange(
                        vehicleGpsDataArrayList,fromDate,toDate);
                if(latLngArrayList != null && latLngArrayList.size() > 0) {
                    //clear map before drawing route
                    mMap.clear();
                    drawRouteOnMap(mMap, latLngArrayList);
                }
                else {
                    Toast.makeText(PathMapActivity.this,
                            "No data availbale withing given date range!", Toast.LENGTH_LONG).show();
                }
            }
        });
        editNameDialogFragment.show(fm, "fragment_pick_date");
    }

    private String getAddressByLatLng(Double lat, Double lng) {
        String address = "NA";
        Geocoder geocoder;
        List<Address> addresses;
        geocoder = new Geocoder(this, Locale.getDefault());

        try {
            addresses = geocoder.getFromLocation(lat, lng, 1); // Here 1 represent max location result to returned, by documents it recommended 1 to 5
            String strAddress = addresses.get(0).getAddressLine(0); // If any additional address line present than only, check with max available address lines by getMaxAddressLineIndex()
            /*String city = addresses.get(0).getLocality()!=null?addresses.get(0).getLocality():"";
            String state = addresses.get(0).getAdminArea()!=null?addresses.get(0).getAdminArea():"";
            String country = addresses.get(0).getCountryName()!=null?addresses.get(0).getCountryName():"";
            String postalCode = addresses.get(0).getPostalCode()!=null?addresses.get(0).getPostalCode():"";*/
            //String knownName = addresses.get(0).getFeatureName(); // Only if available else return NULL

            address = strAddress; /*+ " " + city + " " + state + "\n" + country
                        + " " + postalCode;*/
        } catch (IOException e) {
            e.printStackTrace();
        }

        return address;
    }


}
