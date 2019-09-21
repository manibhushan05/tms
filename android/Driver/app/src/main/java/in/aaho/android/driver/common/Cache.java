package in.aaho.android.driver.common;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.AsyncTask;
import android.os.Environment;
import android.support.v4.util.LruCache;
import android.util.Log;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

/**
 * Created by shobhit on 3/11/16.
 */

public class Cache {
    private DiskLruCache mDiskLruCache;
    private final Object mDiskCacheLock = new Object();
    private boolean mDiskCacheStarting = true;
    private static final int DISK_CACHE_SIZE = 1024 * 1024 * 10; // 10MB
    private static final String DISK_CACHE_SUBDIR = "imageCache";
    private static final int CACHE_VERSION = 1;
    private static final int CACHE_COUNT = 1;
    private static final int CACHE_INDEX = 0;

    private final ImageCache imageCache;
    private final ImageCache thumbCache;
    private final int maxMemory;
    private final int imageCacheSize;
    private final int thumbCacheSize;

    private static Cache instance = null;

    public static Cache getInstance(Context context) {
        if (instance == null) {
            instance = new Cache(context.getApplicationContext());
        }
        return instance;
    }

    public void putImage(String key, Bitmap bitmap) {
        if (bitmap != null) {
            putInMemoryCache(key, bitmap);
            new SyncToDiskCacheTask(key).execute(bitmap);
        }
    }

    public void getImage(String key, ImageReadyListener listener) {
        Bitmap bitmap = getFromMemoryCache(key);
        if (bitmap != null) {
            listener.onBitmapReady(bitmap);
            Log.e("[Cache.getImage]", "found in memory cache");
            return;
        }
        if (!listener.isCanceled()) {
            new GetFromDiskCacheTask(key, listener).execute();
        }
    }

    private Cache(Context context) {
        maxMemory = (int) (Runtime.getRuntime().maxMemory() / 1024);

        // Use 1/8th of the available memory for this memory cache.
        imageCacheSize = maxMemory / 8;
        thumbCacheSize = maxMemory / 8;

        imageCache = new ImageCache(imageCacheSize);
        thumbCache = new ImageCache(thumbCacheSize);

        File cacheDir = getDiskCacheDir(context, DISK_CACHE_SUBDIR);
        new InitDiskCacheTask().execute(cacheDir);
    }

    private ImageCache getCache(String key) {
        return key.startsWith(StorageUtil.THUMBNAIL_PREFIX) ? thumbCache : imageCache;
    }

    private void putInMemoryCache(String key, Bitmap bitmap) {
        getCache(key).put(key, bitmap);
    }

    private Bitmap getFromMemoryCache(String key) {
        return getCache(key).get(key);
    }

    private class ImageCache extends LruCache<String, Bitmap> {

        public ImageCache(int maxSize) {
            super(maxSize);
        }

        @Override
        protected int sizeOf(String key, Bitmap bitmap) {
            // The cache size will be measured in kilobytes rather than
            // number of items.
            return bitmap.getByteCount() / 1024;
        }
    }

    private void addToDiskCache(String key, Bitmap bitmap) {
        // Also add to disk cache
        synchronized (mDiskCacheLock) {
            if (mDiskLruCache != null) {
                DiskLruCache.Editor editor;
                try {
                    editor = mDiskLruCache.edit(key);
                    OutputStream outputStream = editor.newOutputStream(CACHE_INDEX);
                    bitmap.compress(Bitmap.CompressFormat.JPEG, StorageUtil.IMAGE_QUALITY, outputStream);
                    IoUtils.closeStream(outputStream);
                    editor.commit();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    private Bitmap getFromDiskCache(String key) {
        synchronized (mDiskCacheLock) {
            // Wait while disk cache is started from background thread
            while (mDiskCacheStarting) {
                try {
                    mDiskCacheLock.wait();
                } catch (InterruptedException e) {}
            }
            if (mDiskLruCache != null) {
                try {
                    DiskLruCache.Snapshot snapshot = mDiskLruCache.get(key);
                    if (snapshot == null) {
                        return null;
                    }
                    InputStream inputStream = snapshot.getInputStream(CACHE_INDEX);
                    if (inputStream == null) {
                        return null;
                    }
                    Bitmap bitmap = BitmapFactory.decodeStream(inputStream);
                    IoUtils.closeStream(inputStream);
                    return bitmap;
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
        return null;
    }

    private class InitDiskCacheTask extends AsyncTask<File, Void, Void> {
        @Override
        protected Void doInBackground(File... params) {
            synchronized (mDiskCacheLock) {
                File cacheDir = params[0];
                try {
                    mDiskLruCache = DiskLruCache.open(cacheDir, CACHE_VERSION, CACHE_COUNT, DISK_CACHE_SIZE);
                } catch (IOException e) {
                    e.printStackTrace();
                }
                mDiskCacheStarting = false; // Finished initialization
                mDiskCacheLock.notifyAll(); // Wake any waiting threads
            }
            return null;
        }
    }

    private class SyncToDiskCacheTask extends AsyncTask<Bitmap, Void, Void> {
        private final String key;

        public SyncToDiskCacheTask(String key) {
            this.key = key;
        }

        @Override
        protected Void doInBackground(Bitmap... params) {
            addToDiskCache(key, params[0]);
            return null;
        }
    }

    private class GetFromDiskCacheTask extends AsyncTask<Void, Void, Bitmap> {

        private final ImageReadyListener listener;
        private final String key;

        public GetFromDiskCacheTask(String key, ImageReadyListener listener) {
            this.listener = listener;
            this.key = key;
        }

        protected Bitmap doInBackground(Void... voids) {
            if (!listener.isCanceled()) {
                Bitmap bitmap = getFromDiskCache(key);
                return bitmap;
            }
            return null;
        }

        protected void onPostExecute(Bitmap result) {
            if (result == null) {
                if (listener.isCanceled()) {
                    return;
                }
                new DownloadImageTask(key, listener).execute();
            } else {
                listener.onBitmapReady(result);
                Log.e("[GetFromDiskCacheTask]", "found in disk cache");
                putInMemoryCache(key, result);
            }
        }
    }

    private class DownloadImageTask extends AsyncTask<Void, Void, Bitmap> {

        private final ImageReadyListener listener;
        private final String key;

        public DownloadImageTask(String key, ImageReadyListener listener) {
            this.listener = listener;
            this.key = key;
        }

        protected Bitmap doInBackground(Void... voids) {
            if (listener.isCanceled()) {
                return null;
            }
            String url = S3Util.url(key);
            Bitmap bitmap = null;
            try {
                InputStream in = new java.net.URL(url).openStream();
                bitmap = BitmapFactory.decodeStream(in);
            } catch (IOException e) {
                e.printStackTrace();
            }
            return bitmap;
        }

        protected void onPostExecute(Bitmap result) {
            listener.onBitmapReady(result);
            if (result != null) {
                Log.e("[DownloadImageTask]", "Image successfully downloaded");
                putInMemoryCache(key, result);
                new SyncToDiskCacheTask(key).execute(result);
            } else {
                Log.e("[DownloadImageTask]", "Error Fetching Bitmap");
            }
        }
    }

    // Creates a unique subdirectory of the designated app cache directory. Tries to use external
    // but if not mounted, falls back on internal storage.
    private static File getDiskCacheDir(Context context, String uniqueName) {
        // Check if media is mounted or storage is built-in, if so, try and use external cache dir
        // otherwise use internal cache dir
        final String cachePath =
                Environment.MEDIA_MOUNTED.equals(Environment.getExternalStorageState()) ||
                        !Environment.isExternalStorageRemovable() ? context.getExternalCacheDir().getPath() :
                        context.getCacheDir().getPath();

        return new File(cachePath + File.separator + uniqueName);
    }


}
