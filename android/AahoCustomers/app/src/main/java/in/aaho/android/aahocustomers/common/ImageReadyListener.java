package in.aaho.android.aahocustomers.common;

import android.graphics.Bitmap;

/**
 * Created by mani on 3/11/16.
 */

public abstract class ImageReadyListener {
    private boolean canceled = false;
    public abstract void onReady(Bitmap bitmap);

    public void onBitmapReady(Bitmap bitmap) {
        if (!canceled) {
            onReady(bitmap);
        }
    }

    public void cancel() {
        canceled = true;
    }

    public boolean isCanceled() {
        return canceled;
    }
}
