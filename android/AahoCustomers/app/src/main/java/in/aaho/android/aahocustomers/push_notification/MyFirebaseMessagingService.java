package in.aaho.android.aahocustomers.push_notification;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.Context;
import android.graphics.Color;
import android.text.TextUtils;
import android.util.Log;

import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;

/**
 * Created by aaho on 09/05/18.
 */

public class MyFirebaseMessagingService extends FirebaseMessagingService {
    private final String TAG = getClass().getSimpleName();

    @Override
    public void onMessageReceived(RemoteMessage remoteMessage) {
        super.onMessageReceived(remoteMessage);
        Log.e(TAG,"MessageId = "+remoteMessage.getMessageId());
        String title = remoteMessage.getNotification().getTitle();
        String msgBody = remoteMessage.getNotification().getBody();
        Log.e(TAG,"Message = "+msgBody);
        showNotification(title,msgBody);
    }

    private void showNotification(String title,String msg) {
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
