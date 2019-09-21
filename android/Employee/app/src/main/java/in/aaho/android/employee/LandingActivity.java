package in.aaho.android.employee;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.support.design.widget.NavigationView;
import android.support.v4.view.GravityCompat;
import android.support.v4.widget.DrawerLayout;
import android.support.v4.widget.SwipeRefreshLayout;
import android.support.v7.app.ActionBarDrawerToggle;
import android.support.v7.widget.CardView;
import android.support.v7.widget.Toolbar;
import android.text.TextUtils;
import android.util.Log;
import android.view.KeyEvent;
import android.view.MenuItem;
import android.view.View;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import com.android.volley.VolleyError;
import com.google.firebase.messaging.RemoteMessage;
import com.squareup.otto.Bus;
import com.squareup.otto.Subscribe;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.UnsupportedEncodingException;
import java.util.HashMap;
import java.util.Map;

import in.aaho.android.employee.activity.CustomerPendingPaymentActivity;
import in.aaho.android.employee.activity.DeliveredActivity;
import in.aaho.android.employee.activity.InTransitActivity;
import in.aaho.android.employee.activity.InvoiceConfirmationActivity;
import in.aaho.android.employee.activity.NotificationActivity;
import in.aaho.android.employee.activity.PendingLRActivity;
import in.aaho.android.employee.common.ApiResponseListener;
import in.aaho.android.employee.common.BaseActivity;
import in.aaho.android.employee.common.MainApplication;
import in.aaho.android.employee.common.Utils;
import in.aaho.android.employee.loads.AvailableLoadsActivity;
import in.aaho.android.employee.loads.MyLoadsActivity;
import in.aaho.android.employee.notification.MyNotification;
import in.aaho.android.employee.requests.EmployeeRoleFuncMappingList;
import in.aaho.android.employee.requests.EmployeeRolesMappingList;
import in.aaho.android.employee.requests.LogoutRequest;
import in.aaho.android.employee.support.ContactUsActivity;

/**
 * Created by aaho on 07/05/18.
 */

public class LandingActivity extends BaseActivity
        implements NavigationView.OnNavigationItemSelectedListener {

    private static final String TAG = "LandingActivity";
    private Toolbar toolbar;
    private CardView cvNewLoads;
    private CardView cvCustomerLoads;
    private CardView cvMyLoads;
    private ImageView imgNotification,myProfile;
    private TextView navUserNameTextView, navRoleNameTextView,
            empty_view, tvNotificationCount;

    private SwipeRefreshLayout refreshLayout;
    private LinearLayout linear_container;
    private int roleId, roleLength;
    private int aahoOfficeId;
    private final int MI_REQ_CODE_FOR_IN_TRANSIT = 101;

    private String roles = "";
    /** This count is used to set the APP url from mobile end */
    private int mCountForUrl = 0;

    /**
     * This list contains the functionality names we are going to display
     */
    private Map<String, Integer> listTDFunctionality = new HashMap<>();

    public static Bus bus;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_landing);

        toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        getSupportActionBar().setTitle(R.string.app_name);

        setViewVariables();
        setClickListeners();
        updateUserName();
        setRoleName(); // reset roles here
        initBus();

        loadInitialDataFromServer(100);
    }

    /**
     * Initialize the Bus
     */
    private void initBus() {
        try {
            bus = MainApplication.getBus();
            bus.register(this);
        } catch (Exception ex) {
            Log.e(TAG, "Failed to Init Bus, Ex=" + ex.getLocalizedMessage());
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        checkAndGetPerms();
        setMyNotificationCount();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
    }

    private void loadInitialDataFromServer(int time) {
        final Handler handler = new Handler();
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                makeEmpRoleMappingListRequest(false);
            }
        }, time);
    }

    private void makeEmpRoleMappingListRequest(boolean swiped) {
        listTDFunctionality.clear();
        linear_container.removeAllViews(); // Removes dynamic view here
        Map<String, String> params = new HashMap<String, String>();
        params.put("employee_id", Aaho.getEmployeeId());
        EmployeeRolesMappingList request = new EmployeeRolesMappingList(params,
                new EmployeeRolesMappingListListener(swiped));
        queue(request, false);
    }

    private class EmployeeRolesMappingListListener extends ApiResponseListener {
        private final boolean swiped;

        public EmployeeRolesMappingListListener(boolean swiped) {
            this.swiped = swiped;
        }

        @Override
        public void onResponse(JSONObject response) {
            if (swiped) {
                refreshLayout.setRefreshing(false);
            } else {
                dismissProgress();
            }
            boolean result = false;
            try {
                if (Utils.isRequestSuccess(response)) {
                    JSONArray data = response.getJSONArray("data");
                    if (data != null && data.length() > 0) {
                        roleLength = data.length();
                        for (int i = 0; i < data.length(); i++) {
                            JSONObject employeeRole = data.getJSONObject(i)
                                    .getJSONObject("employee_role");
                            if (employeeRole != null) {
                                roleId = employeeRole.getInt("id");
                                // Set roles
                                if (TextUtils.isEmpty(roles)) {
                                    roles = Utils.get(employeeRole, "role");
                                } else {
                                    if (!roles.contains(Utils.get(employeeRole, "role")))
                                        roles = roles + ", " + Utils.get(employeeRole, "role");
                                }
                                setRoleName();
                                Aaho.setRoles(roles);

                                if (roleId != 0) {
                                    /*makeEmpRoleFunListRequest();*/
                                    // get the aaho office id
                                    JSONObject employee = data.getJSONObject(i)
                                            .getJSONObject("employee");
                                    if (employee != null) {
                                        aahoOfficeId = employee.getInt("aaho_office_id");
                                        if (aahoOfficeId != 0) {
                                            result = true;
                                            makeEmpRoleFunListRequest();
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            } catch (JSONException e) {
                e.printStackTrace();
                Log.e(TAG, "Exeption ex = " + e.getLocalizedMessage());
            }

            if (!result) {
                String msg = Utils.getRequestMessage(response);
                if (TextUtils.isEmpty(msg)) {
                    showDialog("Couldn't find Employee Role!\nDo you want to retry now?");
                } else {
                    showDialog(msg + "\nDo you want to retry now?");
                }
            }
        }

        @Override
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);
            if (swiped) {
                refreshLayout.setRefreshing(false);
            } else {
                dismissProgress();
            }
            try {
                if (error != null && error.networkResponse != null
                        && error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    JSONObject errorData = new JSONObject(errorMsg);
                    Utils.showInfoDialog(LandingActivity.this,
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

    private void makeEmpRoleFunListRequest() {
        Map<String, String> params = new HashMap<>();
        params.put("employee_role_id", roleId + "");
        EmployeeRoleFuncMappingList request = new EmployeeRoleFuncMappingList(params,
                new EmployeeRoleFuncMappingListListener());
        queue(request, false);
    }

    private class EmployeeRoleFuncMappingListListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            boolean result = false;
            try {
                if (response != null) {
                    JSONArray data = response.getJSONArray("data");
                    if (data != null && data.length() > 0) {
                        result = generateDynamicLayout(data);
                    }
                }
            } catch (JSONException e) {
                e.printStackTrace();
                showDialog("Couldn't find Employee Role Functionality!\nDo you want to retry now?");
            }

            if (roleLength != 0)
                roleLength--;

            if (!result && roleLength == 0 && listTDFunctionality.size() == 0) {
                String msg = Utils.getRequestMessage(response);
                empty_view.setVisibility(View.VISIBLE);
                if (TextUtils.isEmpty(msg)) {
                    showDialog("Couldn't find Employee Role Functionality!\nDo you want to retry now?");
                } else {
                    showDialog(msg + "\nDo you want to retry now?");
                }
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
                    Utils.toast(errorMsg);
                    Log.i(TAG, errorMsg);
                }
            } catch (UnsupportedEncodingException e) {
                e.printStackTrace();
            } catch (Exception ex) {
                Log.e(TAG, "Exception = " + ex.getLocalizedMessage());
            }
        }
    }

    /**
     * Generate UI Dynamically
     *
     * @param data JSonArray to process
     */
    private boolean generateDynamicLayout(JSONArray data) {
        boolean result = false;
        try {
            for (int count = 0; count < data.length(); count++) {
                View cardLayout = getLayoutInflater().inflate(R.layout.button_layout, null);
                LinearLayout.LayoutParams buttonLayoutParams = new LinearLayout
                        .LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT);
                buttonLayoutParams.setMargins(2, 2, 2, 2);
                cardLayout.setLayoutParams(buttonLayoutParams);
                TextView tvMenuOption = cardLayout.findViewById(R.id.tvMenuName);
                TextView tvFunCount = cardLayout.findViewById(R.id.tvFunCount);
                JSONObject jsonObject = data.getJSONObject(count);
                int id = 0;
                String functionalityName = "";
                String consumerName = "";
                if (jsonObject != null) {
                    JSONObject td_functionality = jsonObject.getJSONObject("td_functionality");
                    if (td_functionality != null) {
                        id = Integer.valueOf(Utils.get(td_functionality, "id"));
                        functionalityName = Utils.get(td_functionality, "functionality");
                        consumerName = Utils.get(td_functionality, "consumer");
                        if(consumerName.equalsIgnoreCase("web")){
                            continue;
                        }
                        cardLayout.setTag(functionalityName);
                    }
                }
                final String caption = Utils.get(jsonObject, "caption");
                String functionalityCount = Utils.get(jsonObject, "current_functionality_count");
                if (listTDFunctionality.containsKey(functionalityName)) {
                    // It means this is already added in functionality list, don't add again
                    // check for count if greater update new count
                    Integer prevCount = listTDFunctionality.get(functionalityName);
                    if (prevCount < Integer.valueOf(functionalityCount)) {
                        int childLength = linear_container.getChildCount();
                        for (int childCounter = 0; childCounter < childLength; childCounter++) {
                            View childCardLayout = linear_container.getChildAt(childCounter);
                            String tag = String.valueOf(childCardLayout.getTag());
                            if (tag.equalsIgnoreCase(functionalityName)) {
                                TextView tvFunCountUpdate = childCardLayout.findViewById(R.id.tvFunCount);
                                tvFunCountUpdate.setText(functionalityCount);
                                listTDFunctionality.put(functionalityName, Integer.valueOf(functionalityCount));
                                break;
                            }
                        }
                    }
                } else {
                    // It means this is new functionality & need to add in list
                    if (!TextUtils.isEmpty(caption)) {
                        /*listTDFunctionality.add(functionalityName);*/
                        listTDFunctionality.put(functionalityName, Integer.valueOf(functionalityCount));
                        tvMenuOption.setId(id);
                        tvMenuOption.setText(caption);
                        if (TextUtils.isEmpty(functionalityCount) ||
                                functionalityCount.equalsIgnoreCase("0") ||
                                !TDFunctionality.isWorkingFunctionality(functionalityName)) {
                            tvFunCount.setVisibility(View.INVISIBLE);
                        } else {
                            tvFunCount.setText(functionalityCount);
                            tvFunCount.setVisibility(View.VISIBLE);
                        }
                        linear_container.addView(cardLayout);
                        result = true;

                        final int finalId = id;
                        final String finalFunctionalityName = functionalityName;
                        cardLayout.setOnClickListener(new View.OnClickListener() {
                            @Override
                            public void onClick(View view) {
                                setFunctionality(finalFunctionalityName);
                            }
                        });
                    }
                }
            }
        } catch (Exception ex) {
            Log.e(TAG, "Error while generating dynamic layout! " +
                    "Exception = " + ex.getLocalizedMessage());
        }

        return result;
    }

    public void updateUserName() {
        if (navUserNameTextView != null) {
            if (TextUtils.isEmpty(Aaho.getUserFullname())) {
                navUserNameTextView.setText(Aaho.getUsername());
            } else {
                navUserNameTextView.setText(Aaho.getUserFullname());
            }
        }
    }

    private void setRoleName() {
        if (navRoleNameTextView != null) {
            if (TextUtils.isEmpty(roles)) {
                navRoleNameTextView.setText("No Role Assigned");
            } else {
                navRoleNameTextView.setText(roles);
            }
        }
    }

    public void setViewVariables() {
        //cvNewLoads = findViewById(R.id.card_view_new_loads);
        cvCustomerLoads = findViewById(R.id.card_view_available_loads);
        //cvMyLoads = findViewById(R.id.card_view_my_loads);
        linear_container = findViewById(R.id.linear_container);
        empty_view = findViewById(R.id.empty_view);
        refreshLayout = findViewById(R.id.swipe_refresh_layout);
        tvNotificationCount = findViewById(R.id.tvNotificationCount);
        imgNotification = findViewById(R.id.imgNotification);

        // Drawer initialization
        DrawerLayout drawer = findViewById(R.id.drawer_layout);
        ActionBarDrawerToggle toggle = new ActionBarDrawerToggle(
                this, drawer, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close);
        drawer.addDrawerListener(toggle);
        toggle.syncState();

        NavigationView navigationView = findViewById(R.id.nav_view);
        navigationView.setNavigationItemSelectedListener(this);

        View header = navigationView.getHeaderView(0);
        navUserNameTextView = header.findViewById(R.id.side_nav_company_name);
        navRoleNameTextView = header.findViewById(R.id.side_nav_roles);
        myProfile = header.findViewById(R.id.myProfile);
    }

    private void setClickListeners() {
        refreshLayout.setOnRefreshListener(new SwipeRefreshLayout.OnRefreshListener() {
            @Override
            public void onRefresh() {
                makeEmpRoleMappingListRequest(true);
            }
        });
        imgNotification.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                // call the notification api to get all the notification list
                /*setNotificationCount(0); // once clicked hide the count
                getNotificationList();*/
                startActivity(new Intent(LandingActivity.this, NotificationActivity.class));
            }
        });
        myProfile.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                /*if(mCountForUrl > 10) {
                    mCountForUrl = 0;
                    // launch dialog to set URL
                    Utils.toast("Profile clicked");
                } else {
                    mCountForUrl++;
                }*/
            }
        });
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
            //App.clearAppData();
            Aaho.setToken(null);
            startActivity(new Intent(LandingActivity.this, LoginActivity.class));
            LandingActivity.this.finish();
        }

        @Override
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);
            Aaho.setToken(null);
            startActivity(new Intent(LandingActivity.this,
                    LoginActivity.class));
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

    private void setFunctionality(String functionalityName) {
        Intent intent = null;
        Bundle bundle = new Bundle();
        switch (functionalityName) {
            case TDFunctionality.PENDING_PAYMENTS:
                bundle.putString("roles", roles);
                intent = new Intent(LandingActivity.this,
                        CustomerPendingPaymentActivity.class);
                intent.putExtras(bundle);
                startActivity(intent);
                break;
            case TDFunctionality.CUSTOMER_INQUIRY:
                bundle.putInt("roleId", roleId);
                bundle.putInt("aahoOfficeId", aahoOfficeId);
                bundle.putString("status", "unverified");
                bundle.putString("roles", roles);
                bundle.putString("toolbarName", "Customer Inquiries");
                intent = new Intent(LandingActivity.this,
                        AvailableLoadsActivity.class);
                intent.putExtras(bundle);
                startActivity(intent);
                break;
            case TDFunctionality.PENDING_LR:
                bundle.putString("roles", roles);
                intent = new Intent(LandingActivity.this,
                        PendingLRActivity.class);
                intent.putExtras(bundle);
                startActivity(intent);
                break;
            case TDFunctionality.IN_TRANSIT:
                bundle.putString("roles", roles);
                intent = new Intent(LandingActivity.this,
                        InTransitActivity.class);
                intent.putExtras(bundle);
                startActivityForResult(intent,MI_REQ_CODE_FOR_IN_TRANSIT);
                break;
            case TDFunctionality.DELIVERED:
                bundle.putString("roles", roles);
                intent = new Intent(LandingActivity.this,
                        DeliveredActivity.class);
                intent.putExtras(bundle);
                startActivity(intent);
                break;
            case TDFunctionality.INVOICE_CONFIRMATION:
                bundle.putString("roles", roles);
                intent = new Intent(LandingActivity.this,
                        InvoiceConfirmationActivity.class);
                intent.putExtras(bundle);
                startActivity(intent);
                break;
            case TDFunctionality.NEW_INQUIRY:
                bundle.putString("toolbarName", "New Inquiry");
                bundle.putBoolean("isUpdate", false);
                intent = new Intent(LandingActivity.this,
                        RequirementActivity.class);
                intent.putExtras(bundle);
                startActivity(intent);
                break;
            case TDFunctionality.MY_INQUIRY:
                bundle.putInt("aahoOfficeId", aahoOfficeId);
                bundle.putString("roles", roles);
                intent = new Intent(LandingActivity.this,
                        MyLoadsActivity.class);
                intent.putExtras(bundle);
                startActivity(intent);
                break;
            case TDFunctionality.OPEN_INQUIRY:
                bundle.putInt("roleId", roleId);
                bundle.putInt("aahoOfficeId", aahoOfficeId);
                bundle.putString("status", "open");
                bundle.putString("roles", roles);
                bundle.putString("toolbarName", "Open Inquiries");
                intent = new Intent(LandingActivity.this,
                        AvailableLoadsActivity.class);
                intent.putExtras(bundle);
                startActivity(intent);
                break;
            case TDFunctionality.SEND_INVOICE:
                Utils.customToast("Coming soon");
                break;
            case TDFunctionality.PAY_BALANCE:
                Utils.customToast("Coming soon");
                break;
            case TDFunctionality.PAY_ADVANCE:
                Utils.customToast("Coming soon");
                break;
            case TDFunctionality.LR_GENERATION:
                Utils.customToast("Coming soon");
                break;
            case TDFunctionality.CONFIRM_BOOKING:
                Utils.customToast("Coming soon");
                break;
            case TDFunctionality.RECONCILE:
                Utils.customToast("Coming soon");
                break;
            case TDFunctionality.PROCESS_PAYMENTS:
                Utils.customToast("Coming soon");
                break;
            case TDFunctionality.INWARD_ENTRY:
                Utils.customToast("Coming soon");
                break;
            case TDFunctionality.CONFIRM_INVOICE:
                Utils.customToast("Coming soon");
                break;
            case TDFunctionality.RAISE_INVOICE:
                Utils.customToast("Coming soon");
                break;
            case TDFunctionality.VERIFY_POD:
                Utils.customToast("Coming soon");
                break;
            default:
                break;
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if(requestCode == MI_REQ_CODE_FOR_IN_TRANSIT) {
            if(resultCode == Activity.RESULT_OK) {
                // Update In Transit notification count
                // get the flag from data to know if want to refresh data
                if(data != null) {
                    if(data.getBooleanExtra("hasInTransitDataChanged",false))
                        makeEmpRoleMappingListRequest(true);
                }
            }
        }
    }

    private class CustomAlertDialogListener implements Utils.AlertDialogListener {

        @Override
        public void onPositiveButtonClicked() {
            loadInitialDataFromServer(100);
        }

        @Override
        public void onNegativeButtonClicked() {
            LandingActivity.this.finish();
        }
    }

    private void showDialog(String msg) {
        Utils.showAlertDialog(LandingActivity.this,
                getString(R.string.app_name),
                msg, "Retry", "Exit",
                new CustomAlertDialogListener());
    }

    /**
     * Update notification count for specified functionality
     */
    private void updateNotificationCount(String functionalityName, int functionalityCount) {
        try {
            Integer prevCount = listTDFunctionality.get(functionalityName);
            if (prevCount != null) {
                int childLength = linear_container.getChildCount();
                for (int childCounter = 0; childCounter < childLength; childCounter++) {
                    View childCardLayout = linear_container.getChildAt(childCounter);
                    String tag = String.valueOf(childCardLayout.getTag());
                    if (tag.equalsIgnoreCase(functionalityName)) {
                        final TextView tvFunCountUpdate = childCardLayout.findViewById(R.id.tvFunCount);
                        functionalityCount = prevCount + functionalityCount;
                        final int finalFunctionalityCount = functionalityCount;
                        this.runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                setNotificationCountText(tvFunCountUpdate, finalFunctionalityCount);
                            }
                        });
                        listTDFunctionality.put(functionalityName, Integer.valueOf(functionalityCount));
                        break;
                    }
                }
            }
        } catch (Exception ex) {
            Log.e(TAG, "Exception while updating functionality count" + ex.getLocalizedMessage());
        }
    }

    private void setNotificationCountText(TextView tvFunCountUpdate, int functionalityCount) {
        try {
            tvFunCountUpdate.setText(String.valueOf(functionalityCount));
            tvFunCountUpdate.setVisibility(View.VISIBLE);
        } catch (Exception ex) {
            Log.e(TAG, "Failed to update texview count, ex=" + ex.getLocalizedMessage());
        }
    }

    /*This method is used to update the notification count via push notification */
    @Subscribe
    public void onPushMessageReceived(RemoteMessage remoteMessage) {
        if (remoteMessage != null) {
            if (remoteMessage.getData() != null) {
                if (remoteMessage.getData().containsKey("is_count_update")) {
                    boolean isCountUpdate = Boolean.valueOf(remoteMessage.getData()
                            .get("is_count_update").toString());
                    if (isCountUpdate) {
                        if (remoteMessage.getData().containsKey("functionality")) {
                            String functionalityName = remoteMessage.getData().get("functionality");
                            if (remoteMessage.getData().containsKey("notification_count")) {
                                Integer functionalityCount = Integer.valueOf(remoteMessage.getData().get("notification_count"));
                                // Notify activity to update count
                                updateNotificationCount(functionalityName, functionalityCount);
                            }
                        }
                    }
                }
                String title = "", body = "";
                if (remoteMessage.getData().containsKey("title")) {
                    title = remoteMessage.getData().get("title");
                }
                if (remoteMessage.getData().containsKey("body")) {
                    body = remoteMessage.getData().get("body");
                }
                saveNotificationData(title, body);
            }
        }
    }

    /**
     * Save today's notification data
     */
    private void saveNotificationData(String title, String body) {
        MyNotification myNotification = new MyNotification(
                MyNotification.getTodayDate("ddMMyyyy"), title, body,
                MyNotification.getTodayDate("dd-MM-yyyy hh:mm:ss"));
        String jsonNotification = myNotification.toJson(myNotification);
        Aaho.setMyNotification(jsonNotification);
        setMyNotificationCount();
    }

    /* set my notification count */
    private void setMyNotificationCount() {
        final int count = MyNotification.getMyNotificationCount(Aaho.getMyNotificationJson());
        this.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                if(count > 0) {
                    tvNotificationCount.setVisibility(View.VISIBLE);
                } else {
                    tvNotificationCount.setVisibility(View.INVISIBLE);
                }
                tvNotificationCount.setText(String.valueOf(count));
            }
        });
    }

}