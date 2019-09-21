package in.aaho.android.aahocustomers;

import android.app.Activity;
import android.os.Bundle;
import android.text.TextUtils;
import android.util.Log;

import org.json.JSONObject;

import java.util.ArrayList;

import in.aaho.android.aahocustomers.common.ApiResponseListener;
import in.aaho.android.aahocustomers.common.BaseActivity;
import in.aaho.android.aahocustomers.common.S3Util;
import in.aaho.android.aahocustomers.common.Utils;
import in.aaho.android.aahocustomers.data.PODData;
import in.aaho.android.aahocustomers.docs.Document;
import in.aaho.android.aahocustomers.docs.DocumentEditFragment;
import in.aaho.android.aahocustomers.requests.PODUploadRequest;

/**
 * Created by aaho on 14/06/18.
 */


public class UploadActivity extends BaseActivity {

    public static final String title = "Upload POD";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_upload);

        launchUploadDialog(null);
    }

    @Override
    public void onBackPressed() {
        super.onBackPressed();
        finish();
    }

    private void launchUploadDialog(Document doc) {
        DocumentEditFragment.ResultListenerForPOD listener = new DocumentEditFragment.ResultListenerForPOD() {
            @Override
            public void onResult(String lrNumber, String url, String thumbUrl, String bucketname,
                                 String foldername, String filename, String uuid,
                                 String displayUrl, ArrayList<PODData> podDataArrayList) {
                if(TextUtils.isEmpty(lrNumber)) {
                    toast("POD Not uploaded!");
                    finish();
                } else {
                    makePodUploadEntryRequest(lrNumber,url,thumbUrl,bucketname,foldername,filename,
                            uuid,displayUrl,podDataArrayList);
                }
                Log.i("Upload Activity","onResult"+lrNumber);
            }
        };

        Bundle bundle = getIntent().getExtras();
        String lrNumber = "";
        if(bundle != null && bundle.containsKey("LR_LIST")) {
            lrNumber = bundle.getString("LR_LIST");
        }
        ArrayList<String> lrList = new ArrayList<>();
        if (!TextUtils.isEmpty(lrNumber)) {
            String[] lrNumberList = lrNumber.split("\n");
            // Add selection options only when there are more than two lr numbers
            if(lrNumberList.length > 2)
                lrList.add("Select");

            for (int i = 0; i < lrNumberList.length; i++) {
                lrList.add(lrNumberList[i]);
            }
        }

        DocumentEditFragment.Builder builder = new DocumentEditFragment
                .Builder(this, title, lrList, listener);


        //builder.setHints(idHint, null);
        builder.setValues(doc);
        builder.setEnabled(false, false, false,
                false, false, false);
        builder.setUploadId(S3Util.S3_UPLOAD_ID_FOR_POD_DIR);
        builder.build();
    }


    private void makePodUploadEntryRequest(String lr_number, String url, String thumbUrl, String bucketname, String foldername, String filename,
                                           String uuid, String displayUrl, ArrayList<PODData> podDataArrayList) {
        PODUploadRequest podUploadRequest = new PODUploadRequest(lr_number,url,thumbUrl,
                bucketname,foldername,filename,uuid,displayUrl,podDataArrayList,new PodUploadListener());
        queue(podUploadRequest);
    }

    private class PodUploadListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            Utils.dismissProgress(UploadActivity.this);
            toast("POD is uploaded!");
            setResult(Activity.RESULT_OK);
            finish();
        }

        @Override
        public void onError() {
            Utils.dismissProgress(UploadActivity.this);
            toast("POD is Not uploaded!");
            setResult(Activity.RESULT_CANCELED);
            finish();
        }
    }

}
