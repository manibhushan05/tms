package in.aaho.android.employee.push_notification;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.Context;
import android.graphics.Color;
import android.text.TextUtils;
import android.util.Log;

import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;

import java.util.Map;

import in.aaho.android.employee.common.MainApplication;

/**
 * Created by Suraj M
 */

public class MyFirebaseMessagingService extends FirebaseMessagingService {
    private final String TAG = getClass().getSimpleName();

    @Override
    public void onMessageReceived(RemoteMessage remoteMessage) {
        super.onMessageReceived(remoteMessage);
        // Commented sales check code, because its handled on back end side
        /*// show notification part only if employee role is sales
        if(Aaho.getRoles().contains("Sales")) {*/
            /*Log.e(TAG, "MessageId = " + remoteMessage.getMessageId());
            String title = remoteMessage.getNotification().getTitle();
            String msgBody = remoteMessage.getNotification().getBody();
            Log.e(TAG, "Message = " + msgBody);*/
            //LandingActivity.setRemoteMessage(remoteMessage);
            //Log.e(TAG, "Saved, RemoteMessage = " + remoteMessage);
            /*showNotification(title, msgBody);*/
            Map<String,String> remoteMsgData = remoteMessage.getData();
            showNotification(remoteMsgData.get("title"), remoteMsgData.get("body"));

            try {
                MainApplication.getBus().post(remoteMessage);
            } catch (Exception ex) {
                Log.e(TAG,"Unable to send bus event! ex="+ex.getLocalizedMessage());
            }

        /*} else {
            // Do not show notification this user role is not sales
        }*/
    }

    private void  showNotification(String title,String msg) {
        if(!TextUtils.isEmpty(msg)) {
            /* If the device is having android oreo we will create a notification channel **/
            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
                NotificationManager mNotificationManager =
                        (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
                int importance = NotificationManager.IMPORTANCE_HIGH;
                NotificationChannel mChannel = new NotificationChannel(NotificationConfig.CHANNEL_ID,
                        NotificationConfig.CHANNEL_NAME, importance);
                mChannel.setDescription(NotificationConfig.CHANNEL_DESCRIPTION);
                mChannel.enableLights(true);
                mChannel.setLightColor(Color.RED);
                mChannel.enableVibration(true);
                mChannel.setVibrationPattern(new long[]{100, 200, 300, 400, 500, 400, 300, 200, 400});
                mNotificationManager.createNotificationChannel(mChannel);
            }

            /** Displaying a notification locally */
            MyNotificationManager.getInstance(this).displayNotification(title, msg);
        }
    }
}
