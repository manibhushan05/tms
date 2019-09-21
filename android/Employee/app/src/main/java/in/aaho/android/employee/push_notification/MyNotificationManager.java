package in.aaho.android.employee.push_notification;

import android.app.Notification;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Build;
import android.support.v4.app.NotificationCompat;
import android.support.v4.app.RemoteInput;
import android.util.Log;

import in.aaho.android.employee.LandingActivity;
import in.aaho.android.employee.R;
import in.aaho.android.employee.common.Utils;

import static android.content.Context.NOTIFICATION_SERVICE;

/**
 * Created by aaho on 09/05/18.
 */


public class MyNotificationManager {
    private final String TAG = getClass().getSimpleName();
    private Context mCtx;
    private static MyNotificationManager mInstance;
    public static final String REPLY_ACTION = "Reply";
    private static final String KEY_NOTIFICATION_ID = "KeyNotificationId";

    public static final String NOTIFICATION_REPLY = "NotificationReply";
    public static final String CHANNEL_ID = "ChannelId";

    public static final int REQUEST_CODE_REPLY = 100;
    public static final int NOTIFICATION_ID = 200;

    private MyNotificationManager(Context context) {
        mCtx = context;
    }

    public static synchronized MyNotificationManager getInstance(Context context) {
        if (mInstance == null) {
            mInstance = new MyNotificationManager(context);
        }
        return mInstance;
    }


    public void displayNotification(String title, String body) {
        PendingIntent pendingIntent = getPendingIntent();

        //We need this object for getting direct input from notification
        RemoteInput remoteInput = new RemoteInput.Builder(NOTIFICATION_REPLY)
                .setLabel("type here")
                .build();

        //For the remote input we need this action object
        NotificationCompat.Action action =
                new NotificationCompat.Action.Builder(android.R.drawable.ic_menu_send,
                        "Reply", pendingIntent)
                        .addRemoteInput(remoteInput)
                        .build();

        Bitmap logo = BitmapFactory.decodeResource(mCtx.getResources(),R.drawable.aaho_logo);
        //Creating the notification builder object
        NotificationCompat.Builder mBuilder = new NotificationCompat.Builder(mCtx, CHANNEL_ID)
                .setSmallIcon(R.drawable.aaho_logo)
                .setContentTitle(title)
                .setContentText(body)
                .setAutoCancel(true)
                .setDefaults(Notification.DEFAULT_ALL)


                // to add picture in notification uncomment below line
                /*.setStyle(new NotificationCompat.BigPictureStyle().bigPicture(logo))*/
                .setContentIntent(pendingIntent);

        if (android.os.Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            mBuilder.setPriority(Notification.PRIORITY_MAX);
        }
            // To add notification reply button uncomment below line
                /*.addAction(action)
                .addAction(android.R.drawable.ic_menu_compass, "More", morePendingIntent)
                .addAction(android.R.drawable.ic_menu_directions, "Help", helpPendingIntent);*/

        if (android.os.Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            mBuilder.setSmallIcon(R.drawable.aaho_logo);
            mBuilder.setColor(mCtx.getResources().getColor(R.color.colorAccent));
        } else {
            mBuilder.setSmallIcon(R.drawable.aaho_logo);
        }

        //finally displaying the notification
        NotificationManager notificationManager = (NotificationManager) mCtx.getSystemService(NOTIFICATION_SERVICE);
        Log.e(TAG,"Message to notify = "+mBuilder.build());
        notificationManager.notify(NOTIFICATION_ID, mBuilder.build());
    }

    public PendingIntent getPendingIntent() {
        Intent intent;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            // start a broadcast receiver which runs on the UI thread
            intent = new Intent(mCtx, NotificationReceiver.class);
            intent.setAction(REPLY_ACTION);
            //intent.putExtra(KEY_MESSAGE_ID, messageId);
            intent.putExtra(KEY_NOTIFICATION_ID, NOTIFICATION_ID);
            return PendingIntent.getBroadcast(mCtx, REQUEST_CODE_REPLY, intent,
                    PendingIntent.FLAG_UPDATE_CURRENT);
        } else {
            // start your activity for Android M and below
            intent = new Intent(mCtx, LandingActivity.class);
            intent.setAction(REPLY_ACTION);
            //intent.putExtra(KEY_MESSAGE_ID, messageId);
            intent.putExtra(KEY_NOTIFICATION_ID, NOTIFICATION_ID);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            return PendingIntent.getActivity(mCtx, REQUEST_CODE_REPLY, intent,
                    PendingIntent.FLAG_UPDATE_CURRENT);
        }
    }
}
