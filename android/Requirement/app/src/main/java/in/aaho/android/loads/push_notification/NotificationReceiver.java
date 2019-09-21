package in.aaho.android.loads.push_notification;

import android.app.NotificationManager;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.support.v4.app.RemoteInput;
import android.widget.Toast;

import static android.content.Context.NOTIFICATION_SERVICE;
import static in.aaho.android.loads.push_notification.MyNotificationManager.NOTIFICATION_ID;

/**
 * Created by aaho on 09/05/18.
 */

public class NotificationReceiver extends BroadcastReceiver {

    @Override
    public void onReceive(Context context, Intent intent) {
        //getting the remote input bundle from intent
        /*Bundle remoteInput = RemoteInput.getResultsFromIntent(intent);

        //if there is some input
        if (remoteInput != null) {

            //getting the input value
            CharSequence name = remoteInput.getCharSequence(MyNotificationManager.NOTIFICATION_REPLY);

            Toast.makeText(context, "You typed = "+name, Toast.LENGTH_SHORT).show();
            updating the notification with the input value
            NotificationCompat.Builder mBuilder = new NotificationCompat.Builder(context, MyNotificationManager.CHANNEL_ID)
                    .setSmallIcon(R.drawable.aaho_logo)
                    .setContentTitle(name);
            NotificationManager notificationManager = (NotificationManager) context.
                    getSystemService(Context.NOTIFICATION_SERVICE);
            //notificationManager.notify(MyNotificationManager.NOTIFICATION_ID, mBuilder.build());
            notificationManager.cancel(MyNotificationManager.NOTIFICATION_ID);
        }*/

        /*//if help button is clicked
        if (intent.getIntExtra(MyNotificationManager.KEY_INTENT_HELP, -1) == MyNotificationManager.REQUEST_CODE_HELP) {
            Toast.makeText(context, "You Clicked Help", Toast.LENGTH_LONG).show();
        }

        //if more button is clicked
        if (intent.getIntExtra(MyNotificationManager.KEY_INTENT_MORE, -1) == MyNotificationManager.REQUEST_CODE_MORE) {
            Toast.makeText(context, "You Clicked More", Toast.LENGTH_LONG).show();
        }*/

        if (MyNotificationManager.REPLY_ACTION.equals(intent.getAction())) {
            // do whatever you want with the message. Send to the server or add to the db.
            // for this tutorial, we'll just show it in a toast;
            CharSequence message = getReplyMessage(intent);
            //int messageId = intent.getIntExtra(KEY_MESSAGE_ID, 0);

            // todo: for the time being we are displaying msg only
            Toast.makeText(context, "Message: " + message,
                    Toast.LENGTH_SHORT).show();

            NotificationManager notificationManager = (NotificationManager)
                    context.getSystemService(NOTIFICATION_SERVICE);
            notificationManager.cancel(NOTIFICATION_ID);
        }
    }

    private CharSequence getReplyMessage(Intent intent) {
        Bundle remoteInput = RemoteInput.getResultsFromIntent(intent);
        if (remoteInput != null) {
            return remoteInput.getCharSequence(MyNotificationManager.NOTIFICATION_REPLY);
        }
        return null;
    }
}

