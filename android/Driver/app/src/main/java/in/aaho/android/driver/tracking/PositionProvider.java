package in.aaho.android.driver.tracking;

/**
 * Created by shobhit on 16/9/16.
 */
public interface PositionProvider {

    void startUpdates();

    void stopUpdates();

    interface PositionListener {
        void onPositionUpdate(Position position);
    }
}
