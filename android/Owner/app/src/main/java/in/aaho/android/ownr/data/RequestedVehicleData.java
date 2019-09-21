package in.aaho.android.ownr.data;

/**
 * Created by mani on 3/8/16.
 */
public class RequestedVehicleData {
    private String vehicleType;
    private String numberOfVehicle;

    public RequestedVehicleData(String vehicleType, String numberOfVehicle) {
        this.vehicleType = vehicleType;
        this.numberOfVehicle = numberOfVehicle;
    }

    public String getVehicleType() {
        return vehicleType;
    }

    public void setVehicleType(String vehicleType) {
        this.vehicleType = vehicleType;
    }

    public String getNumberOfVehicle() {
        return numberOfVehicle;
    }

    public void setNumberOfVehicle(String numberOfVehicle) {
        this.numberOfVehicle = numberOfVehicle;
    }
}
