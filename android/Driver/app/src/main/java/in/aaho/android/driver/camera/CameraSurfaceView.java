package in.aaho.android.driver.camera;

/**
 * Created by shobhit on 26/11/16.
 */

import android.content.Context;
import android.hardware.Camera;
import android.util.Log;
import android.view.SurfaceHolder;
import android.view.SurfaceView;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/** A basic Camera preview class */
@SuppressWarnings("deprecation")
public class CameraSurfaceView extends SurfaceView implements SurfaceHolder.Callback {
    private List<Camera.Size> mSupportedPictureSizes;
    private List<Camera.Size> mSupportedPreviewSizes;
    private SurfaceHolder mHolder;
    private Camera mCamera;

    private static final String TAG = "[Preview]";
    private Camera.Size mPreviewSize;

    public CameraSurfaceView(Context context, Camera camera) {
        super(context);
        mCamera = camera;
        mSupportedPreviewSizes = mCamera.getParameters().getSupportedPreviewSizes();
        mSupportedPictureSizes = mCamera.getParameters().getSupportedPictureSizes();

        // Install a SurfaceHolder.Callback so we get notified when the
        // underlying surface is created and destroyed.
        mHolder = getHolder();
        mHolder.addCallback(this);
        // deprecated setting, but required on Android versions prior to 3.0
        mHolder.setType(SurfaceHolder.SURFACE_TYPE_PUSH_BUFFERS);
    }

    public void surfaceCreated(SurfaceHolder holder) {
        // The Surface has been created, now tell the camera where to draw the preview.
        try {
            mCamera.setPreviewDisplay(holder);
            mCamera.startPreview();
        } catch (IOException e) {
            Log.d(TAG, "Error setting camera preview: " + e.getMessage());
        }
    }

    public void surfaceDestroyed(SurfaceHolder holder) {
        // empty. Take care of releasing the Camera preview in your activity.
    }

    public void surfaceChanged(SurfaceHolder holder, int format, int w, int h) {
        // If your preview can change or rotate, take care of those events here.
        // Make sure to stop the preview before resizing or reformatting it.

        if (mHolder.getSurface() == null){
            // preview surface does not exist
            return;
        }

        // stop preview before making changes
        try {
            mCamera.stopPreview();
        } catch (Exception e){
            // ignore: tried to stop a non-existent preview
        }

        // set preview size and make any resize, rotate or
        // reformatting changes here

        // start preview with new settings
        try {
            mCamera.setPreviewDisplay(mHolder);
            mCamera.setDisplayOrientation(90);

            if (mPreviewSize != null) {
                Camera.Parameters parameters = mCamera.getParameters();
                parameters.setPreviewSize(mPreviewSize.width, mPreviewSize.height);
                mCamera.setParameters(parameters);
            }

            mCamera.startPreview();

        } catch (Exception e){
            Log.d(TAG, "Error starting camera preview: " + e.getMessage());
        }
    }

    @Override
    protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
        int width = resolveSize(getSuggestedMinimumWidth(), widthMeasureSpec);
        int height = resolveSize(getSuggestedMinimumHeight(), heightMeasureSpec);

        Camera.Size maxPicSize = getMaxPicSize();
        double targetRatio;
        if (maxPicSize == null) {
            targetRatio = (double)width / height;
        } else {
            targetRatio = (double)maxPicSize.width / maxPicSize.height;
            height = (int) Math.round(width * targetRatio);
        }
        setMeasuredDimension(width, height);
        mPreviewSize = getOptimalPreviewSize(width, height, targetRatio);
    }

    private Camera.Size getMaxPicSize() {
        if (mSupportedPictureSizes == null) {
            return null;
        }

        Camera.Size maxPicSize = null;
        for (Camera.Size size : mSupportedPictureSizes) {
            if (maxPicSize == null || maxPicSize.height * maxPicSize.width < size.height * size.width) {
                maxPicSize = size;
            }
        }

        return maxPicSize;
    }

    private Camera.Size getOptimalPreviewSize(int w, int h, double targetRatio) {

        List<Camera.Size> minRatioDiffSizes = new ArrayList<>();
        double minRatioDiff = Double.MAX_VALUE;
        for (Camera.Size size : mSupportedPreviewSizes) {
            double ratio = (double)size.width / size.height;
            double ratioDiff = Math.abs(ratio - targetRatio);
            if (ratioDiff < minRatioDiff) {
                minRatioDiffSizes.clear();
                minRatioDiffSizes.add(size);
                minRatioDiff = ratioDiff;
            } else if (ratioDiff == minRatioDiff) {
                minRatioDiffSizes.add(size);
            }
        }

        if (minRatioDiffSizes.isEmpty()) {
            return null;
        }

        Camera.Size optimalSize = minRatioDiffSizes.get(0);
        int minAreaDiff = Math.abs(optimalSize.width * optimalSize.height - w * h);
        for (Camera.Size size : mSupportedPreviewSizes) {
            int areaDiff = Math.abs(size.width * size.height - w * h);
            if (areaDiff < minAreaDiff) {
                optimalSize = size;
                minAreaDiff = areaDiff;
            }
        }

        return optimalSize;
    }
}