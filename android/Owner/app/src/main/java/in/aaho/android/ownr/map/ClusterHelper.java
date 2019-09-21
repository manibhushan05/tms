package in.aaho.android.ownr.map;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.drawable.ClipDrawable;
import android.graphics.drawable.Drawable;
import android.util.Log;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.Toast;

import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.model.BitmapDescriptorFactory;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.LatLngBounds;
import com.google.android.gms.maps.model.MarkerOptions;
import com.google.maps.android.clustering.Cluster;
import com.google.maps.android.clustering.ClusterItem;
import com.google.maps.android.clustering.ClusterManager;
import com.google.maps.android.clustering.view.DefaultClusterRenderer;
import com.google.maps.android.ui.IconGenerator;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.common.BaseActivity;
import in.aaho.android.ownr.common.Utils;

/**
 * Demonstrates heavy customisation of the look of rendered clusters.
 */
public class ClusterHelper implements ClusterManager.OnClusterClickListener<TrackingData>, ClusterManager.OnClusterInfoWindowClickListener<TrackingData>, ClusterManager.OnClusterItemClickListener<TrackingData>, ClusterManager.OnClusterItemInfoWindowClickListener<TrackingData> {
    private final BaseActivity activity;
    private final Context context;
    private final GoogleMap map;
    private ClusterManager<TrackingData> mClusterManager;

    public ClusterHelper(BaseActivity activity, GoogleMap map) {
        this.activity = activity;
        this.context = activity.getApplicationContext();
        this.map = map;
    }

    /**
     * Draws profile photos inside markers (using IconGenerator).
     * When there are multiple people in the cluster, draw multiple photos (using MultiDrawable).
     */
    private class PersonRenderer extends DefaultClusterRenderer<TrackingData> {
        // private final IconGenerator mIconGenerator = new IconGenerator(context);
        private final IconGenerator mClusterIconGenerator = new IconGenerator(context);
        // private final ImageView mImageView;
        // private final ImageView mClusterImageView;
        // private final int mDimension;

        public PersonRenderer() {
            super(context, map, mClusterManager);

            //View multiProfile = activity.getLayoutInflater().inflate(R.layout.multi_profile, null);
            //mClusterIconGenerator.setContentView(multiProfile);
            //mClusterImageView = (ImageView) multiProfile.findViewById(R.id.image);

            // mImageView = new ImageView(context);
            // mDimension = (int) activity.getResources().getDimension(R.dimen.custom_profile_image);
            // mImageView.setLayoutParams(new ViewGroup.LayoutParams(mDimension, mDimension));
            // int padding = (int) activity.getResources().getDimension(R.dimen.custom_profile_padding);
            // mImageView.setPadding(padding, padding, padding, padding);
            // mIconGenerator.setContentView(mImageView);
        }

        @Override
        protected void onBeforeClusterItemRendered(TrackingData data, MarkerOptions markerOptions) {
            // Draw a single person.
            // Set the info window to show their name.
            data.getMarker(markerOptions);
        }

        @Override
        protected void onBeforeClusterRendered(Cluster<TrackingData> cluster, MarkerOptions markerOptions) {
            // Draw multiple people.
            // Note: this method runs on the UI thread. Don't spend too much time in here (like in this example).
            // List<Drawable> profilePhotos = new ArrayList<Drawable>(Math.min(4, cluster.getSize()));
            // int width = mDimension;
            // int height = mDimension;

            // for (TrackingData p : cluster.getItems()) {
                // Draw 4 at most.
            //     if (profilePhotos.size() == 4) break;
            //    Drawable drawable = activity.getResources().getDrawable(p.profilePhoto);
            //    drawable.setBounds(0, 0, width, height);
            //    profilePhotos.add(drawable);
            // }
            // MultiDrawable multiDrawable = new MultiDrawable(profilePhotos);
            // multiDrawable.setBounds(0, 0, width, height);

            // mClusterImageView.setImageDrawable(multiDrawable);
            Bitmap icon = mClusterIconGenerator.makeIcon(String.valueOf(cluster.getSize()));
            markerOptions.icon(BitmapDescriptorFactory.fromBitmap(icon));
        }

        @Override
        protected boolean shouldRenderAsCluster(Cluster cluster) {
            // Always render clusters.
            return cluster.getSize() > 1;
        }
    }

    @Override
    public boolean onClusterClick(Cluster<TrackingData> cluster) {
        // Show a toast with some info when the cluster is clicked.
        String firstName = cluster.getItems().iterator().next().getVehicleNumber();
        Utils.toast(cluster.getSize() + " (including " + firstName + ")");

        // Zoom in the cluster. Need to create LatLngBounds and including all the cluster items
        // inside of bounds, then animate to center of the bounds.

        // Create the builder to collect all essential cluster items for the bounds.
        LatLngBounds.Builder builder = LatLngBounds.builder();
        for (ClusterItem item : cluster.getItems()) {
            builder.include(item.getPosition());
        }
        // Get the LatLngBounds
        final LatLngBounds bounds = builder.build();

        // Animate camera to the bounds
        try {
            map.animateCamera(CameraUpdateFactory.newLatLngBounds(bounds, 100));
        } catch (Exception e) {
            e.printStackTrace();
        }

        return true;
    }

    @Override
    public void onClusterInfoWindowClick(Cluster<TrackingData> cluster) {
        // Does nothing, but you could go to a list of the users.
    }

    @Override
    public boolean onClusterItemClick(TrackingData item) {
        // Does nothing, but you could go into the user's profile page, for example.
        return false;
    }

    @Override
    public void onClusterItemInfoWindowClick(TrackingData item) {
        // Does nothing, but you could go into the user's profile page, for example.
    }

    protected void startDemo() {
        map.moveCamera(CameraUpdateFactory.newLatLngZoom(new LatLng(51.503186, -0.126446), 9.5f));

        mClusterManager = new ClusterManager<>(activity, map);
        mClusterManager.setRenderer(new PersonRenderer());
        map.setOnCameraIdleListener(mClusterManager);
        map.setOnMarkerClickListener(mClusterManager);
        map.setOnInfoWindowClickListener(mClusterManager);
        mClusterManager.setOnClusterClickListener(this);
        mClusterManager.setOnClusterInfoWindowClickListener(this);
        mClusterManager.setOnClusterItemClickListener(this);
        mClusterManager.setOnClusterItemInfoWindowClickListener(this);

        addItems();
        mClusterManager.cluster();
    }

    private void addItems() {
        // http://www.flickr.com/photos/sdasmarchives/5036248203/
        // mClusterManager.addItem(new Person(position(), "Walter", R.drawable.walter));

    }

}