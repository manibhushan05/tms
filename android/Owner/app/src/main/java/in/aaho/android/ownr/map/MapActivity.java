package in.aaho.android.ownr.map;

import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.location.Location;
import android.os.Bundle;
import android.os.SystemClock;
import android.support.v7.widget.DefaultItemAnimator;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.util.Log;
import android.view.Gravity;
import android.view.View;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import com.google.android.gms.maps.CameraUpdate;
import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.MapView;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.LatLngBounds;
import com.google.android.gms.maps.model.Marker;
import com.google.gson.JsonObject;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import in.aaho.android.ownr.ObjectFileUtil;
import in.aaho.android.ownr.PathMapActivity;
import in.aaho.android.ownr.R;
import in.aaho.android.ownr.VehicleGpsData;
import in.aaho.android.ownr.common.ApiResponseListener;
import in.aaho.android.ownr.common.BaseActivity;
import in.aaho.android.ownr.common.EditTextWatcher;
import in.aaho.android.ownr.common.InstantAutoComplete;
import in.aaho.android.ownr.common.InstantFocusListener;
import in.aaho.android.ownr.common.Utils;
import in.aaho.android.ownr.drivers.BrokerDriver;
import in.aaho.android.ownr.drivers.BrokerDriverDetails;
import in.aaho.android.ownr.requests.VehiclePathDataRequest;
import in.aaho.android.ownr.requests.VehicleTrackRequest;

/**
 * Created by shobhit on 29/11/16.
 * <p>
 * increase zoom for single marker
 * increase padding for multiple markers
 * back to tracking list
 * duplicate markers
 */

public class MapActivity extends BaseActivity implements OnMapReadyCallback {

    // search bar
    private InstantAutoComplete searchBar;
    private ImageButton clearBtn;

    // map
    private MapView mapView;

    //    refresh button
    private ImageButton imageButtonRefresh;

    // vehicle list
    private LinearLayout vehicleListLayout;
    private ImageView expandImageList;
    private TextView vehicleListDetailTv;
    private RecyclerView vehicleListRecyclerView;
    private LinearLayout toggleVehicleListBtn;
    private LinearLayout vehicleListContainer;
    private TextView emptyView;

    // vehicle details
    private LinearLayout vehicleDetailLayout;
    private ImageView expandImageDetail;
    private TextView vehicleNumberTv;
    private LinearLayout vehicleDetailContainer;
    private LinearLayout toggleVehicleDetailBtn;

    // vehicle card
    private LinearLayout callDriverBtn, trackBtn;
    private TextView trackCardDriverNameTv, trackCardDriverNumberTv, trackCardLocationDetailsTv;
    private TextView trackCardTruckNoTv;
    private TextView tvTrackCaption;

    // recycler view related
    private TrackVehiclesAdapter trackVehiclesAdapter;
    private final List<TrackingData> trackList = new ArrayList<>();
    // This list is build for references for suggestions from adapter
    public static final List<TrackingData> trackListNew = new ArrayList<>();

    // search bar related
    private InstantFocusListener searchFocusListener;
    private SearchVehicleArrayAdapter searchAdapter;

    // vehicle details related
    private TrackingData selectedVehicleData = null;

    // map related
    private static final float CITY_ZOOM_LEVEL = 10;
    private static final float MIN_BOUND_DISTANCE = 20 * 1000;  // 20 km
    private static final int MAP_BOUNDS_PADDING = 50;  // px

    private final MapHelper mapHelper = new MapHelper();
    private final List<Marker> markers = new ArrayList<>();
    private CameraUpdate showAllMarkers;

    private static JSONObject jsonVehiclePathData;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.map_activity);
        setToolbarTitle("Track Vehicles");

        mapView = findViewById(R.id.map_view);
        mapView.onCreate(savedInstanceState);
        mapView.getMapAsync(this);

        imageButtonRefresh = findViewById(R.id.image_btn_refresh);


        setViewVariables();
        setClickListeners();
        setupAdapters();

        loadDataFromServer();

        searchBar.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {

            }
        });
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        loadDataFromServer();
    }

    private void loadDataFromServer() {
        VehicleTrackRequest request = new VehicleTrackRequest(new TrackingDataReadyListener());
        queue(request);
    }

    private void setupAdapters() {
        setupVehicleListAdapter();
        setupSearchAdapter();
    }

    private class VehicleTrackSelectListener implements TrackSelectListener {
        @Override
        public void onSelect(TrackingData data) {
            if (data != null) {
                selectedVehicleData = data;
                setVehicleTrackUI();
            }
        }
    }

    private void setupSearchAdapter() {
        searchFocusListener = new InstantFocusListener(searchBar);
        searchAdapter = new SearchVehicleArrayAdapter(this, trackList, new VehicleTrackSelectListener());
        searchBar.setAdapter(searchAdapter);
        searchBar.setOnItemSelectedListener(searchAdapter);
        searchBar.setOnItemClickListener(searchAdapter);
        searchBar.setOnFocusChangeListener(searchFocusListener);
        //searchBar.setThreshold(2);
    }

    private void setupVehicleListAdapter() {
        trackVehiclesAdapter = new TrackVehiclesAdapter(this, trackList, new VehicleTrackSelectListener());
        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getApplicationContext());
        vehicleListRecyclerView.setLayoutManager(mLayoutManager);
        vehicleListRecyclerView.setItemAnimator(new DefaultItemAnimator());
        vehicleListRecyclerView.setAdapter(trackVehiclesAdapter);

        trackVehiclesAdapter.notifyDataSetChanged();
    }

    private void setVehicleTrackUI() {
        if (selectedVehicleData == null) {
            return;
        }
        setToolbarTitle("Track - " + selectedVehicleData.getVehicleNumber());
        vehicleDetailLayout.setVisibility(View.VISIBLE);
        vehicleListLayout.setVisibility(View.GONE);
        vehicleNumberTv.setText(Utils.def(selectedVehicleData.getVehicleNumber(), "-"));
        updateDetailCard();
        setMapDetailUI();
    }

    private void setMapDetailUI() {
        mapHelper.perform(new MapHelper.Action() {
            @Override
            public void onMapReady(GoogleMap map) {
                addMarkers(map);
                Marker activeMarker = setActiveMarker(selectedVehicleData);
                map.animateCamera(getCameraUpdate(activeMarker));
            }
        });

    }

    private void updateDetailCard() {
        TrackingData data = selectedVehicleData;
        if (data == null) {
            return;
        }
        trackCardDriverNameTv.setText(
                data.getDriver() == null ? "-" : Utils.def(data.getDriver().getName(), "-")
        );
        trackCardDriverNumberTv.setText(
                data.getDriver() == null ? "-" : Utils.def(data.getDriver().getPhone(), "-")
        );
        trackCardTruckNoTv.setText(Utils.def(data.getVehicleNumber(), "-"));
        trackCardLocationDetailsTv.setText(
                data.getLastLocation() == null ? "-" : data.getLastLocation().text()
        );
    }

    private void setTrackListUI() {
        setToolbarTitle("Track Vehicles");
        vehicleDetailLayout.setVisibility(View.GONE);
        vehicleListLayout.setVisibility(View.VISIBLE);
        if (trackList.size() == 0) {
            emptyView.setVisibility(View.VISIBLE);
            vehicleListRecyclerView.setVisibility(View.GONE);
        } else {
            emptyView.setVisibility(View.GONE);
            vehicleListRecyclerView.setVisibility(View.VISIBLE);
            trackVehiclesAdapter.notifyDataSetChanged();
        }
        updateVehicleCountUI();
        setMapListUI();
    }

    private void updateVehicleCountUI() {
        vehicleListDetailTv.setText("(" + trackList.size() + " Vehicles)");
    }

    private void setMapListUI() {
        Log.e("setMapListUI", "setMapListUI");
        mapHelper.perform(new MapHelper.Action() {
            @Override
            public void onMapReady(GoogleMap map) {
                boolean added = addMarkers(map);
                // no need to reset to defaults if added recently, it already has default values
                if (!added) {
                    resetMarkers();
                }
                if (showAllMarkers != null) {
                    map.animateCamera(showAllMarkers);
                }
            }
        });
    }

    private void resetMarkers() {
        for (Marker marker : markers) {
            setDefault(marker);
        }
    }

    private void setDefault(Marker marker) {
        marker.setAlpha(1.0f);
        marker.setIcon(MapMarkers.getSmallMarker());
    }

    private void setActive(Marker marker) {
        marker.setAlpha(1.0f);
        marker.setIcon(MapMarkers.getLargeMarker());
    }

    private void setInactive(Marker marker) {
        marker.setAlpha(0.5f);
        marker.setIcon(MapMarkers.getSmallMarker());
    }

    private Marker setActiveMarker(TrackingData data) {
        long vehicleId;
        if (data == null) {
            return null;
        } else {
            vehicleId = data.getVehicleId();
        }
        Marker activeMarker = null;
        for (int i = 0; i < trackList.size(); i++) {
            if (trackList.get(i).getVehicleId() == vehicleId) {
                activeMarker = markers.get(i);
                setActive(activeMarker);
            } else {
                setInactive(markers.get(i));
            }
        }
        return activeMarker;
    }

    private boolean addMarkers(GoogleMap map) {
        boolean added = false;
        if (markers.isEmpty()) {
            for (TrackingData data : trackList) {
                Marker marker = map.addMarker(data.getMarker());
                markers.add(marker);
                added = true;
            }
        }
        if (added) {
            showAllMarkers = getCameraUpdate(markers);
        }
        return added;
    }

    private CameraUpdate getCameraUpdate(List<Marker> markers) {
        if (Utils.not(markers)) {
            return null;
        }
        if (markers.size() == 1) {
            return getCameraUpdate(markers.get(0));
        }
        LatLngBounds.Builder builder = new LatLngBounds.Builder();
        for (Marker marker : markers) {
            builder.include(marker.getPosition());
        }
        LatLngBounds bounds = builder.build();
        float dist = getDistance(bounds.northeast, bounds.southwest);
        if (dist < MIN_BOUND_DISTANCE) {
            return CameraUpdateFactory.newLatLngZoom(bounds.getCenter(), CITY_ZOOM_LEVEL);
        } else {
            return CameraUpdateFactory.newLatLngBounds(bounds, MAP_BOUNDS_PADDING);
        }
    }

    public static float getDistance(LatLng l1, LatLng l2) {
        float[] results = new float[1];
        Location.distanceBetween(l1.latitude, l1.longitude, l2.latitude, l2.longitude, results);
        return results[0];
    }

    private CameraUpdate getCameraUpdate(Marker marker) {
        return CameraUpdateFactory.newLatLngZoom(marker.getPosition(), CITY_ZOOM_LEVEL);
    }

    private void setClickListeners() {
        clearBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                searchBar.setText("");
                searchBar.requestFocus();
            }
        });
        imageButtonRefresh.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                loadDataFromServer();
            }
        });
        toggleVehicleListBtn.setOnClickListener(
                new ToggleVisibleClickListener(vehicleListContainer, expandImageList)
        );
        toggleVehicleDetailBtn.setOnClickListener(
                new ToggleVisibleClickListener(vehicleDetailContainer, expandImageDetail)
        );
        callDriverBtn.setOnClickListener(new CallDriverClickListener());

        trackBtn.setOnClickListener(new TripHistoryClickListener());
        tvTrackCaption.setText("Trip Route");
    }

    private class ToggleVisibleClickListener implements View.OnClickListener {
        private View contentView;
        private ImageView expandImage;

        public ToggleVisibleClickListener(View contentView, ImageView expandImage) {
            this.contentView = contentView;
            this.expandImage = expandImage;
        }

        @Override
        public void onClick(View v) {
            if (contentView.getVisibility() == View.VISIBLE) {
                contentView.setVisibility(View.GONE);
                expandImage.setImageResource(R.drawable.ic_expand_more_black_24dp);
            } else {
                contentView.setVisibility(View.VISIBLE);
                expandImage.setImageResource(R.drawable.ic_expand_less_black_24dp);
            }
        }
    }

    private void setViewVariables() {

        clearBtn = findViewById(R.id.clear_btn);
        searchBar = findViewById(R.id.search_bar_text);
        toggleVehicleDetailBtn = findViewById(R.id.toggle_vehicle_detail_btn);
        toggleVehicleListBtn = findViewById(R.id.toggle_vehicle_list_btn);

        expandImageDetail = findViewById(R.id.expand_image_detail);
        expandImageList = findViewById(R.id.expand_image_list);
        vehicleDetailContainer = findViewById(R.id.vehicle_detail_container);
        vehicleDetailLayout = findViewById(R.id.vehicle_detail_layout);
        vehicleListLayout = findViewById(R.id.vehicle_list_layout);
        vehicleListContainer = findViewById(R.id.vehicle_list_container);

        vehicleListRecyclerView = findViewById(R.id.vehicle_list_recycler_view);
        vehicleListDetailTv = findViewById(R.id.vehicle_list_detail_tv);
        vehicleNumberTv = findViewById(R.id.vehicle_number_tv);

        callDriverBtn = findViewById(R.id.call_driver_btn);

        trackBtn = findViewById(R.id.track_btn);
        // commented because we now showing the trip route
        //trackBtn.setVisibility(View.INVISIBLE);
        tvTrackCaption = findViewById(R.id.tvTrackCaption);

        trackCardDriverNameTv = findViewById(R.id.track_card_driver_name_tv);
        trackCardDriverNumberTv = findViewById(R.id.track_card_driver_number_tv);
        trackCardLocationDetailsTv = findViewById(R.id.track_card_location_details_tv);
        trackCardTruckNoTv = findViewById(R.id.track_card_truck_no_tv);
        emptyView = findViewById(R.id.empty_view);
    }

    @Override
    public void onMapReady(GoogleMap googleMap) {
        mapHelper.setGoogleMap(googleMap);
    }

    private class TrackingDataReadyListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            String resp = response.toString();
            try {
                JSONObject jsonObject = new JSONObject(resp);
                JSONArray vehiclesTrackingData = jsonObject.getJSONArray("data");
                trackList.clear();
                markers.clear();
                trackList.addAll(TrackingData.fromJson(vehiclesTrackingData));
                trackListNew.addAll(trackList);
                setTrackListUI();
            } catch (JSONException e) {
                e.printStackTrace();
                toast("error reading response data:\n" + resp);
            }
        }

        @Override
        public void onError() {
            dismissProgress();
        }
    }

    private class CallDriverClickListener implements View.OnClickListener {

        @Override
        public void onClick(View v) {
            if (selectedVehicleData == null) {
                return;
            }
            BrokerDriver driver = selectedVehicleData.getDriver();
            if (driver == null) {
                Utils.toast("driver not set");
                return;
            }
            launchDialer(driver.getPhone());
        }
    }

    private class TripHistoryClickListener implements View.OnClickListener {

        @Override
        public void onClick(View v) {
            loadVehiclePathDataFromServer();
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        mapView.onResume();
    }

    @Override
    public final void onDestroy() {
        mapView.onDestroy();
        trackListNew.clear();
        jsonVehiclePathData = null;
        super.onDestroy();
    }

    @Override
    public final void onLowMemory() {
        mapView.onLowMemory();
        super.onLowMemory();
    }

    @Override
    public final void onPause() {
        mapView.onPause();
        super.onPause();
    }

    @Override
    public void onBackPressed() {
        if (vehicleDetailLayout.getVisibility() == View.VISIBLE) {
            setTrackListUI();
        } else {
            super.onBackPressed();
        }
    }


    private void loadVehiclePathDataFromServer() {
        String vehicleId = String.valueOf(selectedVehicleData.getVehicleId());
        Map<String, String> params = new HashMap<String, String>();
        params.put("vehicle_id", vehicleId);

        VehiclePathDataRequest appDataRequest = new VehiclePathDataRequest(
                params, new VehiclePathDataResponseListener());
        queue(appDataRequest);
    }

    private class VehiclePathDataResponseListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            String resp = response.toString();
            try {
                JSONObject jsonObject = new JSONObject(resp);
                jsonVehiclePathData = jsonObject.getJSONObject("data");
                if(jsonVehiclePathData == null) {
                    Toast.makeText(MapActivity.this,
                            "No Trip Data available at this moment!", Toast.LENGTH_SHORT).show();
                } else {
                    JSONArray jsonArray = jsonVehiclePathData.getJSONArray("gps_data");
                    if(jsonArray == null || jsonArray.length() == 0) {
                        Toast.makeText(MapActivity.this,
                                "No Trip Data available at this moment!", Toast.LENGTH_SHORT).show();
                    } else {
                        Intent intent = new Intent(MapActivity.this, PathMapActivity.class);
                        MapActivity.this.startActivity(intent);
                    }
                }

                //JSONArray jsonArray = jsonVehiclePathData.getJSONArray("gps_data");

                //JSONArray jsonArray = jsonObject.getJSONArray("data");


                /*if(jsonArray != null && jsonArray.length() > 0) {
                    ArrayList<VehicleGpsData> vehicleGpsDataArrayList = VehicleGpsData.getListFromJsonArray(jsonArray);
                    // write vehicleGpsData to file
                    ObjectFileUtil<ArrayList<VehicleGpsData>> objectFileUtil = new ObjectFileUtil<>(MapActivity.this,
                            "VehicleGpsData");
                    objectFileUtil.put(vehicleGpsDataArrayList);

                    Intent intent = new Intent(MapActivity.this, PathMapActivity.class);
                    //commented because list size is too large to pass in bundle
                    //intent.putExtra("VehicleGpsDataList",vehicleGpsDataArrayList);
                    MapActivity.this.startActivity(intent);
                } else {
                    Toast.makeText(MapActivity.this,
                            "No Trip Data available at this moment!", Toast.LENGTH_SHORT).show();
                }*/

            } catch (JSONException e) {
                e.printStackTrace();
                toast("error reading response data:\n" + resp);
            }
        }

        @Override
        public void onError() {
            dismissProgress();
        }
    }

    /** To get the vehicle gps data */
    public static JSONObject getJsonVehiclePathData() {
        return jsonVehiclePathData;
    }
}
