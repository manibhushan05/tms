package in.aaho.android.driver.tracking;

import android.app.ActivityManager;
import android.content.Context;

/**
 * Created by shobhit on 15/9/16.
 */
public class MemInfo {
    private long totalMemory;
    private long availMemory;
    private long threshold;
    private int lowMemory;

    private MemInfo(long totalMemory, long availMemory, long threshold, boolean lowMemory) {
        this.totalMemory = totalMemory;
        this.availMemory = availMemory;
        this.threshold = threshold;
        this.lowMemory = lowMemory ? 1 : 0;
    }

    public long getTotalMemory() {
        return totalMemory;
    }

    public long getAvailMemory() {
        return availMemory;
    }

    public long getThreshold() {
        return threshold;
    }

    public static MemInfo get(Context context) {
        ActivityManager activityManager = (ActivityManager) context.getSystemService(Context.ACTIVITY_SERVICE);
        ActivityManager.MemoryInfo info = new ActivityManager.MemoryInfo();
        activityManager.getMemoryInfo(info);
        return new MemInfo(info.totalMem, info.availMem, info.threshold, info.lowMemory);
    }

    public int getLowMemory() {
        return lowMemory;
    }
}
