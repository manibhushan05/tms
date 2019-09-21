package in.aaho.android.loads.push_notification;

import android.provider.Settings;
import android.util.Log;

import com.google.firebase.iid.FirebaseInstanceId;
import com.google.firebase.iid.FirebaseInstanceIdService;
import in.aaho.android.loads.Aaho;
/**
 * Created by aaho on 09/05/18.
 */


public class MyFirebaseInstanceIDService extends FirebaseInstanceIdService {
    private final String TAG = getClass().getSimpleName();

    @Override
    public void onTokenRefresh() {
        super.onTokenRefresh();
        String token = FirebaseInstanceId.getInstance().getToken();
        String androidId = Settings.Secure.getString(getContentResolver(),
                Settings.Secure.ANDROID_ID);
        String deviceId = androidId;
        // save in preferences also
        Aaho.setFcmToken(token);
        Aaho.setDeviceId(deviceId);
        Log.e(TAG,"Token = "+ token);
        Log.e(TAG,"DeviceId = "+ deviceId);
        //saveTokenIdOnServer(token,deviceId); // move to login call now
    }
}
