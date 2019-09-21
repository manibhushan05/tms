package in.aaho.android.ownr.map;

import com.google.android.gms.maps.model.BitmapDescriptor;
import com.google.android.gms.maps.model.BitmapDescriptorFactory;

import in.aaho.android.ownr.R;

/**
 * Created by mani on 7/12/16.
 */

public class MapMarkers {
    private static BitmapDescriptor smallMarker = null;
    private static BitmapDescriptor largeMarker = null;
    private static BitmapDescriptor circleMarker = null;

    public static BitmapDescriptor getSmallMarker() {
        if (smallMarker == null) {
            smallMarker = BitmapDescriptorFactory.fromResource(R.drawable.ic_truck_black_18dp);
        }
        return smallMarker;
    }

    public static BitmapDescriptor getLargeMarker() {
        if (largeMarker == null) {
            largeMarker = BitmapDescriptorFactory.fromResource(R.drawable.ic_truck_black_24dp);
        }
        return largeMarker;
    }

    public static BitmapDescriptor getCircleMarker() {
        if (circleMarker == null) {
            circleMarker = BitmapDescriptorFactory.fromResource(R.drawable.dot_image);
        }
        return circleMarker;
    }


}
