package in.aaho.android.ownr.data;

/**
 * Created by mani on 2/8/16.
 */
public class AllocatedVehicleData {
    private String typeOfVehicle;
    private String vehicleNumber;
    private String driverLicenceNumber;
    private String driverLicenceValidity;
    private String driverName;
    private String driverContactNumber;

    public AllocatedVehicleData() {
    }

    public AllocatedVehicleData(String typeOfVehicle, String vehicleNumber, String driverLicenceNumber, String driverLicenceValidity, String driverName, String driverContactNumber) {
        this.typeOfVehicle = typeOfVehicle;
        this.vehicleNumber = vehicleNumber;
        this.driverLicenceNumber = driverLicenceNumber;
        this.driverLicenceValidity = driverLicenceValidity;
        this.driverName = driverName;
        this.driverContactNumber = driverContactNumber;
    }

    public String getTypeOfVehicle() {
        return typeOfVehicle;
    }

    public void setTypeOfVehicle(String typeOfVehicle) {
        this.typeOfVehicle = typeOfVehicle;
    }

    public String getVehicleNumber() {
        return vehicleNumber;
    }

    public void setVehicleNumber(String vehicleNumber) {
        this.vehicleNumber = vehicleNumber;
    }

    public String getDriverLicenceNumber() {
        return driverLicenceNumber;
    }

    public void setDriverLicenceNumber(String driverLicenceNumber) {
        this.driverLicenceNumber = driverLicenceNumber;
    }

    public String getDriverName() {
        return driverName;
    }

    public void setDriverName(String driverName) {
        this.driverName = driverName;
    }

    public String getDriverContactNumber() {
        return driverContactNumber;
    }

    public void setDriverContactNumber(String driverContactNumber) {
        this.driverContactNumber = driverContactNumber;
    }

    public String getDriverLicenceValidity() {
        return driverLicenceValidity;
    }

    public void setDriverLicenceValidity(String driverLicenceValidity) {
        this.driverLicenceValidity = driverLicenceValidity;
    }
}
