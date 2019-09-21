package in.aaho.android.employee.activity;

import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.support.v4.widget.SwipeRefreshLayout;
import android.support.v7.widget.AppCompatEditText;
import android.support.v7.widget.DefaultItemAnimator;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.support.v7.widget.Toolbar;
import android.text.Editable;
import android.text.TextUtils;
import android.text.TextWatcher;
import android.util.Log;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import com.android.volley.VolleyError;
import com.google.android.gms.common.GooglePlayServicesNotAvailableException;
import com.google.android.gms.common.GooglePlayServicesRepairableException;
import com.google.android.gms.common.api.Status;
import com.google.android.gms.location.places.AutocompleteFilter;
import com.google.android.gms.location.places.Place;
import com.google.android.gms.location.places.ui.PlaceAutocomplete;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import in.aaho.android.employee.R;
import in.aaho.android.employee.adapter.InTransitAdapter;
import in.aaho.android.employee.common.ApiResponseListener;
import in.aaho.android.employee.common.BaseActivity;
import in.aaho.android.employee.common.Utils;
import in.aaho.android.employee.other.InTransitUpdateDialog;
import in.aaho.android.employee.parser.GooglePlaceParser;
import in.aaho.android.employee.parser.InTransitParser;
import in.aaho.android.employee.requests.CommentUpdateRequest;
import in.aaho.android.employee.requests.GetInTransitDataRequest;
import in.aaho.android.employee.requests.LocationUpdateRequest;
import in.aaho.android.employee.requests.StatusUpdateRequest;

public class InTransitActivity extends BaseActivity implements
        InTransitAdapter.IOnInTransitItemSelectionListener,
        InTransitUpdateDialog.IOnInTransitUpdateListener,
        InTransitUpdateDialog.IOnInTransitLocationListener,
        View.OnClickListener{
    private final String TAG = getClass().getSimpleName();
    private List<InTransitParser> dataList = new ArrayList<>();
    private ArrayList<String> statusList = new ArrayList<>();

    private ImageView imgMoveToTop;
    private RecyclerView recyclerView;
    private SwipeRefreshLayout refreshLayout;
    private Button btnClearFilterButton;
    private AppCompatEditText filterEditText;
    private ImageView imgSearchButton;
    private LinearLayout linearFilterSection;
    private TextView tvFilterLabel;

    private InTransitAdapter adapter;
    private TextView emptyView;
    private boolean isDataLoading;
    private String url = null;
    private String roles = null;

    private InTransitParser mInTransitParser = null;
    private boolean hasInTransitDataChanged = false;
    private InTransitUpdateDialog inTransitUpdateDialog;

    /** Google places that we search from google places api */
    String googlePlaces = "";
    /**
     * Request code for google places autocomplete
     */
    private final int MI_REQ_CODE_FOR_PLACES_AUTOCOMPLETE = 101;

    public String getSearchQuery() {
        return searchQuery;
    }
    public void setSearchQuery(String searchQuery) {
        this.searchQuery = searchQuery;
    }
    private String searchQuery = "";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_in_transit);

        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        getSupportActionBar().setTitle("In Transit");

        setViewVariables();
        setClickListeners();
        setDataFromPrevActivity();
        setupAdapters();

        filterEditText.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {
            }

            @Override
            public void onTextChanged(CharSequence filterQuery, int start, int before, int count) {
                // search button visibility
                if (start == 0) {
                    imgSearchButton.setVisibility(View.INVISIBLE);
                }
                if (count > 0) {
                    imgSearchButton.setVisibility(View.VISIBLE);
                }
            }

            @Override
            public void afterTextChanged(Editable s) {
            }
        });
    }

    private void loadSearchData() {
        url = "";
        dataList.clear();
        loadDataFromServer(false);
        showProgress();
        Utils.hideKeyboard(this);
    }

    @Override
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.imgSearchButton:
                // Set search query
                String searchQuery = filterEditText.getText().toString();
                setSearchQuery(searchQuery);
                setFilterResultVisibility(searchQuery);
                loadSearchData();
                break;
            case R.id.btnClearFilterButton:
                resetFilter();
                loadSearchData();
                break;
            default:
                break;
        }
    }

    /**
     * Reset filter dialog
     */
    private void resetFilter() {
        // NOTE: do not change the sequence of code
        setSearchQuery("");
        setFilterResultVisibility("");
        filterEditText.setText("");
        linearFilterSection.setVisibility(View.GONE);
    }


    /**
     * Set visibility of search result
     */
    private void setFilterResultVisibility(String filterQuery) {
        if (TextUtils.isEmpty(filterQuery)) {
            linearFilterSection.setVisibility(View.GONE);
        } else {
            linearFilterSection.setVisibility(View.VISIBLE);
            tvFilterLabel.setText("Results for " + "'" + filterQuery.toString() + "'");
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (dataList.isEmpty()) {
            loadDataFromServer(false);
        }
    }

    @Override
    public void onBackPressed() {
        Intent data = new Intent();
        data.putExtra("hasInTransitDataChanged", hasInTransitDataChanged);
        setResult(RESULT_OK, data);
        super.onBackPressed();
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        if (item.getItemId() == android.R.id.home) {
            onBackPressed();
            return true;
        }
        return false;
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == MI_REQ_CODE_FOR_PLACES_AUTOCOMPLETE) {
            if (resultCode == RESULT_OK) {
                Place place = PlaceAutocomplete.getPlace(this, data);
                googlePlaces = GooglePlaceParser.getJsonByPlaces(place);
                // Update location value in InTransitUpdate dialog
                if(inTransitUpdateDialog != null) {
                    inTransitUpdateDialog.setLocationText(String.valueOf(place.getAddress()));
                }
            } else if (resultCode == PlaceAutocomplete.RESULT_ERROR) {
                Status status = PlaceAutocomplete.getStatus(this, data);
                Log.i(TAG, status.getStatusMessage());
            } else if (resultCode == RESULT_CANCELED) {
                // The user canceled the operation.
                Log.i(TAG, "user cancelled the google place search!");
            }
        }
    }

    private void setDataFromPrevActivity() {
        Bundle bundle = getIntent().getExtras();
        if (bundle != null) {
            if (bundle.containsKey("roles")) {
                roles = bundle.getString("roles");
            }
        }
    }

    private void setupAdapters() {
        adapter = new InTransitAdapter(this, dataList, roles, this);
        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getApplicationContext());
        recyclerView.setLayoutManager(mLayoutManager);
        recyclerView.setItemAnimator(new DefaultItemAnimator());
        recyclerView.setAdapter(adapter);
        adapter.notifyDataSetChanged();
        setRecyclerScroll();
    }

    private void setClickListeners() {
        refreshLayout.setOnRefreshListener(new SwipeRefreshLayout.OnRefreshListener() {
            @Override
            public void onRefresh() {
                url = "";
                loadDataFromServer(true);
            }
        });
        imgMoveToTop.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (recyclerView != null && dataList.size() > 0) {
                    recyclerView.scrollToPosition(0);
                }
            }
        });
    }

    private void setViewVariables() {
        recyclerView = findViewById(R.id.recycler_view);
        refreshLayout = findViewById(R.id.swipe_refresh_layout);
        emptyView = findViewById(R.id.empty_view);
        imgMoveToTop = findViewById(R.id.imgMoveToTop);

        linearFilterSection = findViewById(R.id.linear_filter_section);
        tvFilterLabel = findViewById(R.id.tvFilterLabel);
        btnClearFilterButton = findViewById(R.id.btnClearFilterButton);
        btnClearFilterButton.setOnClickListener(this);
        filterEditText = findViewById(R.id.filterEditText);
        imgSearchButton = findViewById(R.id.imgSearchButton);
        imgSearchButton.setOnClickListener(this);
    }

    private void loadDataFromServer(boolean swiped) {
        Map<String, String> params = new HashMap<String, String>();
        String searchQuery = this.getSearchQuery();
        if (!TextUtils.isEmpty(searchQuery)) {
            searchQuery = searchQuery.replace(" ", "+");
            params.put("search", searchQuery);
        }
        GetInTransitDataRequest dataRequest = new GetInTransitDataRequest(url, params,
                new InTransitListener(swiped));
        queue(dataRequest, !swiped);
    }

    private class InTransitListener extends ApiResponseListener {

        private final boolean swiped;

        InTransitListener(boolean swiped) {
            this.swiped = swiped;
        }

        @Override
        public void onResponse(JSONObject response) {
            Log.i("", response.toString());
            isDataLoading = false;
            if (swiped) {
                dataList.clear();
                refreshLayout.setRefreshing(false);
            } else {
                dismissProgress();
            }
            String resp = response.toString();
            try {
                if (response != null && response.getString("status")
                        .equalsIgnoreCase("success")) {
                    if (response.has("data")) {
                        String nextPageUrl = response.getString("next");
                        if (TextUtils.isEmpty(nextPageUrl) ||
                                nextPageUrl.equalsIgnoreCase("null")) {
                            url = "";
                        } else {
                            url = nextPageUrl;
                        }
                        JSONArray vehiclesData = response.getJSONArray("data");
                        /*dataList.clear();*/
                        dataList.addAll(InTransitParser.fromJson(vehiclesData));
                        adapter.notifyDataSetChanged();
                        setEmptyViewVisibility();
                    } else {
                        dataList.clear();
                        setEmptyViewVisibility();
                    }
                } else {
                    dataList.clear();
                    setEmptyViewVisibility();
                }
            } catch (JSONException e) {
                e.printStackTrace();
                toast("error reading response data:\n" + resp);
            }
        }

        @Override
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);
            isDataLoading = false;
            if (swiped) {
                refreshLayout.setRefreshing(false);
            } else {
                dismissProgress();
            }
            dataList.clear();
            setEmptyViewVisibility();
            try {
                if (error != null && error.networkResponse != null
                        && error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    JSONObject errorData = new JSONObject(errorMsg);
                    Utils.showInfoDialog(InTransitActivity.this,
                            Utils.getRequestMessage(errorData), Utils.getRequestData(errorData));
                    Log.i(TAG, errorMsg);
                }
            } catch (UnsupportedEncodingException ex) {
                Log.e(TAG, "UnsupportedEncodingException = " + ex.getLocalizedMessage());
            } catch (Exception ex) {
                Log.e(TAG, "Exception = " + ex.getLocalizedMessage());
            }
        }
    }

    private void setEmptyViewVisibility() {
        if (dataList.size() == 0) {
            emptyView.setVisibility(View.VISIBLE);
            recyclerView.setVisibility(View.GONE);
        } else {
            emptyView.setVisibility(View.GONE);
            recyclerView.setVisibility(View.VISIBLE);
        }
    }

    private void updateStatusRequest(Integer id, String bookingStatus, String comment,
                                     String googlePlaces) {
        StatusUpdateRequest statusUpdateRequest = new StatusUpdateRequest(
                id, bookingStatus, new InTransitActivity.UpdateStatusResponseListener(comment,
                googlePlaces));
        queue(statusUpdateRequest);
    }

    private class UpdateStatusResponseListener extends ApiResponseListener {
        private String mComment;
        private String googlePlaces;

        public UpdateStatusResponseListener(String comment, String googlePlaces) {
            this.mComment = comment;
            this.googlePlaces = googlePlaces;
        }

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            String resp = response.toString();
            try {
                String msg = Utils.get(response, "msg");
                if (response != null && response.getString("status")
                        .equalsIgnoreCase("success")) {
                    hasInTransitDataChanged = true;
                    JSONObject data = response.getJSONObject("data");
                    if (data != null && data.has("id")) {
                        Utils.toast("Status updated successfully!");
                        int bookingStatusMappingId = Integer.valueOf(Utils.get(data, "id"));
                        if (!TextUtils.isEmpty(mComment)) {
                            updateCommentRequest(bookingStatusMappingId, mComment);
                        }
                        if (!TextUtils.isEmpty(googlePlaces)) {
                            updateLocationRequest(bookingStatusMappingId, googlePlaces);
                        }
                        // Refresh List from here when status update, we are delaying list
                        // to be refreshed because we may be updating comment/location
                        new Handler().postDelayed(new Runnable() {
                            @Override
                            public void run() {
                                loadDataFromServer(true);
                            }
                        }, 1000);
                    } else {
                        Utils.toast("Status updated successfully!");
                    }
                } else {
                    Utils.toast(msg);
                }
            } catch (JSONException e) {
                e.printStackTrace();
                Utils.toast("Could not update status! Please try again later.");
                Log.e(TAG, "error reading response data:\n" + resp);
            }
        }

        @Override
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);
            dismissProgress();
            try {
                if (error != null && error.networkResponse != null
                        && error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    JSONObject errorData = new JSONObject(errorMsg);
                    Utils.showInfoDialog(InTransitActivity.this,
                            Utils.getRequestMessage(errorData), Utils.getRequestData(errorData));
                    Log.i(TAG, errorMsg);
                }
            } catch (UnsupportedEncodingException e) {
                e.printStackTrace();
            } catch (Exception ex) {
                Log.e(TAG, "Exception = " + ex.getLocalizedMessage());
            }
        }
    }

    private void updateCommentRequest(Integer id, String comment) {
        CommentUpdateRequest statusUpdateRequest = new CommentUpdateRequest(
                id, comment, new InTransitActivity.UpdateCommentResponseListener());
        queue(statusUpdateRequest);
    }

    private class UpdateCommentResponseListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            String resp = response.toString();
            try {
                String msg = Utils.get(response, "msg");
                if (response != null && response.getString("status")
                        .equalsIgnoreCase("success")) {
                    Utils.toast("Comment updated successfully!");
                } else {
                    Utils.toast(msg);
                }
            } catch (JSONException e) {
                e.printStackTrace();
                Utils.toast("Could not update comment! Please try again later.");
                Log.e(TAG, "error reading response data:\n" + resp);
            }
        }

        @Override
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);
            dismissProgress();
            try {
                if (error != null && error.networkResponse != null
                        && error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    JSONObject errorData = new JSONObject(errorMsg);
                    Utils.showInfoDialog(InTransitActivity.this,
                            Utils.getRequestMessage(errorData), Utils.getRequestData(errorData));
                    Log.i(TAG, errorMsg);
                }
            } catch (UnsupportedEncodingException e) {
                e.printStackTrace();
            } catch (Exception ex) {
                Log.e(TAG, "Exception = " + ex.getLocalizedMessage());
            }
        }
    }

    private void updateLocationRequest(Integer id, String googlePlaces) {
        LocationUpdateRequest statusUpdateRequest = new LocationUpdateRequest(id, googlePlaces,
                new UpdateLocationResponseListener());
        queue(statusUpdateRequest);
    }

    private class UpdateLocationResponseListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            String resp = response.toString();
            try {
                String msg = Utils.get(response, "msg");
                if (response != null && response.getString("status")
                        .equalsIgnoreCase("success")) {
                    Utils.toast("Location updated successfully!");
                } else {
                    Utils.toast(msg);
                }
            } catch (JSONException e) {
                e.printStackTrace();
                Utils.toast("Could not update comment! Please try again later.");
                Log.e(TAG, "error reading response data:\n" + resp);
            }
        }

        @Override
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);
            dismissProgress();
            try {
                if (error != null && error.networkResponse != null
                        && error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    JSONObject errorData = new JSONObject(errorMsg);
                    Utils.showInfoDialog(InTransitActivity.this,
                            Utils.getRequestMessage(errorData), Utils.getRequestData(errorData));
                    Log.i(TAG, errorMsg);
                }
            } catch (UnsupportedEncodingException e) {
                e.printStackTrace();
            } catch (Exception ex) {
                Log.e(TAG, "Exception = " + ex.getLocalizedMessage());
            }
        }
    }

    private void setRecyclerScroll() {
        recyclerView.addOnScrollListener(new RecyclerView.OnScrollListener() {
            @Override
            public void onScrollStateChanged(RecyclerView recyclerView, int newState) {
                super.onScrollStateChanged(recyclerView, newState);

                if (!recyclerView.canScrollVertically(1)) {
                    // Toast.makeText(getActivity(),"LAst",Toast.LENGTH_LONG).show();
                    if (isDataLoading)
                        return;
                    else {
                        if (!TextUtils.isEmpty(url)) {
                            isDataLoading = true;
                            loadDataFromServer(false);
                        }
                    }
                }
            }
        });
    }

    @Override
    public void onInTransitItemSelected(InTransitParser inTransitParser) {
        /*Show dialog from here open a dialogue box with fields
            1. Status - Options (booking_status_current and
                        primary_succeeded_booking_status)
            2. Comment - Text Field with suggestion icon on right side
                         On Click of suggestion icon, show comment suggestions (Previous
                         trip incomplete, On the way to loading point, Waiting as loading point,
                         Loading ongoing). The selected suggestion can be auto filled in Text Field.
                         User can enter text without referring suggestions
            3. Location - Text Field of city, district and country */
        mInTransitParser = inTransitParser;
        statusList.clear(); // Reset status list first
        if (inTransitParser != null) {
            // NOTE: if bookingCurrentStatus is not equal to unloaded then only show lr_generated
            // option in drop down list
            if (!TextUtils.isEmpty(inTransitParser.bookingStatusCurrent)) {
                statusList.add(inTransitParser.bookingStatusCurrent);
            }
            if (!TextUtils.isEmpty(inTransitParser.primarySucceededBookingStatus)
                    && !inTransitParser.bookingStatusCurrent.equalsIgnoreCase("unloaded")
                    && inTransitParser.primarySucceededBookingStatus.equalsIgnoreCase("unloaded")) {
                statusList.add(inTransitParser.primarySucceededBookingStatus);
            }

            // Show dialog only if status list has some data
            if (statusList.size() > 0)
                showUpdateStatusDialog();
        }
    }

    @Override
    public void onInTransitLocationClicked(String location) {
        // Start the google autocomplete places
        try {
            if(TextUtils.isEmpty(location)) {
                inTransitUpdateDialog.setLocationEditTextFocus(false);
            }
            Intent intent = new PlaceAutocomplete
                    .IntentBuilder(PlaceAutocomplete.MODE_FULLSCREEN)
                    .build(this);
            startActivityForResult(intent, MI_REQ_CODE_FOR_PLACES_AUTOCOMPLETE);
        } catch (GooglePlayServicesRepairableException e) {
            Log.i(TAG, "Error while calling the google places api, Ex=" + e.getLocalizedMessage());
        } catch (GooglePlayServicesNotAvailableException e) {
            Log.i(TAG, "Error while calling the google places api, Ex=" + e.getLocalizedMessage());
        }
    }

    @Override
    public void onInTransitUpdateClicked(String status, String comment) {
        if (!TextUtils.isEmpty(status) && status.equalsIgnoreCase(mInTransitParser.bookingStatusCurrent)) {
            // To update the comment
            if (!TextUtils.isEmpty(comment)) {
                // Update comment from here
                updateCommentRequest(mInTransitParser.bookingStatusMappingId, comment);
            }
            // To update the location
            if (!TextUtils.isEmpty(googlePlaces)) {
                // Update location from here
                updateLocationRequest(mInTransitParser.bookingStatusMappingId, googlePlaces);
            }
        } else {
            // To update the status & comment if status succeed
            updateStatusRequest(mInTransitParser.id, status, comment, googlePlaces);
        }
    }

    private void showUpdateStatusDialog() {
        // Prepare and show status update/location dialog
        inTransitUpdateDialog = new InTransitUpdateDialog(this,
                statusList, this, this);
        inTransitUpdateDialog.show();
    }

    public void setMoveToTopVisibility(int scrollPosition) {
        if (scrollPosition < 6) {
            imgMoveToTop.setVisibility(View.GONE);
        } else {
            imgMoveToTop.setVisibility(View.VISIBLE);
        }
    }

}
