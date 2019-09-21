package in.aaho.android.driver.common;

import android.annotation.TargetApi;
import android.app.Activity;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Matrix;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.os.StatFs;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.UUID;

/**
 * Created by shobhit on 31/10/16.
 */

public class StorageUtil {
    private static final SimpleDateFormat IMAGE_DATE_FORMAT = new SimpleDateFormat("yyyyMMdd_HHmmss");

    private static final String DOCUMENTS_DIR_NAME = "AahoDocuments";

    public static final String THUMBNAIL_PREFIX = "thumbnail-";

    public static final double BYTES_IN_MB = 1024.0 * 1024.0;

    private static final int MAX_IMAGE_SIZE = 2048;
    private static final int MAX_THUMB_SIZE = 512;

    public static final int IMAGE_QUALITY = 80;

    private static final double LOW_EXTERNAL_SPACE_MB = 50.0;

    // do not delete files stored on internal storage, if this much free space is available
    private static final double ENOUGH_INTERNAL_SPACE_MB = 500.0;

    // prefer external storage, if this much free space is available
    private static final double ENOUGH_EXTERNAL_SPACE_MB = 100.0;

    private static File getPersonalDirIfPossible(File dataDir) {
        File storageDir = new File(dataDir, DOCUMENTS_DIR_NAME);
        if (!storageDir.exists()) {
            boolean created = storageDir.mkdirs();
            if (!created) {
                storageDir = dataDir;
            }
        }
        return storageDir;
    }

    private static StorageDir getStorageDirectory() {
        File externalStorageDir = null;
        double externalFreeSpace = 0;

        if (hasWritableExternalStorage()) {
            File externalPictureDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES);
            externalFreeSpace = getFreeSpaceMb(externalPictureDir);
            externalStorageDir = getPersonalDirIfPossible(externalPictureDir);
        }

        // if external storage exists and has enough space, prefer external storage
        if (externalStorageDir != null && externalFreeSpace > ENOUGH_EXTERNAL_SPACE_MB) {
            return new StorageDir(true, externalStorageDir, externalFreeSpace);
        }

        File appStorageDir = Environment.getDataDirectory();
        double internalFreeSpace = getFreeSpaceMb(appStorageDir);
        File internalStorageDir = getPersonalDirIfPossible(appStorageDir);

        // if external storage exists and has more space than internal memory, prefer external storage
        if (externalStorageDir != null && externalFreeSpace > internalFreeSpace) {
            return new StorageDir(true, externalStorageDir, externalFreeSpace);
        } else {
            // either external storage is not available or has less space than internal storage
            return new StorageDir(false, internalStorageDir, internalFreeSpace);
        }
    }

    private static class StorageDir {
        private boolean onExternalStorage;
        private File directory;
        private double freeMemory;

        public StorageDir(boolean onExternalStorage, File directory, double freeMemory) {
            this.onExternalStorage = onExternalStorage;
            this.directory = directory;
            this.freeMemory = freeMemory;
        }

        public boolean shouldDelete() {
            return onExternalStorage ? freeMemory < LOW_EXTERNAL_SPACE_MB : freeMemory < ENOUGH_INTERNAL_SPACE_MB;
        }
    }

    public static class DeviceFile {
        private File file;
        private StorageDir dir;

        public DeviceFile(File file, StorageDir dir) {
            if (file == null || dir == null) {
                throw new NullPointerException("file or dir null");
            }
            this.dir = dir;
            this.file = file;
        }

        public File getFile() {
            return file;
        }

        public String getFilePath() {
            return "file:" + file.getAbsolutePath();
        }

        public Uri getUri() {
            return Uri.fromFile(file);
        }

        public void deleteIfLowMemory() {
            if (dir.shouldDelete()) {
                file.delete();
            }
        }
    }

    private static double getFreeSpaceMb(File storageDir) {
        StatFs stat = new StatFs(storageDir.getPath());
        long bytesAvailable;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.JELLY_BEAN_MR2) {
            bytesAvailable = getBytesAvailableApi18(stat);
        } else {
            bytesAvailable = getBytesAvailable(stat);
        }
        return bytesAvailable / BYTES_IN_MB;
    }

    @TargetApi(Build.VERSION_CODES.JELLY_BEAN_MR2)
    private static long getBytesAvailableApi18(StatFs stat) {
        return stat.getBlockSizeLong() * stat.getBlockCountLong();
    }

    @SuppressWarnings("deprecation")
    private static long getBytesAvailable(StatFs stat) {
        return (long) stat.getBlockSize() * (long) stat.getBlockCount();
    }

    private static boolean hasWritableExternalStorage() {
        String state = Environment.getExternalStorageState();
        return Environment.MEDIA_MOUNTED.equals(state);
    }

    public static DeviceFile createImageFile() throws IOException {
        String imageFileName = newImageFilename();
        StorageDir storageDir = getStorageDirectory();
        File image = new File(storageDir.directory, imageFileName);
        boolean created = image.createNewFile();
        if (!created) {
            throw new IOException("File already exists, path = " + image.getAbsolutePath());
        }
        return new DeviceFile(image, storageDir);
    }

    private static String newImageFilename() {
        return "aaho_document_" + IMAGE_DATE_FORMAT.format(new Date()) + ".jpg";
    }

    private static Bitmap getResizedBitmap(Bitmap bm, int newWidth, int newHeight) {
        Bitmap resizedBitmap = Bitmap.createScaledBitmap(bm, newWidth, newHeight, false);
        return resizedBitmap;
    }

    public static Bitmap scaleDownRawImage(Bitmap rawImage) {
        int origWidth = rawImage.getWidth();
        int origHeight = rawImage.getHeight();
        float scale = getScaleFactor(origWidth, origHeight, MAX_IMAGE_SIZE, MAX_IMAGE_SIZE);

        boolean shouldScale = scale < 1;
        boolean shouldRotate = origWidth > origHeight;

        if (!shouldScale && !shouldRotate) {
            return rawImage;
        }
        Matrix mtx = new Matrix();

        if (shouldScale) {
            mtx.setScale(scale, scale);
        }
        if (shouldRotate) {
            mtx.postRotate(90);
        }

        Bitmap result = Bitmap.createBitmap(rawImage, 0, 0, origWidth, origHeight, mtx, true);
        rawImage.recycle();
        rawImage = null;
        return result;
    }


    public static File[] saveToTempImages(Activity activity, Bitmap origBitmap) {
        String tempFilename = UUID.randomUUID().toString() + ".jpg";
        File outputFile = new File(activity.getFilesDir(), tempFilename);

        String thumbFilename = THUMBNAIL_PREFIX + tempFilename;
        File thumbOutputFile = new File(activity.getFilesDir(), thumbFilename);

        OutputStream outputStream;
        OutputStream thumbOutputStream;
        try {
            outputStream = new FileOutputStream(outputFile);
            thumbOutputStream = new FileOutputStream(thumbOutputFile);
        } catch (FileNotFoundException e) {
            e.printStackTrace();
            return null;
        }

        int origWidth = origBitmap.getWidth();
        int origHeight = origBitmap.getHeight();

        float scale = getScaleFactor(origWidth, origHeight, MAX_IMAGE_SIZE, MAX_IMAGE_SIZE);
        float thumbScale = getScaleFactor(origWidth, origHeight, MAX_THUMB_SIZE, MAX_THUMB_SIZE);

        int newWidth = Math.round(origWidth * scale);
        int newHeight = Math.round(origHeight * scale);

        int thumbWidth = Math.round(origWidth * thumbScale);
        int thumbHeight = Math.round(origHeight * thumbScale);

        Bitmap bitmap;
        Bitmap thumbBitmap;

        boolean recycleOriginal = true;

        if (scale >= 1) {
            // do not upscale
            bitmap = origBitmap;
            recycleOriginal = false;
        } else {
            bitmap = getResizedBitmap(origBitmap, newWidth, newHeight);
        }

        if (thumbScale >= 1) {
            thumbBitmap = origBitmap;
            recycleOriginal = false;
        } else {
            thumbBitmap = getResizedBitmap(bitmap, thumbWidth, thumbHeight);
        }

        if (recycleOriginal) {
            origBitmap.recycle();
            origBitmap = null;
        }

        // compress
        boolean success = bitmap.compress(Bitmap.CompressFormat.JPEG, IMAGE_QUALITY, outputStream);
        boolean thumbSuccess = thumbBitmap.compress(Bitmap.CompressFormat.JPEG, IMAGE_QUALITY, thumbOutputStream);

        try {
            outputStream.close();
            thumbOutputStream.close();
        } catch (IOException e) {
            e.printStackTrace();
        }

        // add to cache
        Cache cache = Cache.getInstance(activity);
        cache.putImage(tempFilename, bitmap);
        cache.putImage(thumbFilename, thumbBitmap);

        if (success && thumbSuccess) {
            return new File[] {outputFile, thumbOutputFile};
        } else {
            return null;
        }

    }

    public static File[] saveToTempImages(Activity activity, Uri uri) {
        InputStream inputStream;
        try {
            inputStream = activity.getContentResolver().openInputStream(uri);
        } catch (FileNotFoundException e) {
            e.printStackTrace();
            return null;
        }
        Bitmap origBitmap = BitmapFactory.decodeStream(inputStream);
        IoUtils.closeStream(inputStream);

        return saveToTempImages(activity, origBitmap);

    }

    private static float getScaleFactor(int width, int height, int maxWidth, int maxHeight) {
        float scaleWidth = ((float) maxWidth) / width;
        float scaleHeight = ((float) maxHeight) / height;

        return scaleWidth < scaleHeight ? scaleWidth : scaleHeight;
    }

}
