package in.aaho.android.employee.parser;

import android.util.Log;

import com.google.android.gms.location.places.Place;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.LatLngBounds;

import org.json.JSONException;
import org.json.JSONObject;

/**
 * Created by Suraj M
 */
public class GooglePlaceParser {
    private static final String TAG = "GooglePlaceParser";

    public static String getJsonByPlaces(Place place) {
        if (place == null)
            return null;

        JSONObject placesJson = new JSONObject();
        String id = place.getId();
        String name = String.valueOf(place.getName());
        String address = String.valueOf(place.getAddress());
        String websiteUri = String.valueOf(place.getWebsiteUri());

        LatLng coordinate = place.getLatLng();
        Double longitude = null, latitude = null;

        if (coordinate != null) {
            longitude = coordinate.longitude;
            latitude = coordinate.latitude;
        }

        try {

            JSONObject viewPortJson = new JSONObject();
            JSONObject southWestJson = new JSONObject();
            LatLngBounds latLngBoundsForViewPort = place.getViewport();
            // Retrieve southWest coordinate
            LatLng southwestLatLng = latLngBoundsForViewPort.southwest;
            if (southwestLatLng != null) {
                southWestJson.put("longitude", southwestLatLng.longitude);
                southWestJson.put("latitude", southwestLatLng.latitude);
            }
            // Retrieve northWest coordinate
            JSONObject northWestJson = new JSONObject();
            LatLng northwestLatLng = latLngBoundsForViewPort.northeast;
            if (northwestLatLng != null) {
                northWestJson.put("longitude", northwestLatLng.longitude);
                northWestJson.put("latitude", northwestLatLng.latitude);
            }

            placesJson.put("id", id);
            placesJson.put("name", name);
            placesJson.put("address", address);
            placesJson.put("websiteUri", websiteUri);
            placesJson.put("longitude", longitude);
            placesJson.put("latitude", latitude);

            // Add southWest & northWest in viewPort object
            viewPortJson.put("southWestCoordinate",southWestJson);
            viewPortJson.put("northWestCoordinate",northWestJson);
            // Add viewPort json to places object
            placesJson.put("viewPort",viewPortJson);

            Log.i(TAG,"GooglePlacesJson = "+placesJson.toString());
        } catch (JSONException e) {
            e.printStackTrace();
        }

        return placesJson.toString();
    }
}
