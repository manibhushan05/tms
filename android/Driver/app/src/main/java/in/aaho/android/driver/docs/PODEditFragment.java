package in.aaho.android.driver.docs;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Bundle;
import android.support.v4.app.ActivityCompat;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.TextView;

import java.io.File;
import java.io.IOException;

import in.aaho.android.driver.R;
import in.aaho.android.driver.camera.CameraActivity;
import in.aaho.android.driver.common.BaseActivity;
import in.aaho.android.driver.common.BaseDialogFragment;
import in.aaho.android.driver.common.Cache;
import in.aaho.android.driver.common.ImageReadyListener;
import in.aaho.android.driver.common.NetworkUtil;
import in.aaho.android.driver.common.S3Util;
import in.aaho.android.driver.common.StorageUtil;
import in.aaho.android.driver.common.Utils;

/**
 * Created by shobhit on 8/8/16.
 */

public class PODEditFragment extends BaseDialogFragment {
    private static final int SELECT_DOC_REQUEST_CODE = 99;
    private static final int REQUEST_IMAGE_CAPTURE = 95;

    private Button doneButton, cancelButton;
    private ProgressBar progressBar;
    private View dialogView;

    private ImageButton docCameraBtn, docGalleryBtn, docViewBtn;
    private ImageButton[] docBtns;

    private LinearLayout imageProgressView;
    private ImageView brokenImageView, docThumbView;
    private TextView noDocTextView;
    private ScrollView imageContainerView;

    private ResultListener resultListener = null;
    private Result result = new Result();

    private boolean uploading = false;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        dialogView = inflater.inflate(R.layout.document_edit_dialog, container, false);

        setViewVariables();
        setClickListeners();

        updateFormData();

        loadImage();


        return dialogView;
    }

    private void loadImage() {
        imageContainerView.setVisibility(View.GONE);
        brokenImageView.setVisibility(View.GONE);

        String thumbUrl = result == null ? null : result.getThumbUrl();
        if (Utils.not(thumbUrl)) {
            thumbUrl = result == null ? null : result.getUrl();  // default to full image if thumb is not found
        }
        if (Utils.not(thumbUrl)) {
            imageProgressView.setVisibility(View.GONE);
            noDocTextView.setVisibility(View.VISIBLE);
            return;
        }
        imageProgressView.setVisibility(View.VISIBLE);
        noDocTextView.setVisibility(View.GONE);

        Cache cache = Cache.getInstance(getActivity());
        cache.getImage(thumbUrl, new ImageReadyListener() {
            @Override
            public void onReady(Bitmap bitmap) {
                if (bitmap == null) {
                    imageProgressView.setVisibility(View.GONE);
                    brokenImageView.setVisibility(View.VISIBLE);
                    toast("unable to fetch thumbnail");
                } else {
                    imageContainerView.setVisibility(View.VISIBLE);
                    imageProgressView.setVisibility(View.GONE);
                    docThumbView.setImageBitmap(bitmap);
                }
            }
        });

    }

    private void updateFormData() {
        updateBtnUI();

        if (result == null) {
            return;
        }
        updateDocThumb();
    }

    private void updateDocThumb() {
        loadImage();
    }

    private void updateResult() {

    }

    private void setClickListeners() {
        doneButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (uploading) {
                    return;
                }
                updateResult();
                if (resultListener != null) {
                    resultListener.onResult(result);
                }
                dismiss();
            }
        });
        cancelButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dismiss();
            }
        });

        docGalleryBtn.setOnClickListener(new DocGalleryClickListener());
        docCameraBtn.setOnClickListener(new DocCameraClickListener());
        docViewBtn.setOnClickListener(new DocViewClickListener());
    }

    private void setViewVariables() {
        doneButton = (Button) dialogView.findViewById(R.id.document_dialog_ok_btn);
        cancelButton = (Button) dialogView.findViewById(R.id.document_dialog_cancel_btn);

        progressBar = (ProgressBar) dialogView.findViewById(R.id.document_dialog_upload_progress);

        docCameraBtn = (ImageButton) dialogView.findViewById(R.id.document_file_camera_btn);
        docGalleryBtn = (ImageButton) dialogView.findViewById(R.id.document_file_gallery_btn);
        docViewBtn = (ImageButton) dialogView.findViewById(R.id.document_file_view_btn);

        imageProgressView = (LinearLayout) dialogView.findViewById(R.id.image_progress_bar);
        brokenImageView = (ImageView) dialogView.findViewById(R.id.image_broken_image_icon);
        docThumbView = (ImageView) dialogView.findViewById(R.id.image_view);
        noDocTextView = (TextView) dialogView.findViewById(R.id.image_not_selected_text_view);
        imageContainerView = (ScrollView) dialogView.findViewById(R.id.image_container);

        docBtns = new ImageButton[] {docCameraBtn, docGalleryBtn, docViewBtn};

    }

    private void startTransfer(File[] files) {
        if (files == null) {
            uploading = false;
            updateBtnUI();
            return;
        }

        progressBar.setVisibility(View.VISIBLE);
        progressBar.setProgress(0);
        doneButton.setEnabled(false);
        noDocTextView.setText("Uploading...");

        S3Util s3Util = new S3Util(files[0], files[1], new MultiTransferListener());
        s3Util.start();
    }


    private void startTransfer(Uri uri) {
        File[] files = StorageUtil.saveToTempImages(getActivity(), uri);
        if (files == null) {
            toast("Could not save file for URI = " + uri.toString());
        }
        startTransfer(files);
    }

    private void startTransfer(Bitmap bmp) {
        File[] files = StorageUtil.saveToTempImages(getActivity(), bmp);
        if (files == null) {
            toast("Could not save file for bitmap");
        }
        startTransfer(files);
    }

    private class MultiTransferListener implements S3Util.S3UploadListener {
        @Override
        public void onSuccess(String filename, String thumbFileName) {
            result.setUrl(filename);
            result.setThumbUrl(thumbFileName);
            updateDocUI();
        }

        @Override
        public void onError(String msg) {
            toast(msg);
            updateDocUI();
        }

        @Override
        public void onProgress(int progress) {
            progressBar.setProgress(progress);
        }
    }

    private void updateDocUI() {
        progressBar.setVisibility(View.INVISIBLE);
        uploading = false;
        noDocTextView.setText("no document selected");
        updateDocThumb();
        doneButton.setEnabled(true);
        updateBtnUI();
    }

    private void disableAll() {
        for (ImageButton imageButton : docBtns) {
            imageButton.setEnabled(false);
        }
    }

    private void updateBtnUI() {
        if (docCameraBtn != null) {
            docCameraBtn.setEnabled(isCameraAvailable() && hasCameraPerms());
        }
        if (docGalleryBtn != null) {
            docGalleryBtn.setEnabled(true);
        }
    }

    private static Boolean cameraAvailable = null;

    private boolean hasCameraPerms() {
        return ActivityCompat.checkSelfPermission(getActivity(), Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED;
    }

    private boolean isCameraAvailable() {
        if (cameraAvailable == null) {
            PackageManager pm = getActivity().getPackageManager();
            cameraAvailable = pm.hasSystemFeature(PackageManager.FEATURE_CAMERA);
        }
        return cameraAvailable;
    }

    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent intent) {
        super.onActivityResult(requestCode, resultCode, intent);
        Log.e("[POD]", "onActivityResult");
        if (requestCode == SELECT_DOC_REQUEST_CODE) {
            if (resultCode == Activity.RESULT_OK && intent != null && intent.getData() != null) {
                if (!NetworkUtil.canConnect()) {
                    toast("Error: Network is not connected");
                    uploading = false;
                    updateBtnUI();
                    return;
                }
                Uri uri = intent.getData();
                startTransfer(uri);
            } else {
                toast("Nothing Selected");
                uploading = false;
                updateBtnUI();
                return;
            }
        } else if (requestCode == REQUEST_IMAGE_CAPTURE) {
            Log.e("[POD]", "requestCode == REQUEST_IMAGE_CAPTURE");
            if (resultCode == Activity.RESULT_OK && intent != null) {
                Log.e("[POD]", "resultCode == Activity.RESULT_OK && intent != null");
                if (!NetworkUtil.canConnect()) {
                    toast("Error: Network is not connected");
                    uploading = false;
                    updateBtnUI();
                    return;
                }

                Bitmap capturedImage = CameraActivity.capturedImage;
                if (capturedImage == null) {
                    toast("Error: capturedImage is null");
                    uploading = false;
                    updateBtnUI();
                    return;
                }
                startTransfer(capturedImage);
            } else {
                toast("Nothing Selected");
                uploading = false;
                updateBtnUI();
                return;
            }
        }
    }

    private class DocGalleryClickListener implements View.OnClickListener {

        @Override
        public void onClick(View v) {
            if (!uploading) {
                uploading = true;
                disableAll();
                Intent intent = new Intent();
                intent.setType("image/*");
                // intent.setType("image/*|application/pdf");
                intent.setAction(Intent.ACTION_GET_CONTENT);
                // intent.addCategory(Intent.CATEGORY_OPENABLE);
                startActivityForResult(Intent.createChooser(intent, "Select Image"), SELECT_DOC_REQUEST_CODE);
            }
        }
    }

    private class DocCameraClickListener implements View.OnClickListener {

        @Override
        public void onClick(View v) {
            if (!uploading) {
                Intent takePictureIntent = getCameraIntent();
                if (takePictureIntent != null) {
                    uploading = true;
                    disableAll();
                    startActivityForResult(takePictureIntent, REQUEST_IMAGE_CAPTURE);
                }
            }
        }
    }

    private Intent getCameraIntent() {
        Intent takePictureIntent = new Intent(getActivity(), CameraActivity.class);
        return takePictureIntent;
    }

    private StorageUtil.DeviceFile newImageFile() {
        StorageUtil.DeviceFile photoFile;
        try {
                photoFile = StorageUtil.createImageFile();
        } catch (IOException ex) {
            // Error occurred while creating the File
            ex.printStackTrace();
            toast(ex.toString());
            return null;
        }

        // Continue only if the File was successfully created
        if (photoFile != null && photoFile.getFile() != null) {
            return photoFile;
        } else {
            toast("Error: Could not create file");
            return null;
        }

    }

    private class DocViewClickListener implements View.OnClickListener {

        @Override
        public void onClick(View v) {
            String url = result == null ? null : result.url;
            url = url == null ? null : url.trim();
            if (url == null || url.isEmpty()) {
                toast("No image to view");
                return;
            }
            ImageDialogFragment.showNewDialog(getBaseActivity(), url);
        }
    }

    public interface ResultListener {
        void onResult(Result result);
    }

    public void setResultListener(ResultListener resultListener) {
        this.resultListener = resultListener;
    }

    public void setValues(String doc, String thumb) {
        this.result = new Result(doc, thumb);
    }

    public static class Builder {
        private BaseActivity activity;
        private ResultListener resultListener;
        private String doc, thumb;

        public Builder(BaseActivity activity, ResultListener resultListener) {
            this.activity = activity;
            this.resultListener = resultListener;
        }

        public Builder setValues(Pod pod) {
            if (pod != null) {
                setValues(pod.url, pod.thumbUrl);
            }
            return this;
        }

        private Builder setValues(String doc, String thumb) {
            this.doc = doc;
            this.thumb = thumb;
            return this;
        }

        public void build() {
            PODEditFragment documentDialog = new PODEditFragment();
            documentDialog.setResultListener(resultListener);
            documentDialog.setActivity(activity);
            if (doc != null) {
                documentDialog.setValues(doc, thumb);
            }
            documentDialog.show(activity.getSupportFragmentManager(), "pod_fragment");
        }

    }

    public static class Result {
        private String url = null;
        private String thumbUrl = null;

        private boolean edited = false;

        private Result() {

        }

        public Result(String url, String thumbUrl) {
            this.url = url;
            this.thumbUrl = thumbUrl;
        }

        public Pod getDocument() {
            return new Pod(url, thumbUrl, edited);
        }

        public String getThumbUrl() {
            return thumbUrl;
        }


        public String getUrl() {
            return url;
        }

        public boolean isEdited() {
            return edited;
        }


        public void setUrl(String url) {
            if (!Utils.equals(this.url, url)) {
                this.url = url;
                this.edited = true;
            }
        }

        public void setThumbUrl(String thumbUrl) {
            if (!Utils.equals(this.thumbUrl, thumbUrl)) {
                this.thumbUrl = thumbUrl;
                this.edited = true;
            }
        }

    }
}