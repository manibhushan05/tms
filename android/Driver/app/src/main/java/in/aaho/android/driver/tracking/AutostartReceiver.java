
package in.aaho.android.driver.tracking;

import android.content.Context;
import android.content.Intent;
import android.support.v4.content.WakefulBroadcastReceiver;


public class AutostartReceiver extends WakefulBroadcastReceiver {
    
    @Override
    public void onReceive(Context context, Intent intent) {
        Intent serviceIntent = new Intent(context, TrackingService.class);
        String action =  intent.getAction();
        if (action != null) {
            serviceIntent.setAction(action);
        }
        startWakefulService(context, serviceIntent);
    }

}
