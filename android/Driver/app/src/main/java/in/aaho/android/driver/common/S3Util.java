package in.aaho.android.driver.common;

import com.amazonaws.mobileconnectors.s3.transferutility.TransferListener;
import com.amazonaws.mobileconnectors.s3.transferutility.TransferObserver;
import com.amazonaws.mobileconnectors.s3.transferutility.TransferState;
import com.amazonaws.mobileconnectors.s3.transferutility.TransferUtility;

import java.io.File;

/**
 * Created by shobhit on 1/11/16.
 */

public class S3Util {
    public static final String BUCKET_NAME = "fmsdocuments";

    private S3UploadListener listener;
    private String filename;
    private String thumbFilename;
    private File file;
    private File thumbFile;
    private TransferUtility transferUtility;

    public S3Util(File file, File thumbFile, S3UploadListener listener) {
        this.file = file;
        this.thumbFile = thumbFile;
        this.filename = file.getName();
        this.thumbFilename = thumbFile.getName();
        this.listener = listener;
        this.transferUtility = MainApplication.getTransferUtility();
    }

    public void start() {
        startThumbTransfer();
    }

    private void startThumbTransfer() {
        TransferObserver thumbTransferObserver = transferUtility.upload(BUCKET_NAME, thumbFilename, thumbFile);
        thumbTransferObserver.setTransferListener(new ThumbTransferListener());
    }

    private void startFileTransfer() {
        TransferObserver transferObserver = transferUtility.upload(BUCKET_NAME, filename, file);
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
                listener.onSuccess(filename, thumbFilename);
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
        return "https://" + BUCKET_NAME + ".s3.amazonaws.com/" + key;
    }

}
