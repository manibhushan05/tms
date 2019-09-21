package in.aaho.android.driver;

/**
 * Created by shobhit on 8/10/16.
 */

public class Intervals {
    // interval between location updates
    public static final int UPDATE_INTERVAL = 15 * 60 * 1000; // 15 minutes

    // minimum interval at which we should get location update if available
    public static final int FASTEST_INTERVAL = 10 * 60 * 1000; // 10 minutes

    // if we haven't had any updates for this much time, we should try to reconnect
    public static final int MAX_UPDATE_DELAY = 25 * 60 * 1000;  // 25 minutes

    // interval for alarm to repeatedly poke service with a new intent on android phones < M
    public static final int ALARM_INTERVAL = 10 * 60 * 1000; // 10 minutes

    // interval for doze alarm to repeatedly poke service with a new intent on android phones > M
    public static final int DOZE_ALARM_INTERVAL = 20 * 60 * 1000; // 20 minutes
}
