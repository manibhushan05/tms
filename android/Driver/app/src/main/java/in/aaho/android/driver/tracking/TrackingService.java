package in.aaho.android.driver.tracking;

import android.app.AlarmManager;
import android.app.Notification;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.os.IBinder;
import android.support.v4.app.NotificationCompat;
import android.util.Log;

import in.aaho.android.driver.DriverActivity;
import in.aaho.android.driver.Intervals;
import in.aaho.android.driver.R;

public class TrackingService extends Service {

    private static final String TAG = TrackingService.class.getSimpleName();

    private static boolean dozeAlarmSet = false;

    private static final int ALARM_REQUEST_CODE = 1100;
    private static final int DOZE_ALARM_REQUEST_CODE = 1101;

    public static final String DOZE_ALARM_INTENT_ACTION = "app_doze_alarm";
    public static final String ALARM_INTENT_ACTION = "app_alarm";
    public static final String PERM_INTENT_ACTION = "perms_granted";

    private static final int NOTIFICATION_ID = 1;

    private TrackingController trackingController;

    private AlarmManager alarmManager;
    private PendingIntent alarmIntent;
    private PendingIntent dozeAlarmIntent = null;

    @Override
    public void onCreate() {
        Log.i(TAG, "service create");
        StatusDialog.addMessage(getString(R.string.status_service_create));

        alarmManager = (AlarmManager) getSystemService(ALARM_SERVICE);
        alarmIntent = getAlarmIntent(this);
        dozeAlarmIntent = getDozeIntent(this);

        trackingController = new TrackingController(this);
        trackingController.start();

        startForeground(NOTIFICATION_ID, getForegroundNotification());
        setAlarm();
    }


    private static PendingIntent getAlarmIntent(Context context) {
        Intent intent = new Intent(context.getApplicationContext(), AutostartReceiver.class);
        intent.setAction(ALARM_INTENT_ACTION);
        return PendingIntent.getBroadcast(context.getApplicationContext(), ALARM_REQUEST_CODE,
                intent, PendingIntent.FLAG_UPDATE_CURRENT);

    }

    private static PendingIntent getDozeIntent(Context context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            Intent intent = new Intent(context.getApplicationContext(), AutostartReceiver.class);
            intent.setAction(DOZE_ALARM_INTENT_ACTION);
            return PendingIntent.getBroadcast(context.getApplicationContext(), DOZE_ALARM_REQUEST_CODE,
                    intent, PendingIntent.FLAG_UPDATE_CURRENT);
        } else {
            return null;
        }
    }

    private static boolean setDozeAlarm(AlarmManager alarmManager, PendingIntent dozeAlarmIntent) {
        if (TrackingService.dozeAlarmSet) {
            return false;
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M && dozeAlarmIntent != null && alarmManager != null) {
            alarmManager.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,
                    System.currentTimeMillis() + Intervals.DOZE_ALARM_INTERVAL, dozeAlarmIntent);
            StatusDialog.addMessage("Doze alarm set");
            TrackingService.dozeAlarmSet = true;
            return true;
        } else {
            return false;
        }
    }

    private static boolean cancelDozeAlarm(AlarmManager alarmManager, PendingIntent dozeAlarmIntent) {
        if (dozeAlarmIntent != null && alarmManager != null) {
            alarmManager.cancel(dozeAlarmIntent);
            dozeAlarmSet = false;
            return true;
        } else {
            return false;
        }
    }

    private void setAlarm() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            setDozeAlarm(alarmManager, dozeAlarmIntent);
        } else {
            alarmManager.setInexactRepeating(AlarmManager.ELAPSED_REALTIME_WAKEUP,
                    Intervals.ALARM_INTERVAL, Intervals.ALARM_INTERVAL, alarmIntent);
        }
    }

    private void cancelAlarm() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            cancelDozeAlarm(alarmManager, dozeAlarmIntent);
        } else {
            alarmManager.cancel(alarmIntent);
        }
    }

    private Notification getForegroundNotification() {
        NotificationCompat.Builder builder = new NotificationCompat.Builder(getApplicationContext());
        builder.setSmallIcon(R.drawable.location);  // icon id of the image
        builder.setContentTitle("Aaho Driver");
        builder.setContentText("Collecting location data");
        builder.setContentInfo("Aaho Driver");
        builder.setContentIntent(getNotificationIntent());
        builder.setPriority(Notification.PRIORITY_MAX);
        return builder.build();
    }

    private PendingIntent getNotificationIntent() {
        Intent foregroundIntent = new Intent(getApplicationContext(), DriverActivity.class);
        foregroundIntent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        return PendingIntent.getActivity(getApplicationContext(), 0, foregroundIntent, 0);
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null) {
            String action = intent.getAction();
            if (action == null) {
                // pass
            } else if (action.equals(DOZE_ALARM_INTENT_ACTION)) {
                StatusDialog.addMessage("Doze Alarm Fired! yay!");
                dozeAlarmSet = false;
                setDozeAlarm(alarmManager, dozeAlarmIntent);
                trackingController.ping();
            } else if (action.equals(ALARM_INTENT_ACTION)) {
                trackingController.ping();
            } else if (action.equals(PERM_INTENT_ACTION)) {
                trackingController.ping();
            } else {

            }
            AutostartReceiver.completeWakefulIntent(intent);
        }
        return START_STICKY;
    }

    @Override
    public void onDestroy() {
        Log.i(TAG, "service destroy");
        StatusDialog.addMessage(getString(R.string.status_service_destroy));
        cancelAlarm();
        stopForeground(true);
        if (trackingController != null) {
            trackingController.stop();
        }
    }

}
