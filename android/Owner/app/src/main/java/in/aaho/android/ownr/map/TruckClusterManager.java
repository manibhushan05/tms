package in.aaho.android.ownr.map;

import android.content.Context;

import com.google.android.gms.maps.GoogleMap;
import com.google.maps.android.clustering.ClusterManager;
import com.google.maps.android.clustering.view.ClusterRenderer;
import com.google.maps.android.clustering.view.DefaultClusterRenderer;

/**
 * Created by mani on 9/12/16.
 */

public class TruckClusterManager extends ClusterManager<TrackingData> {
    public TruckClusterManager(Context context, GoogleMap map) {
        super(context, map);
    }


}
