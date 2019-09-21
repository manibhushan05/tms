package in.aaho.android.aahocustomers.common;

import com.amazonaws.mobileconnectors.s3.transferutility.TransferListener;
import com.amazonaws.mobileconnectors.s3.transferutility.TransferObserver;
import com.amazonaws.mobileconnectors.s3.transferutility.TransferState;
import com.amazonaws.mobileconnectors.s3.transferutility.TransferUtility;

import java.io.File;
import java.util.UUID;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import in.aaho.android.aahocustomers.booking.App;
import in.aaho.android.aahocustomers.docs.DocumentEditFragment;
import in.aaho.android.aahocustomers.vehicles.VehicleDetailsActivity;

/**
 * Created by aaho on 14/06/18.
 */

public class S3Util {
    public static final String BUCKET_NAME = "fmsdocuments";

    private S3UploadListener listener;
    private String filename;
    private String thumbFilename;
    private File file;
    private File thumbFile;
    private TransferUtility transferUtility;

    private final String S3_UPLOADS_VEHICLE_RC_DIR = "uploads/vehicle/rc/";
    private final String S3_UPLOADS_VEHICLE_INSURANCE_DIR = "uploads/vehicle/insurance/";
    private final String S3_UPLOADS_VEHICLE_PERMIT_DIR = "uploads/vehicle/permit/";
    private final String S3_UPLOADS_FITNESS_DIR = "uploads/vehicle/fitness/";
    private final String S3_UPLOADS_VEHICLE_PUC_DIR = "uploads/vehicle/puc/";
    private final String S3_UPLOADS_SUPPLIER_PAN_DIR = "uploads/supplier/pan/";
    private final String S3_UPLOADS_SUPPLIER_DECLARATION_DIR = "uploads/supplier/declaration/";
    private final String S3_UPLOADS_SUPPLIER_BANK_DIR = "uploads/supplier/bank/";
    private final String S3_UPLOADS_DRIVER_LICENCE_DIR = "uploads/driver/driving_licence/";
    private final String S3_UPLOADS_DRIVER_PAN_DIR = "uploads/driver/pan/";
    private final String S3_UPLOADS_POD_DIR = "uploads/pod/";
    // This is default directory for upload, if none of above match
    private final String S3_DEFAULT_UPLOADS_DIR = "uploads/";


    // constants for upload directories
    public final static int S3_UPLOAD_ID_FOR_VEHICLE_RC_DIR = 1;
    public final static int S3_UPLOAD_ID_FOR_VEHICLE_INSURANCE_DIR = 2;
    public final static int S3_UPLOAD_ID_FOR_VEHICLE_PERMIT_DIR = 3;
    public final static int S3_UPLOAD_ID_FOR_VEHICLE_FITNESS_DIR = 4;
    public final static int S3_UPLOAD_ID_FOR_VEHICLE_PUC_DIR = 5;
    public final static int S3_UPLOAD_ID_FOR_SUPPLIER_PAN_DIR = 6;
    public final static int S3_UPLOAD_ID_FOR_SUPPLIER_DECLARATION_DIR = 7;
    public final static int S3_UPLOAD_ID_FOR_SUPPLIER_BANK_DIR = 8;
    public final static int S3_UPLOAD_ID_FOR_DRIVER_LICENCE_DIR = 9;
    public final static int S3_UPLOAD_ID_FOR_DRIVER_PAN_DIR = 10;
    public final static int S3_UPLOAD_ID_FOR_POD_DIR = 11;
    public final static int S3_UPLOAD_ID_FOR_PROFILE_SUPPLIER_PAN_DIR = 12;
    public final static int S3_UPLOAD_ID_FOR_PROFILE_SUPPLIER_DECLARATION_DIR = 13;

    /** current directory where we want to store the docs */
    private final String UPLOAD_DIR;

    /** Base url for upload */
    public final static String BASE_URL_UPLOAD = "https://" + BUCKET_NAME
            + ".s3.amazonaws.com/";

    /** Display user url only for user to see the url */
    public final static String BASE_DISPLAY_URL = "https://s3-ap-southeast-1.amazonaws.com/"
            + BUCKET_NAME + File.separator;


    public S3Util(File file, File thumbFile, S3UploadListener listener,int upload_id) {
        this.file = file;
        this.thumbFile = thumbFile;
        UPLOAD_DIR = getUploadDirByUploadId(upload_id);
        this.filename = getFileName(upload_id); //file.getName();
        this.thumbFilename = "thumbnail-"+filename;    //thumbFile.getName();
        this.listener = listener;
        this.transferUtility = MainApplication.getTransferUtility();
    }

    public void start() {
        startThumbTransfer();
    }

    private void startThumbTransfer() {
        TransferObserver thumbTransferObserver = transferUtility.upload(BUCKET_NAME,
                UPLOAD_DIR + thumbFilename, thumbFile);
        thumbTransferObserver.setTransferListener(new ThumbTransferListener());
    }

    private void startFileTransfer() {
        /*TransferObserver transferObserver = transferUtility.upload(BUCKET_NAME,
                "uploads/vehicle/permit/" + UUID.randomUUID() + "/" + filename, file);*/
        TransferObserver transferObserver = transferUtility.upload(BUCKET_NAME,
                UPLOAD_DIR + filename, file);
        transferObserver.setTransferListener(new DocTransferListener());
    }

    private class ThumbTransferListener implements TransferListener {

        @Override
        public void onStateChanged(int id, TransferState state) {
            if (state == TransferState.COMPLETED) {
                startFileTransfer();
            } else if (state == TransferState.CANCELED) {
                listener.onError("Error: Transfer Canceled");
            } else if (state == TransferState.FAILED) {
                listener.onError("Error: Transfer Failed, Try Again");
            }
        }

        @Override
        public void onProgressChanged(int id, long bytesCurrent, long bytesTotal) {
        }

        @Override
        public void onError(int id, Exception ex) {
            ex.printStackTrace();
            listener.onError("Error During Transfer: " + ex.toString());
        }

    }

    private class DocTransferListener implements TransferListener {

        @Override
        public void onStateChanged(int id, TransferState state) {
            if (state == TransferState.COMPLETED) {
                listener.onSuccess(UPLOAD_DIR+filename, UPLOAD_DIR+thumbFilename);
                deleteFiles();
            } else if (state == TransferState.CANCELED) {
                listener.onError("Error: Transfer Canceled");
                deleteFiles();
            } else if (state == TransferState.FAILED) {
                listener.onError("Error: Transfer Failed, Try Again");
                deleteFiles();
            }
        }

        @Override
        public void onProgressChanged(int id, long bytesCurrent, long bytesTotal) {
            if (bytesTotal != 0) {
                int progress = Math.round((bytesCurrent * 100) / bytesTotal);
                listener.onProgress(progress);
            }
        }

        @Override
        public void onError(int id, Exception ex) {
            ex.printStackTrace();
            listener.onError("Error During Transfer: " + ex.toString());
            deleteFiles();
        }

        private void deleteFiles() {
            if (file != null) {
                file.delete();
            }
            if (thumbFile != null) {
                thumbFile.delete();
            }
        }

    }

    public interface S3UploadListener {
        void onSuccess(String filename, String thumbFileName);

        void onError(String msg);

        void onProgress(int progress);
    }

    public static String url(String key) {
        //return "https://" + BUCKET_NAME + ".s3.amazonaws.com/" + key;
        // now base url will come directly in key, as we set it while uploading
        return key;
    }

    private String getUploadDirByUploadId(int upload_id) {
        String upload_dir = "";
        switch (upload_id) {
            case S3Util.S3_UPLOAD_ID_FOR_VEHICLE_RC_DIR:
                upload_dir = S3_UPLOADS_VEHICLE_RC_DIR + UUID.randomUUID() + File.separator;
                break;
            case S3Util.S3_UPLOAD_ID_FOR_VEHICLE_INSURANCE_DIR:
                upload_dir = S3_UPLOADS_VEHICLE_INSURANCE_DIR + UUID.randomUUID() + File.separator;
                break;
            case S3Util.S3_UPLOAD_ID_FOR_VEHICLE_PERMIT_DIR:
                upload_dir = S3_UPLOADS_VEHICLE_PERMIT_DIR + UUID.randomUUID() + File.separator;
                break;
            case S3Util.S3_UPLOAD_ID_FOR_VEHICLE_FITNESS_DIR:
                upload_dir = S3_UPLOADS_FITNESS_DIR+ UUID.randomUUID() + File.separator;
                break;
            case S3Util.S3_UPLOAD_ID_FOR_VEHICLE_PUC_DIR:
                upload_dir = S3_UPLOADS_VEHICLE_PUC_DIR + UUID.randomUUID() + File.separator;
                break;
            case S3Util.S3_UPLOAD_ID_FOR_SUPPLIER_PAN_DIR:
                upload_dir = S3_UPLOADS_SUPPLIER_PAN_DIR + UUID.randomUUID() + File.separator;
                break;
            case S3Util.S3_UPLOAD_ID_FOR_SUPPLIER_DECLARATION_DIR:
                upload_dir = S3_UPLOADS_SUPPLIER_DECLARATION_DIR + UUID.randomUUID() + File.separator;
                break;
            case S3Util.S3_UPLOAD_ID_FOR_SUPPLIER_BANK_DIR:
                upload_dir = S3_UPLOADS_SUPPLIER_BANK_DIR + UUID.randomUUID() + File.separator;
                break;
            case S3Util.S3_UPLOAD_ID_FOR_DRIVER_LICENCE_DIR:
                upload_dir = S3_UPLOADS_DRIVER_LICENCE_DIR + UUID.randomUUID() + File.separator;
                break;
            case S3Util.S3_UPLOAD_ID_FOR_DRIVER_PAN_DIR:
                upload_dir = S3_UPLOADS_DRIVER_PAN_DIR + UUID.randomUUID() + File.separator;
                break;
            case S3Util.S3_UPLOAD_ID_FOR_POD_DIR:
                upload_dir = S3_UPLOADS_POD_DIR + UUID.randomUUID() + File.separator;
                break;
            case S3Util.S3_UPLOAD_ID_FOR_PROFILE_SUPPLIER_PAN_DIR:
                upload_dir = S3_UPLOADS_SUPPLIER_PAN_DIR + UUID.randomUUID() + File.separator;
                break;
            case S3Util.S3_UPLOAD_ID_FOR_PROFILE_SUPPLIER_DECLARATION_DIR:
                upload_dir = S3_UPLOADS_SUPPLIER_DECLARATION_DIR + UUID.randomUUID() + File.separator;
                break;
            default:
                upload_dir = S3_DEFAULT_UPLOADS_DIR + UUID.randomUUID() + File.separator;
                break;
        }

        return upload_dir;
    }

    /** get the file name as vehicle number */
    private String getFileName(int upload_id) {
        String fileName = "";
        switch (upload_id) {
            case S3Util.S3_UPLOAD_ID_FOR_VEHICLE_RC_DIR:
                fileName = VehicleDetailsActivity.brokerVehicleDetails.getNumber();
                fileName = fileName.toLowerCase();
                fileName = fileName.replaceAll(Utils.REGEX_FOR_ALPHANEUMERIC, "");
                break;
            case S3Util.S3_UPLOAD_ID_FOR_VEHICLE_INSURANCE_DIR:
                fileName = VehicleDetailsActivity.brokerVehicleDetails.getNumber();
                fileName = fileName.toLowerCase();
                fileName = fileName.replaceAll(Utils.REGEX_FOR_ALPHANEUMERIC, "");
                break;
            case S3Util.S3_UPLOAD_ID_FOR_VEHICLE_PERMIT_DIR:
                fileName = VehicleDetailsActivity.brokerVehicleDetails.getNumber();
                fileName = fileName.toLowerCase();
                fileName = fileName.replaceAll(Utils.REGEX_FOR_ALPHANEUMERIC, "");
                break;
            case S3Util.S3_UPLOAD_ID_FOR_VEHICLE_FITNESS_DIR:
                fileName = VehicleDetailsActivity.brokerVehicleDetails.getNumber();
                fileName = fileName.toLowerCase();
                fileName = fileName.replaceAll(Utils.REGEX_FOR_ALPHANEUMERIC, "");
                break;
            case S3Util.S3_UPLOAD_ID_FOR_VEHICLE_PUC_DIR:
                fileName = VehicleDetailsActivity.brokerVehicleDetails.getNumber();
                fileName = fileName.toLowerCase();
                fileName = fileName.replaceAll(Utils.REGEX_FOR_ALPHANEUMERIC, "");
                break;
            case S3Util.S3_UPLOAD_ID_FOR_SUPPLIER_PAN_DIR:
                fileName = VehicleDetailsActivity.brokerVehicleDetails.vehicleOwner.name;
                fileName = fileName.toLowerCase();
                fileName = fileName.replaceAll(Utils.REGEX_FOR_ALPHANEUMERIC, "");
                break;
            case S3Util.S3_UPLOAD_ID_FOR_SUPPLIER_DECLARATION_DIR:
                fileName = VehicleDetailsActivity.brokerVehicleDetails.vehicleOwner.name;
                fileName = fileName.toLowerCase();
                fileName = fileName.replaceAll(Utils.REGEX_FOR_ALPHANEUMERIC, "");
                break;
            case S3Util.S3_UPLOAD_ID_FOR_SUPPLIER_BANK_DIR:
                fileName = VehicleDetailsActivity.brokerVehicleDetails.getNumber();
                fileName = fileName.toLowerCase();
                fileName = fileName.replaceAll(Utils.REGEX_FOR_ALPHANEUMERIC, "");
                break;
            case S3Util.S3_UPLOAD_ID_FOR_DRIVER_LICENCE_DIR:
                fileName = VehicleDetailsActivity.brokerVehicleDetails.vehicleDriver.name;
                fileName = fileName.toLowerCase();
                fileName = fileName.replaceAll(Utils.REGEX_FOR_ALPHANEUMERIC, "");
                break;
            case S3Util.S3_UPLOAD_ID_FOR_DRIVER_PAN_DIR:
                fileName = VehicleDetailsActivity.brokerVehicleDetails.vehicleDriver.name;
                fileName = fileName.toLowerCase();
                fileName = fileName.replaceAll(Utils.REGEX_FOR_ALPHANEUMERIC, "");
                break;
            case S3Util.S3_UPLOAD_ID_FOR_POD_DIR:
                fileName = DocumentEditFragment.LRNumber;
                fileName = fileName.toLowerCase();
                fileName = fileName.replaceAll(Utils.REGEX_FOR_ALPHANEUMERIC, "");
                break;
            case S3Util.S3_UPLOAD_ID_FOR_PROFILE_SUPPLIER_PAN_DIR:
                fileName = Utils.def(App.getProfile().userContactName, "");
                fileName = fileName.toLowerCase();
                fileName = fileName.replaceAll(Utils.REGEX_FOR_ALPHANEUMERIC, "");
                break;
            case S3Util.S3_UPLOAD_ID_FOR_PROFILE_SUPPLIER_DECLARATION_DIR:
                fileName = Utils.def(App.getProfile().userContactName, "");
                fileName = fileName.toLowerCase();
                fileName = fileName.replaceAll(Utils.REGEX_FOR_ALPHANEUMERIC, "");
                break;
            default:
                if(VehicleDetailsActivity.brokerVehicleDetails != null) {
                    fileName = VehicleDetailsActivity.brokerVehicleDetails.getNumber();
                } else {
                    fileName = "default";
                }
                fileName = fileName.toLowerCase();
                fileName = fileName.replaceAll(Utils.REGEX_FOR_ALPHANEUMERIC, "");
                break;
        }
        /*String vehicleNumber = VehicleDetailsActivity.brokerVehicleDetails.getNumber();
        vehicleNumber = vehicleNumber.replaceAll("[^a-zA-Z0-9]", "");
        String fileName = vehicleNumber + ".jpg";*/

        return fileName + ".jpg";
    }


}
