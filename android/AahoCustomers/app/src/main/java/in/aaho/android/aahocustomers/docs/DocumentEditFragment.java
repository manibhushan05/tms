package in.aaho.android.aahocustomers.docs;

import android.Manifest;
import android.annotation.TargetApi;
import android.app.Activity;
import android.app.DatePickerDialog;
import android.content.ClipData;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.MediaStore;
import android.support.v4.app.ActivityCompat;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.ViewGroup.LayoutParams;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.DatePicker;
import android.widget.EditText;
import android.widget.HorizontalScrollView;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.TextView;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;

import in.aaho.android.aahocustomers.R;
import in.aaho.android.aahocustomers.camera.CameraActivity;
import in.aaho.android.aahocustomers.common.BaseActivity;
import in.aaho.android.aahocustomers.common.BaseDialogFragment;
import in.aaho.android.aahocustomers.common.Cache;
import in.aaho.android.aahocustomers.common.ImageReadyListener;
import in.aaho.android.aahocustomers.common.NetworkUtil;
import in.aaho.android.aahocustomers.common.S3Util;
import in.aaho.android.aahocustomers.common.StorageUtil;
import in.aaho.android.aahocustomers.common.Utils;
import in.aaho.android.aahocustomers.data.PODData;

/**
 * Created by mani on 8/8/16.
 */

public class DocumentEditFragment extends BaseDialogFragment {
    private static final int SELECT_DOC_REQUEST_CODE = 99;
    private static final int REQUEST_IMAGE_CAPTURE = 95;

    private Button doneButton, cancelButton;
    private TextView titleText;
    private ProgressBar progressBar;
    private EditText docIdEditText, docValidityEditText;
    private EditText manufactureDateEditText;  // only for rc
    private EditText insurerEditText;  // only for insurance
    private EditText issueLocationEditText;  // only for dl
    private EditText permitTypeEditText;  // only for permit
    private View dialogView;

    private ImageButton docCameraBtn, docGalleryBtn, docViewBtn;
    private ImageButton[] docBtns;

    private LinearLayout imageProgressView,imageContainerViewSet;
    private ImageView brokenImageView, docThumbView;
    private TextView noDocTextView;
    private ScrollView imageContainerView;
    private HorizontalScrollView horizontal_scrollview;


    private boolean idEnabled = true;
    private boolean validityEnabled = true;
    private boolean manufactureDateEnabled = false;
    private boolean insurerEnabled = false;
    private boolean issueLocationEnabled = false;
    private boolean permitTypeEnabled = false;

    private ResultListener resultListener = null;
    private ResultListenerForPOD resultListenerForPOD = null;
    private Result result = new Result();

    private String idHint = "Document ID";
    private String validityHint = "Document Validity";

    private boolean uploading = false;

    private String title = "Select Document";

    private boolean isPODUpload = false;
    public ArrayList<String> mLrList = new ArrayList<>();
    private Spinner spinner;
    /** To know which document to upload */
    private int mUpload_id = 0;
    public static String LRNumber = null;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        dialogView = inflater.inflate(R.layout.document_edit_dialog, container, false);

        setViewVariables();
        setEditTextHints();
        setActiveViews();
        setClickListeners();

        if (titleText != null && title != null) {
            titleText.setText(title);
        }
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
                    //imageContainerView.setVisibility(View.VISIBLE);
                    imageProgressView.setVisibility(View.GONE);
                    if(horizontal_scrollview.getVisibility() == View.VISIBLE) {
                        //TODO: create new imageview dynamically and set image to it
                        imageContainerView.setVisibility(View.GONE);
                        ImageView imageView = new ImageView(getActivity());
                        imageView.setLayoutParams(new LayoutParams(200,
                                LayoutParams.WRAP_CONTENT));
                        imageView.setImageBitmap(bitmap);
                        imageContainerViewSet.addView(imageView);
                    } else {
                        imageContainerView.setVisibility(View.VISIBLE);
                        docThumbView.setImageBitmap(bitmap);
                    }
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
        updateDocValidityEditText(result.getValidity());
        updateEditText(idEnabled, docIdEditText, result.getId());
        updateEditText(manufactureDateEnabled, manufactureDateEditText, result.getManufactureYear());
        updateEditText(insurerEnabled, insurerEditText, result.getInsurerName());
        updateEditText(issueLocationEnabled, issueLocationEditText, result.getIssueLocation());
        updateEditText(permitTypeEnabled, permitTypeEditText, result.getPermitType());
        fillSpinner();
    }

    private void updateDocThumb() {
        loadImage();
    }

    private void updateDocValidityEditText(Date validity) {
        if (validityEnabled && docValidityEditText != null) {
            docValidityEditText.setText(validity == null ? "" : Utils.formatDate(validity));
        }
    }

    private void updateEditText(boolean enabled, EditText editText, String value) {
        if (enabled && editText != null) {
            value = (value == null ? "" : value.trim());
            editText.setText(value);
        }
    }

    private void updateResult() {
        if (idEnabled && docIdEditText != null) {
            result.setId(docIdEditText.getText().toString().trim());
        }
        if (manufactureDateEnabled && manufactureDateEditText != null) {
            result.setManufactureYear(manufactureDateEditText.getText().toString().trim());
        }
        if (insurerEnabled && insurerEditText != null) {
            result.setInsurerName(insurerEditText.getText().toString().trim());
        }
        if (issueLocationEnabled && issueLocationEditText != null) {
            result.setIssueLocation(issueLocationEditText.getText().toString().trim());
        }
        if (permitTypeEnabled && permitTypeEditText != null) {
            result.setPermitType(permitTypeEditText.getText().toString().trim());
        }
    }

    private void setClickListeners() {
        doneButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (uploading) {
                    return;
                }

                if(isPODUpload) {
                    // This section is only for POD upload
                    setLRNumberValueIfNeeded();

                    // check if image is selected or not first
                    if(hasImageUploaded()) {
                        if (resultListenerForPOD != null) {
                            if (spinner != null) {
                                resultListenerForPOD.onResult(spinner.getSelectedItem().toString(),result.url,
                                        result.thumbUrl,result.bucketname,result.foldername,result.filename,
                                        result.uuid,result.displayUrl,podDataArrayList);
                            } else {
                                resultListenerForPOD.onResult("",null,null,null,
                                        null,null,null,null, podDataArrayList);
                            }
                            resultListenerForPOD = null;
                        }
                        dismiss();
                    } else {
                        toast("Please attach POD first!");
                    }
                } else {
                    // This section is for other than POD
                    updateResult();
                    if (resultListener != null) {
                        resultListener.onResult(result);
                    }
                    dismiss();
                }
                //dismiss();
            }
        });
        cancelButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                if(isPODUpload) {
                    if (resultListenerForPOD != null) {
                        resultListenerForPOD.onResult("",null,null,null,
                                null,null,null,null, podDataArrayList);
                    }
                    dismiss();
                } else {
                    dismiss();
                }
            }
        });
        docValidityEditText.setOnClickListener(new ValidityClickListener());

        docGalleryBtn.setOnClickListener(new DocGalleryClickListener());
        docCameraBtn.setOnClickListener(new DocCameraClickListener());
        docViewBtn.setOnClickListener(new DocViewClickListener());
    }

    private void setViewVariables() {
        doneButton = dialogView.findViewById(R.id.document_dialog_ok_btn);
        cancelButton = dialogView.findViewById(R.id.document_dialog_cancel_btn);

        docIdEditText = dialogView.findViewById(R.id.document_id_edittext);
        docValidityEditText = dialogView.findViewById(R.id.document_validity_edittext);
        manufactureDateEditText = dialogView.findViewById(R.id.document_manufacture_year_edittext);
        insurerEditText = dialogView.findViewById(R.id.document_insurer_edittext);
        issueLocationEditText = dialogView.findViewById(R.id.document_issue_location_edittext);
        permitTypeEditText = dialogView.findViewById(R.id.document_permit_type_edittext);

        titleText = dialogView.findViewById(R.id.document_dialog_title);
        progressBar = dialogView.findViewById(R.id.document_dialog_upload_progress);

        docCameraBtn = dialogView.findViewById(R.id.document_file_camera_btn);
        docGalleryBtn = dialogView.findViewById(R.id.document_file_gallery_btn);
        docViewBtn = dialogView.findViewById(R.id.document_file_view_btn);

        imageProgressView = dialogView.findViewById(R.id.image_progress_bar);
        brokenImageView = dialogView.findViewById(R.id.image_broken_image_icon);
        docThumbView = dialogView.findViewById(R.id.image_view);
        noDocTextView = dialogView.findViewById(R.id.image_not_selected_text_view);
        imageContainerView = dialogView.findViewById(R.id.image_container);
        imageContainerViewSet = dialogView.findViewById(R.id.image_container_set);
        horizontal_scrollview = dialogView.findViewById(R.id.horizontal_scrollview);

        docBtns = new ImageButton[] {docCameraBtn, docGalleryBtn, docViewBtn};

        spinner = dialogView.findViewById(R.id.spinner);

    }

    private void setActiveViews() {
        docIdEditText.setVisibility(idEnabled ? View.VISIBLE : View.GONE);
        docValidityEditText.setVisibility(validityEnabled ? View.VISIBLE : View.GONE);
        manufactureDateEditText.setVisibility(manufactureDateEnabled ? View.VISIBLE : View.GONE);
        insurerEditText.setVisibility(insurerEnabled ? View.VISIBLE : View.GONE);
        issueLocationEditText.setVisibility(issueLocationEnabled ? View.VISIBLE : View.GONE);
        permitTypeEditText.setVisibility(permitTypeEnabled ? View.VISIBLE : View.GONE);

        if(mLrList != null && mLrList.size() > 0) {
            isPODUpload = true;
        }

        spinner.setVisibility(isPODUpload ? View.VISIBLE : View.GONE);
    }

    private void setEditTextHints() {
        docIdEditText.setHint(idHint);
        docValidityEditText.setHint(validityHint);
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

        S3Util s3Util = new S3Util(files[0], files[1], new MultiTransferListener(),
                mUpload_id);
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

    ArrayList<PODData> podDataArrayList = new ArrayList<>();

    private class MultiTransferListener implements S3Util.S3UploadListener {
        @Override
        public void onSuccess(String filename, String thumbFileName) {
            String fullFileURl = S3Util.BASE_URL_UPLOAD + filename;
            String fullThumbFileURl = S3Util.BASE_URL_UPLOAD + thumbFileName;
            result.setUrl(fullFileURl);
            result.setThumbUrl(fullThumbFileURl);

            /*result.setUrl(filename);
            result.setThumbUrl(thumbFileName);*/

            result.setBucketname(S3Util.BUCKET_NAME);

            // retrieve file name from full path
            //String folderName = filename.substring(0,filename.lastIndexOf("/"));


            String temp = filename.substring(0,filename.lastIndexOf("/"));
            String upload_dir = temp.substring(0,temp.lastIndexOf("/"));
            String uuid = temp.substring(temp.lastIndexOf("/")+1,temp.length());

            String imgFileName = filename.substring(filename.lastIndexOf("/")+1,
                    filename.length());
            /*String uuid = filename.substring(folderName.lastIndexOf("/")+1,
                    filename.length());*/

            //https://fmsdocuments.s3.amazonaws.com/uploads/vehicle/insurance/616e4a5d-7c01-4ad1-a8ea-917a4c756e39/CG08L3653.jpg'

            result.setFoldername(upload_dir);
            result.setFilename(imgFileName);
            result.setUuid(uuid);

            // send https://s3-ap-southeast-1.amazonaws.com/ + bucketname
            String displayUrl = S3Util.BASE_DISPLAY_URL + filename;
            result.setDisplayUrl(displayUrl);

            updateDocUI();

            // Make a list of POD images which we've uploaded for sending later
            // the entry to server
            PODData podData = new PODData(result.getUrl(),result.thumbUrl,
                    result.getBucketname(),result.getFoldername(),result.getFilename(),
                    result.getUuid(),result.getDisplayUrl());

            podDataArrayList.add(podData);
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
        docCameraBtn.setEnabled(isCameraAvailable() && hasCameraPerms());
        docGalleryBtn.setEnabled(true);
    }

    private void fillSpinner() {
        ArrayAdapter aa = new ArrayAdapter(getContext(),android.R.layout.simple_spinner_item,mLrList);
        aa.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        //Setting the ArrayAdapter data on the Spinner
        spinner.setAdapter(aa);
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

    @TargetApi(Build.VERSION_CODES.JELLY_BEAN)
    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent intent) {
        super.onActivityResult(requestCode, resultCode, intent);
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
            } else if(intent.getClipData() != null) {
                // means user selected more than one images for upload
                horizontal_scrollview.setVisibility(View.VISIBLE);
                imageContainerView.setVisibility(View.GONE);
                String[] filePathColumn = { MediaStore.Images.Media.DATA };
//                ArrayList<String> imagesEncodedList = new ArrayList<String>();
                if (intent.getClipData() != null) {
                    ClipData mClipData = intent.getClipData();
                    ArrayList<Uri> mArrayUri = new ArrayList<Uri>();
                    for (int i = 0; i < mClipData.getItemCount(); i++) {
                        ClipData.Item item = mClipData.getItemAt(i);
                        Uri uri = item.getUri();
                        startTransfer(uri); // start the file transfer
                        mArrayUri.add(uri);
                        // Get the cursor
                        Cursor cursor = getActivity().getContentResolver().query(uri, filePathColumn, null, null, null);
                        // Move to first row
                        cursor.moveToFirst();

                        /*int columnIndex = cursor.getColumnIndex(filePathColumn[0]);
                        String imageEncoded  = cursor.getString(columnIndex);
                        imagesEncodedList.add(imageEncoded);
                        cursor.close();*/

                    }
                    Log.v("LOG_TAG", "Selected Images" + mArrayUri.size());
                }
            } else {
                toast("Nothing Selected");
                uploading = false;
                updateBtnUI();
                return;
            }
        } else if (requestCode == REQUEST_IMAGE_CAPTURE) {
            if (resultCode == Activity.RESULT_OK && intent != null) {
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
            if(!setLRNumberValueIfNeeded()) {
                return;
            }

            if (!uploading) {
                uploading = true;
                disableAll();
                Intent intent = new Intent();
                intent.setType("image/*");
                // intent.setType("image/*|application/pdf");
                intent.setAction(Intent.ACTION_GET_CONTENT);
                intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true);
                // intent.addCategory(Intent.CATEGORY_OPENABLE);
                startActivityForResult(Intent.createChooser(intent, "Select Image"), SELECT_DOC_REQUEST_CODE);
            }
        }
    }

    private class DocCameraClickListener implements View.OnClickListener {

        @Override
        public void onClick(View v) {
            if(!setLRNumberValueIfNeeded()) {
                return;
            }

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
            String url = result == null ? null : result.url.trim();
            if (url == null || url.isEmpty()) {
                toast("No image to view");
                return;
            }
            ImageDialogFragment.showNewDialog(getBaseActivity(), url);
        }
    }

    private class ValidityClickListener implements View.OnClickListener {

        @Override
        public void onClick(View v) {
            Calendar c = Calendar.getInstance();
            Date validityDate = result.getValidity();
            if (validityDate != null) {
                c.setTime(validityDate);
            }
            int mYear = c.get(Calendar.YEAR);
            int mMonth = c.get(Calendar.MONTH);
            int mDay = c.get(Calendar.DAY_OF_MONTH);

            ValiditySetListener dateSetListener = new ValiditySetListener();

            DatePickerDialog datePickerDialog = new DatePickerDialog(getActivity(), dateSetListener, mYear, mMonth, mDay);
            datePickerDialog.show();
        }
    }

    private class ValiditySetListener implements DatePickerDialog.OnDateSetListener {

        @Override
        public void onDateSet(DatePicker view, int year, int monthOfYear, int dayOfMonth) {
            result.setValidity(Utils.getDate(year, monthOfYear, dayOfMonth));
            updateDocValidityEditText(result.getValidity());
        }
    }

    public interface ResultListener {
        void onResult(Result result);
    }

    public void setResultListener(ResultListener resultListener) {
        this.resultListener = resultListener;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public void setValues(String doc, String thumb, String id, Date validity, String type, String manufactureYear,
                          String insurerName, String issueLocation, String permitType,
                          String bucketname, String foldername, String filename,
                          String uuid, String displayUrl) {
        this.result = new Result(doc, thumb, id, validity, type, manufactureYear,
                insurerName, issueLocation, permitType,
                bucketname, foldername, filename, uuid, displayUrl);
    }

    public void setHints(String idHint, String validityHint) {
        if (!Utils.not(idHint)) {
            this.idHint = idHint;
        }
        if (!Utils.not(validityHint)) {
            this.validityHint = validityHint;
        }
    }

    public void setEnabled(boolean idEnabled, boolean validityEnabled,
                           boolean manufactureDateEnabled, boolean insurerEnabled,
                           boolean issueLocationEnabled, boolean permitTypeEnabled) {
        this.idEnabled = idEnabled;
        this.validityEnabled = validityEnabled;
        this.manufactureDateEnabled = manufactureDateEnabled;
        this.insurerEnabled = insurerEnabled;
        this.issueLocationEnabled = issueLocationEnabled;
        this.permitTypeEnabled = permitTypeEnabled;
    }


    public static class Builder {
        private BaseActivity activity;
        private String title;

        private String idHint, validityHint;
        private ResultListener resultListener;
        private ResultListenerForPOD resultListenerForPOD;

        private String doc, thumb, id, type, manufactureYear, insurerName, issueLocation,
                permitType, bucketname, foldername, filename, uuid, displayUrl;
        private Date validity;

        private boolean idEnabled = true, validityEnabled = true;
        private boolean issueLocationEnabled = false, manufactureDateEnabled = false;
        private boolean insurerEnabled = false, permitTypeEnabled = false;

        private ArrayList<String> lrList = new ArrayList<>();
        private int upload_id = 0;

        public Builder(BaseActivity activity, String title, ResultListener resultListener) {
            this.activity = activity;
            this.title = title;
            this.resultListener = resultListener;
        }

        public Builder(BaseActivity activity, String title, ArrayList<String> lrList,
                       ResultListenerForPOD resultListenerForPOD) {
            this.activity = activity;
            this.title = title;
            this.lrList = lrList;
            this.resultListenerForPOD = resultListenerForPOD;
        }

        public Builder setHints(String idHint, String validityHint) {
            this.idHint = idHint;
            this.validityHint = validityHint;
            return this;
        }

        public Builder setValues(Document document) {
            if (document != null) {
                setValues(document.url, document.thumbUrl, document.id, document.validity, document.type,
                        document.manufactureYear, document.insurerName, document.issueLocation,
                        document.permitType,document.bucketname,document.foldername,
                        document.filename,document.uuid,document.displayUrl);
            }
            return this;
        }

        public void setUploadId(int upload_id) {
            this.upload_id = upload_id;
        }

        private Builder setValues(String doc, String thumb, String id, Date validity, String type, String manufactureYear,
                                  String insurerName, String issueLocation, String permitType,
                                  String bucketname, String foldername, String filename,
                                  String uuid, String displayUrl) {
            this.doc = doc;
            this.thumb = thumb;
            this.id = id;
            this.validity = validity;
            this.type = type;
            this.manufactureYear = manufactureYear;
            this.insurerName = insurerName;
            this.issueLocation = issueLocation;
            this.permitType = permitType;

            this.bucketname = bucketname;
            this.foldername = foldername;
            this.filename = filename;
            this.uuid = uuid;
            this.displayUrl = displayUrl;

            return this;
        }

        public Builder setEnabled(boolean idEnabled, boolean validityEnabled,
                                  boolean manufactureDateEnabled, boolean insurerEnabled,
                                  boolean issueLocationEnabled, boolean permitTypeEnabled) {
            this.idEnabled = idEnabled;
            this.validityEnabled = validityEnabled;
            this.manufactureDateEnabled = manufactureDateEnabled;
            this.insurerEnabled = insurerEnabled;
            this.issueLocationEnabled = issueLocationEnabled;
            this.permitTypeEnabled = permitTypeEnabled;
            return this;
        }

        public void build() {
            DocumentEditFragment documentDialog = new DocumentEditFragment();
            documentDialog.setTitle(title);
            documentDialog.setResultListener(resultListener);
            documentDialog.setActivity(activity);
            if (id != null || doc != null || validity != null) {
                documentDialog.setValues(doc, thumb, id, validity, type, manufactureYear,
                        insurerName, issueLocation, permitType,
                        bucketname,foldername,filename,uuid,displayUrl);
            }
            if (idHint != null || validityHint != null) {
                documentDialog.setHints(idHint, validityHint);
            }

            if(lrList != null && lrList.size() > 0) {
                documentDialog.setResultListenerForPOD(resultListenerForPOD);
                documentDialog.setLRList(lrList);
            }

            // Set upload id
            documentDialog.setUploadId(upload_id);

            documentDialog.setEnabled(idEnabled, validityEnabled, manufactureDateEnabled, insurerEnabled,
                    issueLocationEnabled, permitTypeEnabled);
            documentDialog.show(activity.getSupportFragmentManager(), "doc_fragment_" + System.currentTimeMillis());
        }

    }

    public static class Result {
        private String url = null;
        private String thumbUrl = null;
        private String id = null;
        private String type = null;
        private Date validity = null;

        private String manufactureYear = null;
        private String insurerName = null;
        private String issueLocation = null;
        private String permitType = null;

        private boolean edited = false;

        // Added by suraj.m
        public String filename = null;
        public String foldername = null;
        public String bucketname = null;
        public String uuid = null;
        public String displayUrl = null;

        private Result() {

        }

        public Result(String url, String thumbUrl, String id, Date validity, String type,
                      String manufactureYear, String insurerName, String issueLocation,
                      String permitType, String bucketname, String foldername, String filename,
                      String uuid, String displayUrl) {
            this.url = url;
            this.thumbUrl = thumbUrl;
            this.id = id;
            this.validity = validity;
            this.type = type;
            this.manufactureYear = manufactureYear;
            this.insurerName = insurerName;
            this.issueLocation = issueLocation;
            this.permitType = permitType;

            this.bucketname = bucketname;
            this.foldername = foldername;
            this.filename = filename;
            this.uuid = uuid;
            this.displayUrl = displayUrl;
        }

        public Document getDocument() {
            return new Document(url, thumbUrl, id, validity, type, manufactureYear, insurerName, issueLocation,
                    permitType, edited, bucketname, foldername, filename, uuid, displayUrl);
        }

        public void setType(String type) {
            this.type = type;
        }

        public String getType() {
            return type;
        }

        public String getThumbUrl() {
            return thumbUrl;
        }

        public Date getValidity() {
            return validity;
        }

        public String getId() {
            return id;
        }

        public String getUrl() {
            return url;
        }

        public boolean isEdited() {
            return edited;
        }

        public String getInsurerName() {
            return insurerName;
        }

        public String getIssueLocation() {
            return issueLocation;
        }

        public String getManufactureYear() {
            return manufactureYear;
        }

        public String getPermitType() {
            return permitType;
        }

        public void setId(String id) {
            if (!Utils.equals(this.id, id)) {
                this.id = id;
                this.edited = true;
            }
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

        public void setValidity(Date validity) {
            if (!Utils.equals(this.validity, validity)) {
                this.validity = validity;
                this.edited = true;
            }
        }

        public void setInsurerName(String insurerName) {
            if (!Utils.equals(this.insurerName, insurerName)) {
                this.insurerName = insurerName;
                this.edited = true;
            }
        }

        public void setIssueLocation(String issueLocation) {
            if (!Utils.equals(this.issueLocation, issueLocation)) {
                this.issueLocation = issueLocation;
                this.edited = true;
            }
        }

        public void setManufactureYear(String manufactureYear) {
            if (!Utils.equals(this.manufactureYear, manufactureYear)) {
                this.manufactureYear = manufactureYear;
                this.edited = true;
            }
        }

        public void setPermitType(String permitType) {
            if (!Utils.equals(this.permitType, permitType)) {
                this.permitType = permitType;
                this.edited = true;
            }
        }

        // Added by suraj m
        public String getFilename() {
            return filename;
        }

        public void setFilename(String filename) {
            this.filename = filename;
        }

        public String getFoldername() {
            return foldername;
        }

        public void setFoldername(String foldername) {
            this.foldername = foldername;
        }

        public String getBucketname() {
            return bucketname;
        }

        public void setBucketname(String bucketname) {
            this.bucketname = bucketname;
        }

        public String getUuid() {
            return uuid;
        }

        public void setUuid(String uuid) {
            this.uuid = uuid;
        }

        public String getDisplayUrl() {
            return displayUrl;
        }

        public void setDisplayUrl(String displayUrl) {
            this.displayUrl = displayUrl;
        }
    }

    public void setLRList(ArrayList<String> lrList) {
        this.mLrList = lrList;
    }

    public void setUploadId(int upload_id) {
        this.mUpload_id = upload_id;
    }

    public interface ResultListenerForPOD {
        void onResult(String lrNumber, String url, String thumbUrl, String bucketname,
                      String foldername, String filename, String uuid, String displayUrl, ArrayList<PODData> podDataArrayList);
    }

    public void setResultListenerForPOD(ResultListenerForPOD resultListenerForPOD) {
        this.resultListenerForPOD = resultListenerForPOD;
    }

    private boolean setLRNumberValueIfNeeded() {
        if(isPODUpload) {
            if (spinner.getSelectedItem().toString().equalsIgnoreCase("Select")) {
                toast("Please select LR Number first!");
                return false;
            } else {
                LRNumber = spinner.getSelectedItem().toString();
                return true;
            }
        } else {
            return true;
        }
    }

    /** Check if image is uploaded or not
     * @return return true if image(s) has been uploaded else return false
     */
    private boolean hasImageUploaded() {
        return imageContainerView.getVisibility() == View.VISIBLE ||
                horizontal_scrollview.getVisibility() == View.VISIBLE;

    }

    @Override
    public void onDismiss(DialogInterface dialog) {
        super.onDismiss(dialog);
        if(isPODUpload) {
            if (resultListenerForPOD != null) {
                resultListenerForPOD.onResult("",null,null,null,
                        null,null,null,null, podDataArrayList);
            }
        }
    }

    /** check the validation required */
    private boolean isValidInputByUser() {
        return mUpload_id == S3Util.S3_UPLOAD_ID_FOR_DRIVER_PAN_DIR
                || mUpload_id == S3Util.S3_UPLOAD_ID_FOR_DRIVER_PAN_DIR;
    }
}