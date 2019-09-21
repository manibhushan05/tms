//package in.aaho.android.employee.activity;
//
//import android.app.ProgressDialog;
//import android.os.AsyncTask;
//import android.os.Bundle;
//import android.support.v7.app.AppCompatActivity;
//import android.support.v7.widget.Toolbar;
//import android.view.MenuItem;
//
//import com.github.barteksc.pdfviewer.PDFView;
//
//import java.io.BufferedInputStream;
//import java.io.IOException;
//import java.io.InputStream;
//import java.net.HttpURLConnection;
//import java.net.URL;
//
//import in.aaho.android.employee.R;
//import in.aaho.android.employee.common.Utils;
//
//public class PDFViewerActivity extends AppCompatActivity {
//
//    private PDFView mPdfView;
//    private ProgressDialog progress;
//
//    @Override
//    protected void onCreate(Bundle savedInstanceState) {
//        super.onCreate(savedInstanceState);
//        setContentView(R.layout.activity_pdfviewer);
//
//        setToolbar();
//        findViews();
//        loadPdfFile();
//    }
//
//    private void loadPdfFile() {
//        if(getIntent().getExtras() != null) {
//            String pdfFileUrl = getIntent().getStringExtra("pdfFileUrl");
//            new RetrivePDFStream().execute(pdfFileUrl);
//        }
//    }
//
//    @Override
//    public boolean onOptionsItemSelected(MenuItem item) {
//        if (item.getItemId() == android.R.id.home) {
//            onBackPressed();
//            return true;
//        }
//        return false;
//    }
//
//    private void findViews() {
//        mPdfView = findViewById(R.id.pdfView);
//    }
//
//    private void setToolbar() {
//        Toolbar toolbar = findViewById(R.id.toolbar);
//        setSupportActionBar(toolbar);
//        getSupportActionBar().setTitle("Invoice");
//        getSupportActionBar().setDisplayHomeAsUpEnabled(true);
//        getSupportActionBar().setDisplayShowHomeEnabled(true);
//    }
//
//
//    private class RetrivePDFStream extends AsyncTask<String, Void, InputStream> {
//
//        @Override
//        protected void onPreExecute() {
//            super.onPreExecute();
//            showProgress();
//        }
//
//        @Override
//        protected InputStream doInBackground(String... strings) {
//            InputStream inputStream = null;
//            try {
//                URL uri = new URL(strings[0]);
//                HttpURLConnection urlConnection = (HttpURLConnection) uri.openConnection();
//                if (urlConnection.getResponseCode() == 200) {
//                    inputStream = new BufferedInputStream(urlConnection.getInputStream());
//                }
//            } catch (IOException e) {
//                return null;
//            }
//            return inputStream;
//        }
//
//        @Override
//        protected void onPostExecute(InputStream inputStream) {
//            super.onPostExecute(inputStream);
//            if(inputStream == null) {
//                Utils.toast("Unable to load invoice!");
//            } else {
//                mPdfView.fromStream(inputStream)
//                        //*.password("Your Password")*//* // use when the pdf file is password protected
//                        .load();
//                dismissProgress();
//            }
//        }
//    }
//
//    private void showProgress() {
//        progress = new ProgressDialog(this);
//        progress.setTitle(R.string.progress_title);
//        progress.setMessage("Please wait");
//        progress.setCanceledOnTouchOutside(false);
//        progress.show();
//    }
//
//    private void dismissProgress() {
//        if(progress != null) {
//            progress.dismiss();
//        }
//    }
//
//}
