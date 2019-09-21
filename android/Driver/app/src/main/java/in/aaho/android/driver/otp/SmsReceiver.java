package in.aaho.android.driver.otp;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Build;
import android.os.Bundle;
import android.provider.Telephony;
import android.telephony.SmsMessage;
import android.util.Log;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

import in.aaho.android.driver.common.BaseActivity;
import in.aaho.android.driver.common.Utils;

/**
 * Created by shobhit on 27/12/16.
 */

public class SmsReceiver extends BroadcastReceiver {
    private static final Pattern smsText = Pattern.compile("([0-9]+) is your OTP for Aaho Driver App phone number verification");

    private final IntentFilter intentFilter = new IntentFilter();
    private boolean registered = false;
    private OtpListener listener;
    private BaseActivity activity;
    private Context context;

    public static SmsReceiver getNew(BaseActivity activity, OtpListener otpListener) {
        SmsReceiver smsReceiver = new SmsReceiver();
        smsReceiver.listener = otpListener;
        smsReceiver.activity = activity;
        smsReceiver.context = activity.getApplicationContext();
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT) {
            smsReceiver.intentFilter.addAction(Telephony.Sms.Intents.SMS_RECEIVED_ACTION);
        }
        return smsReceiver;
    }

    public void register() {
        if (!registered) {
            context.registerReceiver(this, intentFilter);
            Log.e("[SmsReceiver]", "registered");
            registered = true;
        }
    }

    public void unregister() {
        if (registered) {
            context.unregisterReceiver(this);
            Log.e("[SmsReceiver]", "unregistered");
            registered = false;
        }
    }

    @Override
    public void onReceive(Context context, Intent intent) {
        Log.e("[SmsReceiver]", "onReceive");
        Bundle data  = intent.getExtras();
        Object[] pdus = (Object[]) data.get("pdus");

        if (pdus == null) {
            return;
        }

        for (Object pdu : pdus) {
            SmsMessage smsMessage = SmsMessage.createFromPdu((byte[]) pdu);

            String sender = smsMessage.getDisplayOriginatingAddress();
            String content = smsMessage.getMessageBody();
            Log.e("[SmsReceiver]", "msg = " + content);

            if (isAahoSms(sender)) {
                String otp = getOtp(content);
                Log.e("[SmsReceiver]", "otp = " + otp);
                if (!Utils.not(otp)) {
                    notifyListener(otp);
                    return;
                }
            }
        }
    }

    private void notifyListener(String otp) {
        if (listener != null) {
            listener.otpReceived(otp);
        }
    }

    private boolean isAahoSms(String sender) {
        return true;
    }

    private String getOtp(String content) {
        content = content.trim();
        Matcher match = smsText.matcher(content);
        return match.find() ? match.group(1) : null;
    }

}