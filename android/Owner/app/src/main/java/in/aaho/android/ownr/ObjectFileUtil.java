package in.aaho.android.ownr;

import android.content.Context;
import android.util.Log;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;

/**
 * Created by suraj on 29/3/18.
 */

public class ObjectFileUtil<T> {
    private final File mFile;

    public ObjectFileUtil(Context context, String name) {
        mFile = new File(context.getFilesDir(), name);
    }

    public File getFile() {
        return mFile;
    }

    public void put(T o) {

        try {
            //delete if file exist
            if (mFile.exists()) {
                mFile.delete();
            }
            mFile.createNewFile();

            FileOutputStream fos = new FileOutputStream(mFile);

            ObjectOutputStream objOut = new ObjectOutputStream(fos);

            try {
                objOut.writeObject(o);
            } finally {
                objOut.close();
            }
        } catch (IOException e) {
            Log.e("ObjectFileUtil", "error saving cache file", e);
        }
    }

    public T get() {

        if (!mFile.exists()) {
            return null;
        }

        try {
            ObjectInputStream objIn = new ObjectInputStream(new FileInputStream(mFile));
            try {
                return (T) objIn.readObject();
            } finally {
                objIn.close();
            }
        } catch (IOException e) {
            Log.e("ObjectFileUtil", "error reading cache file", e);
        } catch (ClassNotFoundException e1) {
            Log.e("ObjectFileUtil", "cache file corrupted, deleting", e1);
            mFile.delete();
        }

        return null;
    }
}
