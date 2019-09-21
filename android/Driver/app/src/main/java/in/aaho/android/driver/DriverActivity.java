
package in.aaho.android.driver;

import android.Manifest;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.location.LocationManager;
import android.os.Build;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.support.v7.app.AppCompatDialogFragment;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.ImageButton;
import android.widget.LinearLayout;
import android.widget.TextView;

import org.json.JSONException;
import org.json.JSONObject;

import java.lang.ref.WeakReference;
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;

import in.aaho.android.driver.common.ApiResponseListener;
import in.aaho.android.driver.common.BaseActivity;
import in.aaho.android.driver.common.Lang;
import in.aaho.android.driver.common.LanguageSelectDialogFragment;
import in.aaho.android.driver.common.Utils;
import in.aaho.android.driver.docs.Pod;
import in.aaho.android.driver.docs.PODEditFragment;
import in.aaho.android.driver.requests.Api;
import in.aaho.android.driver.requests.PodUpdateRequest;
import in.aaho.android.driver.requests.VehiclePodDetailsRequest;
import in.aaho.android.driver.requests.VehicleStatusRequest;
import in.aaho.android.driver.tracking.FusedPositionProvider;
import in.aaho.android.driver.tracking.StatusDialog;
import in.aaho.android.driver.tracking.TrackingService;


public class DriverActivity extends BaseActivity {

    public static final int GPS_SETTINGS_REQUEST = 1099;

    public static boolean resolvingLocationSetting = false;
    public static boolean resolvingPerms = false;

    public static final String NETWORK_PROVIDER = LocationManager.NETWORK_PROVIDER;
    public static final String GPS_PROVIDER = LocationManager.GPS_PROVIDER;
    public static final String MIXED_PROVIDER = "mixed";
    public static final String FUSED_PROVIDER = "fused";

    private static final int PERMISSIONS_REQUEST_LOCATION = 2;
    private static final String[] permissions = {
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION,
            Manifest.permission.READ_PHONE_STATE,
            Manifest.permission.RECEIVE_SMS,
            Manifest.permission.READ_SMS,
            Manifest.permission.READ_EXTERNAL_STORAGE,
            Manifest.permission.WRITE_EXTERNAL_STORAGE,
            Manifest.permission.CAMERA
    };

    private static WeakReference<DriverActivity> instanceRef;

    private boolean paused = false;

    public static final String STATUS_UNLOADED = "unloaded";
    public static final String STATUS_LOADING = "loading";
    public static final String STATUS_LOADED = "loaded";
    public static final String STATUS_UNLOADING = "unloading";

    public static final float BTN_DISABLED_ALPHA = 0.5f;
    public static final float BTN_ENABLED_ALPHA = 1.0f;

    private ImageButton btnStatus;
    private ImageButton btnUnloaded;
    private ImageButton btnLoading;
    private ImageButton btnLoaded;
    private ImageButton btnUnloading;
    private LinearLayout uploadPodBtn;
    private TextView uploadPodText;
    private TextView txtVehicleStatus;
    private TextView txtVehicleStatusDesc;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        instanceRef = new WeakReference<>(this);
        setContentView(R.layout.activity_main);
        setTitle(R.string.app_name);


        boolean hasPerms = resolveMissingPermissions();
        if (hasPerms) {
            setDeviceIdAndStartService();
        }

        setViewRefs();
        setClickListeners();
        if (!Aaho.isRegistered()) {
            showRegisterDialog(false);
        }

        updateUI();
    }

    private void setClickListeners() {
        btnStatus.setOnClickListener(new StatusCycleOnClickListener());
        btnUnloaded.setOnClickListener(new StatusOnClickListener(STATUS_UNLOADED));
        btnLoading.setOnClickListener(new StatusOnClickListener(STATUS_LOADING));
        btnLoaded.setOnClickListener(new StatusOnClickListener(STATUS_LOADED));
        btnUnloading.setOnClickListener(new StatusOnClickListener(STATUS_UNLOADING));
        uploadPodBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                getVehiclePodDetails();
            }
        });
    }

    private void getVehiclePodDetails() {
        VehiclePodDetailsRequest request = new VehiclePodDetailsRequest(new VehiclePodDetailsResponseListener());
        queue(request);
    }

    class VehiclePodDetailsResponseListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            try {
                Log.e("response", response + "    from server");

                if (response.getString("status").equals(Api.STATUS_SUCCESS)) {
                    Log.e("SUCCESS", Api.STATUS_SUCCESS);
                    boolean canUploadPod = response.getBoolean("can_upload_pod");
                    JSONObject podDetails = Utils.getObject(response, "pod_details");
                    setPodDetails(canUploadPod, podDetails);
                    launchPodDialog();
                } else {
                    throw new AssertionError(response.toString());
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }

        @Override
        public void onError() {
            dismissProgress();
        }
    }

    private void launchPodDialog() {
        PODEditFragment.ResultListener listener = new PODEditFragment.ResultListener() {
            @Override
            public void onResult(PODEditFragment.Result result) {
                updatePod(result);
            }
        };

        PODEditFragment.Builder builder = new PODEditFragment.Builder(this, listener);
        builder.setValues(Aaho.getPodDetails());
        builder.build();
    }

    private void updatePod(PODEditFragment.Result result) {
        if (result != null && result.isEdited()) {
            makePodUpdateRequest(result);
        }
    }

    private void makePodUpdateRequest(PODEditFragment.Result result) {
        PodUpdateRequest request = new PodUpdateRequest(result.getUrl(), result.getThumbUrl(), new PodUpdateResponseListener());
        queue(request);
    }

    class PodUpdateResponseListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            try {
                Log.e("response", response + "    from server");

                if (response.getString("status").equals(Api.STATUS_SUCCESS)) {
                    Log.e("SUCCESS", Api.STATUS_SUCCESS);
                    JSONObject podDetails = Utils.getObject(response, "pod_details");
                    setPodDetails(true, podDetails);
                    toast("POD updated");
                } else {
                    throw new AssertionError(response.toString());
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }

        @Override
        public void onError() {
            dismissProgress();
        }
    }

    private void updatePodUI(String status) {
        Pod doc = Aaho.getPodDetails();
        boolean canUpload = status.equals(STATUS_UNLOADED) && Aaho.isCanUploadPod();

        // update ui
        uploadPodBtn.setVisibility(canUpload ? View.VISIBLE : View.GONE);
        uploadPodText.setText(doc == null || doc.notSet() ? "Upload POD" : "Update POD");
    }

    private void setViewRefs() {
        btnStatus = (ImageButton) findViewById(R.id.vehicle_status_image);
        btnUnloaded = (ImageButton) findViewById(R.id.btn_unloaded);
        btnLoading = (ImageButton) findViewById(R.id.btn_loading);
        btnLoaded = (ImageButton) findViewById(R.id.btn_loaded);
        btnUnloading = (ImageButton) findViewById(R.id.btn_unloading);
        uploadPodBtn = (LinearLayout) findViewById(R.id.btn_upload_pod);
        uploadPodText = (TextView) findViewById(R.id.upload_pod_tv);
        txtVehicleStatus = (TextView) findViewById(R.id.vehicle_status);
        txtVehicleStatusDesc = (TextView) findViewById(R.id.vehicle_status_desc);
    }

    private void startTrackingService() {
        Intent intent = new Intent(this, TrackingService.class);
        intent.setAction(TrackingService.PERM_INTENT_ACTION);
        startService(intent);
    }

    private void stopTrackingService() {
        stopService(new Intent(this, TrackingService.class));
    }

    private void setDeviceIdAndStartService() {
        Aaho.setupDeviceId(this);
        startTrackingService();
    }

    private boolean hasPermission(String permission) {
        if (Build.VERSION.SDK_INT <= Build.VERSION_CODES.LOLLIPOP_MR1) {
            return true;
        }
        return checkSelfPermission(permission) == PackageManager.PERMISSION_GRANTED;
    }

    @Override
    public void onResume() {
        super.onResume();
        if (paused) {
            if (resolveMissingPermissions()) {
                resolveLocationSetting();
            }
        }
        paused = false;
    }

    @Override
    public void onPause() {
        super.onPause();
        paused = true;
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.main, menu);
        return super.onCreateOptionsMenu(menu);
    }

    @Override
    public boolean onPrepareOptionsMenu(Menu menu) {
        menu.findItem(R.id.menu_change_language).setTitle("\uD83C\uDF10 " + Lang.getLanguage().name);
        return super.onPrepareOptionsMenu(menu);
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
            case R.id.menu_edit_registration_details:
                launchRegistrationEdit();
                return true;
            case R.id.menu_call_us:
                dialAppSupportNumber();
                return true;
            case R.id.status:
                showStatusDialog();
                return true;
            case R.id.menu_change_language:
                showChangeLanguageDialog();
                return true;
            default:
                return super.onOptionsItemSelected(item);
        }
    }

    private void showChangeLanguageDialog() {
        LanguageSelectDialogFragment.showNewDialog(this, new LanguageSelectDialogFragment.OnChangeListener() {
            @Override
            public void onChange() {
                recreate();

            }
        });
    }

    private void launchRegistrationEdit() {
        if (Aaho.isRegistered()) {
            showRegisterDialog(true);
        } else {
            showRegisterDialog(false);
        }
    }

    private void dialAppSupportNumber() {
        launchDialer(Aaho.APP_SUPPORT_NUMBER);
    }


    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        if (requestCode == PERMISSIONS_REQUEST_LOCATION) {
            boolean granted = true;
            for (int result : grantResults) {
                if (result != PackageManager.PERMISSION_GRANTED) {
                    granted = false;
                    break;
                }
            }
            if (granted) {
                resolvingPerms = false;
                resolveLocationSetting();
                setDeviceIdAndStartService();
            } else {
                showPermAlertDialog();
            }
        }
    }

    private void showPermAlertDialog() {
        new AlertDialog.Builder(this)
                .setTitle("Permissions required")
                .setMessage("App will be unable to function until all the requested permissions are granted.")
                .setPositiveButton("ok", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        resolvingPerms = false;
                        resolveMissingPermissions();
                    }
                })
                .setNegativeButton("quit", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        resolvingPerms = false;
                        stopServicesAndQuitApp();
                    }
                })
                .setIcon(R.drawable.alert_icon)
                .show();
    }

    private boolean resolveMissingPermissions() {
        if (resolvingPerms) {
            return false;
        }
        Set<String> missingPermissions = new HashSet<>();
        for (String perm : permissions) {
            if (!hasPermission(perm)) {
                missingPermissions.add(perm);
            }
        }
        if (missingPermissions.isEmpty()) {
            return true;
        } else {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                resolvingPerms = true;
                requestPermissions(missingPermissions.toArray(new String[missingPermissions.size()]),
                        PERMISSIONS_REQUEST_LOCATION);
            }
            return false;
        }
    }

    public void showStatusDialog() {
        StatusDialog statusDialog = new StatusDialog();
        statusDialog.show(this.getSupportFragmentManager(), "status_dialog");
    }

    public void showRegisterDialog(boolean edit) {
        RegisterDialogFragment.showNewDialog(this, edit, new RegisterDialogFragment.OnCompleteListener() {
            @Override
            public void onComplete() {
                updateUI();
            }
        });
    }

    private void updateUI() {
        String status = Aaho.getVehicleStatus();
        setVehicleStatusUI(status);
        updatePodUI(status);
        setVerifiedUI();
    }

    private void setVerifiedUI() {

    }

    private void stopServicesAndQuitApp() {
        // no point in keeping services running if we do not hae the perms
        stopTrackingService();
        finish();
        System.exit(0);
    }

    // GPS settings related code

    private void resolveLocationSetting() {
        if (resolvingLocationSetting) {
            return;
        }
        FusedPositionProvider provider = FusedPositionProvider.getInstance();
        if (provider != null) {
            resolvingLocationSetting = true;
            provider.resolveLocationSetting();
        }
    }


    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        switch (requestCode) {
            // Check for the integer request code originally supplied to startResolutionForResult().
            case GPS_SETTINGS_REQUEST:
                switch (resultCode) {
                    case Activity.RESULT_OK:
                        resolvingLocationSetting = false;
                        break;
                    case Activity.RESULT_CANCELED:
                        showGPSSettingAlertDialog();  // keep asking
                        break;
                    default:
                        resolvingLocationSetting = false;
                        break;
                }
                break;
        }
    }


    private void showGPSSettingAlertDialog() {
        new AlertDialog.Builder(this)
                .setTitle(R.string.gps_request_title)
                .setMessage(R.string.gps_request_msg)
                .setPositiveButton(R.string.ok, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        resolvingLocationSetting = false;
                        resolveLocationSetting();
                    }
                })
                .setIcon(R.drawable.alert_icon)
                .show();
    }


    public static DriverActivity getInstance() {
        return instanceRef == null ? null : instanceRef.get();
    }


    public static String nextStatus(String status) {
        if (status.equals(STATUS_UNLOADED)) return STATUS_LOADING;
        if (status.equals(STATUS_LOADING)) return STATUS_LOADED;
        if (status.equals(STATUS_LOADED)) return STATUS_UNLOADING;
        if (status.equals(STATUS_UNLOADING)) return STATUS_UNLOADED;
        return STATUS_UNLOADED;
    }

    private void showRegisterAlert() {
        new AlertDialog.Builder(this)
                .setTitle("Registration required")
                .setMessage("Registration is required to change the status")
                .setPositiveButton(R.string.register, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        showRegisterDialog(false);
                    }
                })
                .setNegativeButton(R.string.later, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        // do nothing
                    }
                })
                .setIcon(R.drawable.alert_icon)
                .show();
    }

    private class StatusOnClickListener implements View.OnClickListener {
        private String newStatus = null;
        public StatusOnClickListener(String newStatus) {
            if (newStatus == null) throw new AssertionError("newStatus is null, this should not happen");
            this.newStatus = newStatus;
        }

        @Override
        public void onClick(View v) {
            if (!Aaho.isRegistered()) {
                showRegisterAlert();
                return;
            }
            String currStatus = Aaho.getVehicleStatus();
            if (!newStatus.equals(currStatus)) showStatusChangeConfirmDialog(newStatus);
        }
    }

    private class StatusCycleOnClickListener implements View.OnClickListener {

        @Override
        public void onClick(View v) {
            if (!Aaho.isRegistered()) {
                showRegisterAlert();
                return;
            }
            String currStatus = Aaho.getVehicleStatus();
            String nextStatus = nextStatus(currStatus);
            showStatusChangeConfirmDialog(nextStatus);
        }
    }

    private void showStatusChangeConfirmDialog(final String newStatus) {
        String msg = String.format(getString(R.string.action_status_change), newStatus);
        new AlertDialog.Builder(this)
                .setTitle(R.string.confirm_action)
                .setMessage(msg)
                .setPositiveButton(R.string.yes, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        changeStatusOfTruck(newStatus);
                    }
                })
                .setNegativeButton(R.string.no, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        // do nothing
                    }
                })
                .setIcon(R.drawable.alert_icon)
                .show();
    }

    private class TruckStatusResponseListener extends ApiResponseListener {

        private final String newStatus;

        public TruckStatusResponseListener(final String newStatus) {
            this.newStatus = newStatus;
        }

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            try {
                Log.e("response", response + "    from server");

                if (response.getString("status").equals(Api.STATUS_SUCCESS)) {
                    Log.e("SUCCESS", Api.STATUS_SUCCESS);
                    boolean canUploadPod = response.getBoolean("can_upload_pod");
                    JSONObject podDetails = Utils.getObject(response, "pod_details");
                    setVehicleStatus(newStatus, canUploadPod, podDetails);
                } else {
                    throw new AssertionError(response.toString());
                }
            } catch (Exception e) {
                e.printStackTrace();
            }

        }

        @Override
        public void onError() {
            dismissProgress();
        }
    }

    private void changeStatusOfTruck(final String newStatus){
        if (!Aaho.isRegistered()) return;
        // Response received from the server
        TruckStatusResponseListener responseListener = new TruckStatusResponseListener(newStatus);
        VehicleStatusRequest statusChangeRequest = new VehicleStatusRequest(jsonStatusData(newStatus), responseListener);
        queue(statusChangeRequest);
    }

    private JSONObject jsonStatusData(String status){
        JSONObject data = new JSONObject();
        try {
            data.put("vehicle_status", status);  // TODO: define in Api
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return data;
    }

    private void setVehicleStatus(String status, boolean canUploadPod, JSONObject podDetails) {
        Aaho.setVehicleStatus(status);
        setPodDetails(canUploadPod, podDetails);
        setVehicleStatusUI(status);
    }

    private void setPodDetails(boolean canUploadPod, JSONObject podDetails) {
        Aaho.setCanUploadPod(canUploadPod);
        Aaho.setPodDetails(podDetails);
        updatePodUI(Aaho.getVehicleStatus());
    }

    private void setVehicleStatusUI(String status) {
        btnStatus.setImageResource(vehicleStatusImage(status));
        txtVehicleStatus.setText(vehicleStatusString(status));
        txtVehicleStatusDesc.setText(vehicleStatusDesc(status));
        setStatusBtnUI(status);
    }


    private static int vehicleStatusImage(String status) {
        if (status.equals(STATUS_UNLOADED)) return R.drawable.unloaded;
        if (status.equals(STATUS_LOADING)) return R.drawable.loading;
        if (status.equals(STATUS_LOADED)) return R.drawable.loaded;
        if (status.equals(STATUS_UNLOADING)) return R.drawable.unloading;
        return R.drawable.unloaded;
    }

    private static int vehicleStatusString(String status) {
        if (status.equals(STATUS_UNLOADED)) return R.string.unloaded;
        if (status.equals(STATUS_LOADING)) return R.string.loading;
        if (status.equals(STATUS_LOADED)) return R.string.loaded;
        if (status.equals(STATUS_UNLOADING)) return R.string.unloading;
        return R.string.unloaded;
    }

    private static int vehicleStatusDesc(String status) {
        if (status.equals(STATUS_UNLOADED)) return R.string.unloaded_desc;
        if (status.equals(STATUS_LOADING)) return R.string.loading_desc;
        if (status.equals(STATUS_LOADED)) return R.string.loaded_desc;
        if (status.equals(STATUS_UNLOADING)) return R.string.unloading_desc;
        return R.string.unloaded_desc;
    }

    private ImageButton vehicleStatusBtn(String status) {
        if (status.equals(STATUS_UNLOADED)) return btnUnloaded;
        if (status.equals(STATUS_LOADING)) return btnLoading;
        if (status.equals(STATUS_LOADED)) return btnLoaded;
        if (status.equals(STATUS_UNLOADING)) return btnUnloading;
        return btnUnloaded;
    }

    private void setStatusBtnUI(String status) {
        modifyBtnUI(status, STATUS_LOADED);
        modifyBtnUI(status, STATUS_LOADING);
        modifyBtnUI(status, STATUS_UNLOADED);
        modifyBtnUI(status, STATUS_UNLOADING);
    }

    private void modifyBtnUI(String status, String statusOfBtn) {
        ImageButton btn = vehicleStatusBtn(statusOfBtn);
        if (status.equals(statusOfBtn)) {
            setStatusBtnEnabledUI(btn);
        } else {
            setStatusBtnDisabledUI(btn);
        }
    }

    private void setStatusBtnEnabledUI(ImageButton btn) {
        btn.setAlpha(BTN_ENABLED_ALPHA);
        btn.setBackgroundResource(R.color.truck_btn_enabled);
    }

    private void setStatusBtnDisabledUI(ImageButton btn) {
        btn.setAlpha(BTN_DISABLED_ALPHA);
        btn.setBackgroundResource(R.color.truck_btn_disabled);
    }

}
