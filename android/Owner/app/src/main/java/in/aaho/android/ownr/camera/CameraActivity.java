package in.aaho.android.ownr.camera;

import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Matrix;
import android.hardware.Camera;
import android.os.Bundle;
import android.view.View;
import android.widget.FrameLayout;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.RelativeLayout;

import java.util.List;

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.common.BaseActivity;
import in.aaho.android.ownr.common.StorageUtil;

/**
 * Created by mani on 26/11/16.
 */
@SuppressWarnings("deprecation")
public class CameraActivity extends BaseActivity {

    private Camera mCamera;
    private CameraSurfaceView cameraSurfaceView;

    private RelativeLayout cameraContainer, reviewContainer;

    private FrameLayout previewLayout;
    private ImageView reviewImageView;
    private ImageButton captureButton, flashToggle, recaptureButton, okButton, backButton;

    private final CameraPictureCallback callback = new CameraPictureCallback();

    public static Bitmap capturedImage = null;

    private int flashMode = 0;

    private static final String[] FLASH_MODES = new String[] {
            Camera.Parameters.FLASH_MODE_AUTO,
            Camera.Parameters.FLASH_MODE_ON,
            Camera.Parameters.FLASH_MODE_OFF
    };

    private static final int[] FLASH_IMAGES = new int[] {
            R.drawable.ic_flash_auto_black_24dp,
            R.drawable.ic_flash_on_black_24dp,
            R.drawable.ic_flash_off_black_24dp
    };

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.camera_activity);

        setViewVariables();
        setClickListeners();
    }

    @Override
    protected void onResume() {
        super.onResume();
        setupCamera();
    }

    private void setupCamera() {
        // Create an instance of Camera
        mCamera = getCameraInstance();
        if (mCamera != null) {
            // Create our Preview view and set it as the content of our activity.
            cameraSurfaceView = new CameraSurfaceView(this, mCamera);
            previewLayout.removeAllViews();
            previewLayout.addView(cameraSurfaceView);
        } else {
            toast("Unable to open the camera");
            return;
        }

        setCameraParams();
    }

    private void setCameraParams() {
        // get Camera parameters
        Camera.Parameters params = mCamera.getParameters();
        if (params.getFlashMode() != null) {
            // set the focus mode
            //params.setFocusMode(Camera.Parameters.FOCUS_MODE_AUTO);
            List<String> focusModes = params.getSupportedFocusModes();

            boolean hasAutoFocus = focusModes != null &&
                    focusModes.contains(Camera.Parameters.FOCUS_MODE_AUTO);
            if(hasAutoFocus) {
                params.setFocusMode(Camera.Parameters.FOCUS_MODE_AUTO);
            }

            if (focusModes.contains(Camera.Parameters.FOCUS_MODE_CONTINUOUS_PICTURE)) {
                params.setFocusMode(Camera.Parameters.FOCUS_MODE_CONTINUOUS_PICTURE);
            }

            params.setFlashMode(FLASH_MODES[flashMode]);
            // set Camera parameters
            mCamera.setParameters(params);
        }
    }

    private boolean toggling = false;

    private void toggleFlash() {
        toggling = true;
        if (flashMode == FLASH_MODES.length - 1) {
            flashMode = 0;
        } else {
            flashMode++;
        }
        Camera.Parameters params = mCamera.getParameters();
        params.setFlashMode(FLASH_MODES[flashMode]);
        mCamera.setParameters(params);
        setFlashUI();
        toggling = false;
    }

    private void setFlashUI() {
        flashToggle.setImageResource(FLASH_IMAGES[flashMode]);
    }

    private void setViewVariables() {
        cameraContainer = findViewById(R.id.camera_container);
        reviewContainer = findViewById(R.id.review_image_container);

        previewLayout = findViewById(R.id.camera_preview);

        captureButton = findViewById(R.id.button_capture);
        recaptureButton = findViewById(R.id.button_recapture);
        okButton = findViewById(R.id.button_ok);
        flashToggle = findViewById(R.id.button_flash);
        backButton = findViewById(R.id.button_back);

        reviewImageView = findViewById(R.id.review_image_view);
    }

    private void setClickListeners() {
        captureButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // get an image from the camera
                resetResult();
                mCamera.takePicture(null, null, callback);
            }
        });
        flashToggle.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (!toggling) {
                    toggleFlash();
                }
            }
        });
        recaptureButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                resetResult();
                resetUI();
            }
        });
        okButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                setResult(RESULT_OK, new Intent());
                finish();
            }
        });
        backButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                onBackPressed();
            }
        });
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        resetResult();
        resetUI();
    }

    private void resetResult() {
        if (capturedImage != null) {
            capturedImage.recycle();
            capturedImage = null;
        }
    }

    private void resetUI() {
        reviewContainer.setVisibility(View.GONE);
        cameraContainer.setVisibility(View.VISIBLE);
        setupCamera();
    }

    /** A safe way to get an instance of the Camera object. */
    public static Camera getCameraInstance(){
        Camera c = null;
        try {
            c = Camera.open(); // attempt to get a Camera instance
        }
        catch (Exception e){
            // Camera is not available (in use or does not exist)
        }
        return c; // returns null if camera is unavailable
    }

    @Override
    protected void onPause() {
        super.onPause();
        releaseCamera();              // release the camera immediately on pause event
    }

    private void releaseCamera(){
        if (mCamera != null){
            mCamera.release();        // release the camera for other applications
            mCamera = null;
        }
    }

    private class CameraPictureCallback implements Camera.PictureCallback {

        @Override
        public void onPictureTaken(byte[] data, Camera camera) {
            capturedImage = StorageUtil.scaleDownRawImage(BitmapFactory.decodeByteArray(data, 0, data.length));
            startReview();
        }
    }

    private void startReview() {
        releaseCamera();
        reviewContainer.setVisibility(View.VISIBLE);
        cameraContainer.setVisibility(View.GONE);
        reviewImageView.setImageBitmap(capturedImage);
    }

}