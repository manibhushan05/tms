package in.aaho.android.loads.common;

import android.app.Application;
import android.content.SharedPreferences;
import android.preference.PreferenceManager;

//import com.amazonaws.auth.AWSCredentials;
//import com.amazonaws.mobileconnectors.s3.transferutility.TransferUtility;
//import com.amazonaws.services.s3.AmazonS3;
//import com.amazonaws.services.s3.AmazonS3Client;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.toolbox.Volley;

import org.acra.ACRA;

/**
 * Created by aaho on 18/04/18.
 */


public class MainApplication extends Application {
    private static final String AWS_ACCESS_KEY = "AKIAJXFC3JRVYNIHX2UA";
    private static final String AWS_ACCESS_SECRET_KEY = "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";

//    public static final AWSCredentials awsCredentials = new AWSCredentials() {
//        @Override
//        public String getAWSAccessKeyId() {
//            return AWS_ACCESS_KEY;
//        }
//
//        @Override
//        public String getAWSSecretKey() {
//            return AWS_ACCESS_SECRET_KEY;
//        }
//    };

    private static MainApplication instance = null;
    private static SharedPreferences prefs = null;
//    private static AmazonS3 s3 = null;
//    private static TransferUtility transferUtility = null;
    private static RequestQueue requestQueue = null;

    @Override
    public void onCreate() {
        super.onCreate();
        ACRA.init(this);
        instance = this;
        prefs = PreferenceManager.getDefaultSharedPreferences(this.getApplicationContext());
        //s3 = new AmazonS3Client(awsCredentials);
        //transferUtility = new TransferUtility(s3, this.getApplicationContext());
        Auth.setPersistentCookieStore();
        requestQueue = Volley.newRequestQueue(this.getApplicationContext());
    }

    public static SharedPreferences getPrefs() {
        return prefs;
    }

    public static MainApplication getInstance() {
        return instance;
    }

//    public static AmazonS3 getS3() {
//        return s3;
//    }

//    public static TransferUtility getTransferUtility() {
//        return transferUtility;
//    }

    public static void queueRequest(Request<?> request) {
        requestQueue.add(request);
    }
}