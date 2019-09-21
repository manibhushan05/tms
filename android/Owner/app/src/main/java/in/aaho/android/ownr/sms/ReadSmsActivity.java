package in.aaho.android.ownr.sms;

import android.content.ContentResolver;
import android.database.Cursor;
import android.net.Uri;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;

import java.util.ArrayList;
import java.util.List;

import in.aaho.android.ownr.R;

public class ReadSmsActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_read_sms);
        Uri inboxURI = Uri.parse("content://sms/inbox");

        // List required columns
        String[] reqCols = new String[] { "_id", "address", "body" };

        // Get Content Resolver object, which will deal with Content Provider
        ContentResolver cr = getContentResolver();

        // Fetch Inbox SMS Message from Built-in Content Provider
        Cursor c = cr.query(inboxURI, reqCols, null, null, null);
        Log.e("SMS", String.valueOf(c));
    }
    public List<Sms> getAllSms(String folderName) {
        List<Sms> lstSms = new ArrayList<Sms>();
        Sms objSms = new Sms();
        Uri message = Uri.parse("content://sms/"+folderName);
        ContentResolver cr = getContentResolver();
        String[] reqCols = new String[] { "_id", "address", "body" };
        Cursor c = cr.query(message, reqCols, null, null, null);
        Log.e("SMS", String.valueOf(c));
//
////        Cursor c = cr.query(message, null, null, null, null);
//        ReadSmsActivity.startManagingCursor(c);
//        int totalSMS = c.getCount();
//
//        if (c.moveToFirst()) {
//            for (int i = 0; i < totalSMS; i++) {
//
//                objSms = new Sms();
//                objSms.setId(c.getString(c.getColumnIndexOrThrow("_id")));
//                objSms.setAddress(c.getString(c
//                        .getColumnIndexOrThrow("address")));
//                objSms.setMsg(c.getString(c.getColumnIndexOrThrow("body")));
//                objSms.setReadState(c.getString(c.getColumnIndex("read")));
//                objSms.setTime(c.getString(c.getColumnIndexOrThrow("date")));
//
//                lstSms.add(objSms);
//                c.moveToNext();
//            }
//        }
//        // else {
//        // throw new RuntimeException("You have no SMS in " + folderName);
//        // }
//        c.close();

        return lstSms;
    }
}
