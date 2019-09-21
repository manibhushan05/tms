package in.aaho.android.driver;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.Build;
import android.telephony.TelephonyManager;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.UUID;

import in.aaho.android.driver.common.Prefs;
import in.aaho.android.driver.common.Utils;
import in.aaho.android.driver.docs.Pod;

/**
 * Created by shobhit on 30/6/16.
 *
 * Project helper sort of thingy
 *
 */

public class Aaho {
    // helper class for global/common variables, constants and functons
    private static String authToken = null;
    private static String deviceId = null;
    private static String vehicleStatus = null;

    // keys for shared preferences
    private static final String DEVICE_ID_KEY = "id";
    private static final String AUTH_TOKEN_KEY = "auth_token";
    private static final String VEHICLE_NUMBER_KEY = "vehicle_number";
    private static final String VEHICLE_TYPE_KEY = "vehicle_type";
    private static final String VEHICLE_STATUS_KEY = "vehicle_status";
    private static final String DRIVER_NAME_KEY = "driver_name";
    private static final String MOBILE_NUMBER_KEY = "mobile_number";
    private static final String NUMBER_VERIFIED_KEY = "number_verified";
    private static final String CAN_UPLOAD_POD_KEY = "can_upload_pod";

    // App constants
    public static final String APP_SUPPORT_NUMBER = "+919969607841";
    private static Pod podDetails = null;


    public static void updateFromResponse(JSONObject response) throws JSONException {
        boolean canUploadPod = response.getBoolean("can_upload_pod");
        JSONObject podDetails = Utils.getObject(response, "pod_details");
        String newStatus = Utils.get(response, "vehicle_status");

        setVehicleStatus(newStatus);
        setCanUploadPod(canUploadPod);
        setPodDetails(podDetails);

        boolean numberVerified = response.getBoolean("number_verified");
        String vehicleNumber = Utils.get(response, "vehicle_number");
        String vehicleType = Utils.get(response, "vehicle_type");
        String driverName = Utils.get(response, "driver_name");
        String mobileNumber = Utils.get(response, "driver_number");

        saveDriverDetails(vehicleNumber, vehicleType, driverName, mobileNumber, numberVerified);
    }


    public static String getVehicleStatus() {
        if (vehicleStatus == null) {
            vehicleStatus = Prefs.get(VEHICLE_STATUS_KEY);
            if (vehicleStatus == null) {
                vehicleStatus = DriverActivity.STATUS_UNLOADED;
                Prefs.set(VEHICLE_STATUS_KEY, vehicleStatus);
            }
        }
        return vehicleStatus;
    }

    public static void setVehicleStatus(String status) {
        if (!vehicleStatus.equals(status)) {
            vehicleStatus = status;
            Prefs.set(VEHICLE_STATUS_KEY, vehicleStatus);
        }
    }

    public static void saveDriverDetails(String vehicleNumber, String vehicleType,
                                         String driverName, String mobileNumber, boolean numberVerified) {
        SharedPreferences.Editor editor = Prefs.editor();
        if (editor == null) {
            return;
        }
        editor.putString(VEHICLE_NUMBER_KEY, vehicleNumber);
        editor.putString(VEHICLE_TYPE_KEY, vehicleType);
        editor.putString(DRIVER_NAME_KEY, driverName);
        editor.putString(MOBILE_NUMBER_KEY, mobileNumber);
        editor.putBoolean(NUMBER_VERIFIED_KEY, numberVerified);
        editor.apply();
    }

    public static String getVehicleNumber() {
        return Prefs.get(VEHICLE_NUMBER_KEY);
    }

    public static String getVehicleType() {
        return Prefs.get(VEHICLE_TYPE_KEY);
    }

    public static String getDriverName() {
        return Prefs.get(DRIVER_NAME_KEY);
    }

    public static String getMobileNumber() {
        return Prefs.get(MOBILE_NUMBER_KEY);
    }

    public static boolean getNumberVerified() {
        return Prefs.get(NUMBER_VERIFIED_KEY, false);
    }

    public static boolean isCanUploadPod() {
        return Prefs.get(CAN_UPLOAD_POD_KEY, false);
    }

    public static boolean isRegistered() {
        return getAuthToken() != null;
    }

    public static String getAuthToken() {
        if (authToken == null) {
            authToken = Prefs.get(AUTH_TOKEN_KEY);
        }
        return authToken;
    }

    public static void setAuthToken(String token) {
        authToken = token;
        Prefs.set(AUTH_TOKEN_KEY, authToken);
    }

    public static String getDeviceId() {
        if (deviceId == null) {
            deviceId = Prefs.get(DEVICE_ID_KEY);
        }
        return deviceId;
    }

    public static void setupDeviceId(Context context) {
        if (deviceId == null) {
            deviceId = Prefs.get(DEVICE_ID_KEY);
            if (deviceId == null) {
                deviceId = imeiOrUUID(context);
                Prefs.set(DEVICE_ID_KEY, deviceId);
            }
        }
    }

    private static String imeiOrUUID(Context context) {
        String deviceId = getImei(context);
        if (deviceId == null || deviceId.trim().isEmpty()) {
            // we have perms but still no imei, our hands are tied, we need a unique id somehow
            deviceId = UUID.randomUUID().toString();
        }
        return deviceId;
    }

    private static String getImei(Context context) {
        String imei = null;
        TelephonyManager manager = (TelephonyManager) context.getSystemService(Context.TELEPHONY_SERVICE);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            try {
                imei = manager.getDeviceId(0);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        if (imei != null && !imei.trim().isEmpty()) {
            return imei.trim();
        }
        try {
            imei = manager.getDeviceId();
        } catch (Exception e) {
            e.printStackTrace();
        }
        if (imei == null || imei.trim().isEmpty()) {
            return null;
        } else {
            return imei.trim();
        }
    }

    public static void setNumberVerified() {
        SharedPreferences.Editor editor = Prefs.editor();
        if (editor == null) {
            return;
        }
        editor.putBoolean(NUMBER_VERIFIED_KEY, true);
        editor.apply();
    }

    public static void setCanUploadPod(boolean canUploadPod) {
        SharedPreferences.Editor editor = Prefs.editor();
        if (editor == null) {
            return;
        }
        editor.putBoolean(CAN_UPLOAD_POD_KEY, canUploadPod);
        editor.apply();
    }


    public static void setPodDetails(JSONObject podDetails) {
        try {
            Aaho.podDetails = Pod.fromJson(podDetails);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    public static void setPodDetails(Pod podDetails) {
        Aaho.podDetails = podDetails;
    }

    public static Pod getPodDetails() {
        return podDetails;
    }
}
