package in.aaho.android.ownr.common;

import android.app.DownloadManager;
import android.content.Context;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Environment;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;

/**
 * This class is use to download the given file
 * Created by hp on 2/17/2018.
 */
public class FileDownloader extends AsyncTask<String, Void, Boolean> {
    private final String TAG = "FileDownloader";
    private Context mContext;
    private onDownloadTaskFinish onDownloadTaskFinish;
    //private Utilities mUtilities = new Utilities();

    public interface onDownloadTaskFinish {
        void onTaskSuccess(String strResult);

        void onTaskFailed(String strResult);
    }

    // constructor
    public FileDownloader(Context context, onDownloadTaskFinish IOnDownloadTaskFinish) {
        this.mContext = context;
        this.onDownloadTaskFinish = IOnDownloadTaskFinish;
    }

    @Override
    protected void onPreExecute() {
        super.onPreExecute();
        //mUtilities.showProgressDialog(mContext);
    }

    @Override
    protected Boolean doInBackground(String... strings) {
        String fileUrl = strings[0];   // -> http://maven.apache.org/maven-1.x/maven.pdf
        String fileName = strings[1];  // -> maven.pdf
        //String extStorageDirectory = Environment.getExternalStorageDirectory().toString();
        String extStorageDirectory = Environment.getExternalStorageDirectory().getAbsolutePath().toString();
        File folder = new File(extStorageDirectory, "AAHO");
        if (!folder.exists())
            folder.mkdir(); // If directory not exist, create a new one

        File file = new File(folder, fileName);

        try {
            file.createNewFile();
        } catch (IOException e) {
            e.printStackTrace();
        }

//        if(new DownloadFile().downloadFile(fileUrl, file))
//            return true;
//        else
//            return false;

        downloadFile(fileName, fileUrl, file);

        return true;
    }

    @Override
    protected void onPostExecute(Boolean bIsSuccess) {
        super.onPostExecute(bIsSuccess);
        //mUtilities.dismissProgressDialog();
        if (bIsSuccess) {
            // File download success
            onDownloadTaskFinish.onTaskSuccess("File download success");
        } else {
            // File download Failed
            onDownloadTaskFinish.onTaskFailed("File download Failed");
        }
    }

    private class DownloadFile {
        final int MEGABYTE = 1024 * 1024;

        public boolean downloadFile(String fileUrl, File directory) {
            boolean bIsDownlaodSuccess = false;
            try {

                URL url = new URL(fileUrl);
                HttpURLConnection urlConnection = (HttpURLConnection) url.openConnection();
                //urlConnection.setRequestMethod("GET");
                //urlConnection.setDoOutput(true);
                urlConnection.connect();

                InputStream inputStream = urlConnection.getInputStream();
                FileOutputStream fileOutputStream = new FileOutputStream(directory);
                int totalSize = urlConnection.getContentLength();

                byte[] buffer = new byte[MEGABYTE];
                int bufferLength = 0;
                while ((bufferLength = inputStream.read(buffer)) > 0) {
                    fileOutputStream.write(buffer, 0, bufferLength);
                }
                fileOutputStream.close();

                bIsDownlaodSuccess = true;
            } catch (FileNotFoundException e) {
                e.printStackTrace();
            } catch (MalformedURLException e) {
                e.printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            }
            return bIsDownlaodSuccess;
        }
    }

    /**
     * download the file using default android downloader
     *
     * @param fileName
     * @param fileUrl
     * @param directory
     */
    private void downloadFile(String fileName, String fileUrl, File directory) {
        DownloadManager.Request request = new DownloadManager.Request(Uri.parse(fileUrl));
        //request.setDescription("Some descrition");
        request.setTitle(fileName);
        // in order for this if to run, you must use the android 3.2 to compile your app
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.HONEYCOMB) {
            request.allowScanningByMediaScanner();
            request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
        }
        request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, fileName);

        // get download service and enqueue file
        DownloadManager manager = (DownloadManager) mContext.getSystemService(Context.DOWNLOAD_SERVICE);
        manager.enqueue(request);
    }
}
