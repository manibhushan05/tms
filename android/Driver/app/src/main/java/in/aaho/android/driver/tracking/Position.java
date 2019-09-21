package in.aaho.android.driver.tracking;

import android.location.Location;
import android.os.Build;

import org.json.JSONArray;
import org.json.JSONException;

import java.util.Date;

import in.aaho.android.driver.Aaho;
import in.aaho.android.driver.BuildConfig;

public class Position {


    private long id;

    private String deviceId;
    private String provider;
    private Date time;
    private double latitude;
    private double longitude;
    private double altitude;
    private double speed;
    private double course;
    private double accuracy;

    private double battery;
    private long totalMemory;
    private long availMemory;
    private long threshold;
    private int lowMemory;

    public Position() {
    }

    public Position(Location location, double batteryLevel, MemInfo info) {
        this.deviceId = Aaho.getDeviceId();
        time = new Date(location.getTime());
        latitude = location.getLatitude();
        longitude = location.getLongitude();
        altitude = location.getAltitude();
        speed = location.getSpeed();
        course = location.getBearing();
        accuracy = location.getAccuracy();
        provider = location.getProvider();
        battery = batteryLevel;
        totalMemory = info.getTotalMemory();
        availMemory = info.getAvailMemory();
        threshold = info.getThreshold();
        lowMemory = info.getLowMemory();
    }

    public String getRequestData() {
        return toJson().toString();
    }

    private JSONArray toJson() {

        // device details (static details, no need to store in sqlite db)
        String brand = Build.BRAND;
        String manufacturer = Build.MANUFACTURER;
        String device = Build.DEVICE;
        String product = Build.PRODUCT;
        String model = Build.MODEL;
        String versionName = BuildConfig.VERSION_NAME;
        int versionCode = BuildConfig.VERSION_CODE;
        String androidRelease = Build.VERSION.RELEASE;
        int androidSdkInt = Build.VERSION.SDK_INT;

        // order important, do not mess with the order
        // to keep the request small, we use an array instead of object
        JSONArray pos = new JSONArray();

        pos.put(deviceId);
        pos.put(time.getTime());
        pos.put(provider);
        try { pos.put(accuracy); } catch (JSONException e) { pos.put(0); }
        try { pos.put(latitude); } catch (JSONException e) { pos.put(0); }
        try { pos.put(longitude); } catch (JSONException e) { pos.put(0); }
        try { pos.put(altitude); } catch (JSONException e) { pos.put(0); }
        try { pos.put(speed); } catch (JSONException e) { pos.put(0); }
        try { pos.put(course); } catch (JSONException e) { pos.put(0); }
        try { pos.put(battery); } catch (JSONException e) { pos.put(0); }
        pos.put(totalMemory);
        pos.put(availMemory);
        pos.put(threshold);
        pos.put(lowMemory);
        pos.put(brand);
        pos.put(manufacturer);
        pos.put(device);
        pos.put(product);
        pos.put(model);
        pos.put(versionName);
        pos.put(versionCode);
        pos.put(androidRelease);
        pos.put(androidSdkInt);

        return pos;
    }

    public long getId() {
        return id;
    }

    public void setId(long id) {
        this.id = id;
    }

    public String getDeviceId() {
        return deviceId;
    }

    public void setDeviceId(String deviceId) {
        this.deviceId = deviceId;
    }

    public Date getTime() {
        return time;
    }

    public void setTime(Date time) {
        this.time = time;
    }

    public double getLatitude() {
        return latitude;
    }

    public void setLatitude(double latitude) {
        this.latitude = latitude;
    }

    public double getLongitude() {
        return longitude;
    }

    public void setLongitude(double longitude) {
        this.longitude = longitude;
    }

    public double getAltitude() {
        return altitude;
    }

    public void setAltitude(double altitude) {
        this.altitude = altitude;
    }

    public double getSpeed() {
        return speed;
    }

    public void setSpeed(double speed) {
        this.speed = speed;
    }

    public double getCourse() {
        return course;
    }

    public void setCourse(double course) {
        this.course = course;
    }

    public double getBattery() {
        return battery;
    }

    public void setBattery(double battery) {
        this.battery = battery;
    }

    public long getTotalMemory() {
        return totalMemory;
    }

    public void setTotalMemory(long totalMemory) {
        this.totalMemory = totalMemory;
    }

    public long getAvailMemory() {
        return availMemory;
    }

    public void setAvailMemory(long availMemory) {
        this.availMemory = availMemory;
    }

    public long getThreshold() {
        return threshold;
    }

    public void setThreshold(long threshold) {
        this.threshold = threshold;
    }


    public int getLowMemory() {
        return lowMemory;
    }

    public void setLowMemory(int lowMemory) {
        this.lowMemory = lowMemory;
    }

    public double getAccuracy() {
        return accuracy;
    }

    public void setAccuracy(double accuracy) {
        this.accuracy = accuracy;
    }

    public String getProvider() {
        return provider;
    }

    public void setProvider(String provider) {
        this.provider = provider;
    }
}
