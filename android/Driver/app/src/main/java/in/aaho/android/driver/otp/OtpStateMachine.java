package in.aaho.android.driver.otp;

import android.os.AsyncTask;
import android.os.Handler;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONObject;

import java.util.HashMap;
import java.util.Map;
import java.util.Timer;
import java.util.TimerTask;

import in.aaho.android.driver.Aaho;
import in.aaho.android.driver.R;
import in.aaho.android.driver.common.ApiResponseListener;
import in.aaho.android.driver.common.BaseActivity;
import in.aaho.android.driver.common.Utils;
import in.aaho.android.driver.requests.Api;
import in.aaho.android.driver.requests.SendOTPRequest;
import in.aaho.android.driver.requests.VerifyOTPRequest;

/**
 * Created by shobhit on 28/12/16.
 *
 * TODO:
 *
 * - make otp state machine thread safe
 * - make otp dialog non dismiss-able
 * - give enter manually option at waiting state
 * - registered/verified UI on driver activity
 *
 *
 * - on server-side run task to monitor devices with gps log gaps and send email report to admins
 * - send in-app notification to app in say 24 hrs
 * - send sms to the device, if still not responding in say 48 hrs
 * - consider taking some high priority action (like manually calling the driver)
 *   in case where the vehicle is not sending updates while on an active trip






 */

public class OtpStateMachine {
    private static final int SUCCESS = 10;
    private static final int ERROR = 11;

    private static final int RESEND = 12;
    private static final int REENTER = 13;
    private static final int CANCEL = 14;
    private static final int OTP_READY = 15;
    private static final int VERIFY_ERROR = 15;

    private State[] states = {
            new SendingState(),    // 0
            new WaitingState(),    // 1
            new VerifyingState(),  // 2
            new RetryState(),      // 3
            new EnterState(),      // 4
            new ErrorState(),      // 5
            new SuccessState(),    // 6
            new CancelState()      // 7
    };

    private final int[][] transitions = {
            {0, SUCCESS, 1}, {0, ERROR, 3},
            {1, OTP_READY, 2}, {1, ERROR, 4},
            {2, SUCCESS, 6}, {2, VERIFY_ERROR, 5},
            {3, RESEND, 0}, {3, CANCEL, 7},
            {4, RESEND, 0}, {4, CANCEL, 7}, {4, OTP_READY, 2},
            {5, RESEND, 0}, {5, CANCEL, 7}, {5, REENTER, 4}
    };
    private final Map<Integer, Map<Integer, Integer>> transitionMap = new HashMap<>();

    private int current = 0;

    private final OnChangeListener listener;
    private final OtpListener otpListener;
    private final SmsReceiver smsReceiver;
    private final BaseActivity activity;
    private final View view;
    private final String phoneNumber;
    private final OTPViewHolder holder;

    private String otp;

    public OtpStateMachine(BaseActivity activity, View view, String phoneNumber, OnChangeListener listener) {
        this.listener = listener;
        this.activity = activity;
        this.view = view;
        this.phoneNumber = phoneNumber;
        this.holder = new OTPViewHolder(view);
        this.otpListener = new SmsOtpListener();
        this.smsReceiver = SmsReceiver.getNew(activity, this.otpListener);
        // make transition map for fast transitions
        for (int[] trans : transitions) {
            int startState = trans[0];
            int action = trans[1];
            int endState = trans[2];
            if (transitionMap.containsKey(startState)) {
                transitionMap.get(startState).put(action, endState);
            } else {
                Map<Integer, Integer> tempMap = new HashMap<>();
                tempMap.put(action, endState);
                transitionMap.put(startState, tempMap);
            }
        }
    }

    public void activate() {
        states[current].activate();
    }

    public void msg(int action) {
        states[current].msg(action);
    }

    private void next(int action) {
        Integer nextState = getNextState(action);
        if (nextState == null) {
            return;
        }
        msg(action);
        current = nextState;
        holder.updateUI();
        activate();
    }

    private Integer getNextState(int action) {
        if (!transitionMap.containsKey(current)) {
            Log.e("[OTPStateMachine]", "Error: transitionMap does not contain state = " + current);
            return null;
        }
        Map<Integer, Integer> map = transitionMap.get(current);
        if (!map.containsKey(action)) {
            Log.e("[OTPStateMachine]", "Error: state = " + current + " has no transition for action = " + action);
            return null;
        }
        int nextState = map.get(action);
        return nextState;
    }

    public void unregister() {
        smsReceiver.unregister();
    }

    interface OnChangeListener {
        void onSuccess();
        void onCancel();
    }

    private class ResendClickListener implements View.OnClickListener {
        @Override
        public void onClick(View v) {
            next(RESEND);
        }
    }


    private class VerifyClickListener implements View.OnClickListener {
        @Override
        public void onClick(View v) {
            String manualOtp = holder.otpEditText.getText().toString().trim();
            if (Utils.not(manualOtp)) {
                holder.otpEditText.setError("OTP is blank");
                return;
            } else {
                otp = manualOtp;
                next(OTP_READY);
            }
        }
    }

    private class ReenterClickListener implements View.OnClickListener {
        @Override
        public void onClick(View v) {
            next(REENTER);
        }
    }

    private class CancelClickListener implements View.OnClickListener {
        @Override
        public void onClick(View v) {
            next(CANCEL);
        }
    }


    private class OTPViewHolder {
        public final ProgressBar progress;
        public final Button resend, verify, cancel, reenter;
        public final TextView otpText, statusText;
        public final EditText otpEditText;

        public OTPViewHolder(View view) {
            progress = (ProgressBar) view.findViewById(R.id.progress);
            resend = (Button) view.findViewById(R.id.resend_btn);
            verify = (Button) view.findViewById(R.id.verify_btn);
            cancel = (Button) view.findViewById(R.id.cancel_btn);
            reenter = (Button) view.findViewById(R.id.reenter_btn);
            otpText = (TextView) view.findViewById(R.id.otp_tv);
            statusText = (TextView) view.findViewById(R.id.status_tv);
            otpEditText = (EditText) view.findViewById(R.id.otp_edit_text);

            resend.setOnClickListener(new ResendClickListener());
            reenter.setOnClickListener(new ReenterClickListener());
            verify.setOnClickListener(new VerifyClickListener());
            cancel.setOnClickListener(new CancelClickListener());
        }

        public void updateUI() {
            State currState = states[current];
            progress.setVisibility(currState.progressVisible ? View.VISIBLE : View.GONE);
            resend.setVisibility(currState.resendVisible ? View.VISIBLE : View.GONE);
            verify.setVisibility(currState.verifyVisible ? View.VISIBLE : View.GONE);
            cancel.setVisibility(currState.cancelVisible ? View.VISIBLE : View.GONE);
            reenter.setVisibility(currState.reenterVisible ? View.VISIBLE : View.GONE);
            otpText.setVisibility(currState.otpVisible ? View.VISIBLE : View.GONE);
            otpEditText.setVisibility(currState.enterOtpVisible ? View.VISIBLE : View.GONE);
            statusText.setText(currState.status());
        }
    }

    public abstract class State {
        public final boolean progressVisible;
        public final boolean resendVisible;
        public final boolean reenterVisible;
        public final boolean verifyVisible;
        public final boolean cancelVisible;
        public final boolean otpVisible;
        public final boolean enterOtpVisible;

        public State(boolean progressVisible, boolean resendVisible, boolean reenterVisible,
                     boolean verifyVisible, boolean cancelVisible, boolean otpVisible,
                     boolean enterOtpVisible) {
            this.progressVisible = progressVisible;
            this.resendVisible = resendVisible;
            this.reenterVisible = reenterVisible;
            this.verifyVisible = verifyVisible;
            this.cancelVisible = cancelVisible;
            this.otpVisible = otpVisible;
            this.enterOtpVisible = enterOtpVisible;
        }

        public void msg(int action) {
            throw new RuntimeException();
        }

        public void activate() {
        }

        public abstract String status();
    }

    // sending state

    public class SendingState extends State {
        public SendingState() {
            super(true, false, false, false, false, false, false);
        }

        @Override
        public void msg(int action) {
            if (action == ERROR) {
                smsReceiver.unregister();
            }
        }

        @Override
        public void activate() {
            smsReceiver.register();
            makeOtpRequest();
        }

        @Override
        public String status() {
            return "Sending OTP message to " + phoneNumber + "...";
        }
    }

    private void makeOtpRequest() {
        SendOTPRequest request = new SendOTPRequest(null, new SendOTPListener());
        activity.queue(request, false);
    }


    private class SendOTPListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            try {
                Log.e("response", response + "    from server");
                if (response.getString("status").equals(Api.STATUS_SUCCESS)) {
                    Log.e("SUCCESS", Api.STATUS_SUCCESS);
                    next(SUCCESS);
                } else {
                    // TODO: implement retry in background
                    throw new AssertionError(response.toString());
                }
            } catch (Exception e) {
                next(ERROR);
                e.printStackTrace();
            }
        }

        @Override
        public void onError() {
            next(ERROR);
        }
    }

    // waiting state

    private class SmsOtpListener implements OtpListener {
        @Override
        public void otpReceived(String otp) {
            OtpStateMachine.this.otp = otp;
            next(OTP_READY);
        }
    }


    public class WaitingState extends State {
        private int startSeconds = 60;
        private int remainingSeconds = startSeconds;
        Handler countdownHandler = new Handler();
        Timer countdownTimer = new Timer();
        final Runnable doA;
        private boolean waiting = true;

        public WaitingState() {
            super(true, false, false, false, false, false, false);
            doA = new Runnable() {
                @Override
                public void run() {
                    if (!waiting) {
                        return;
                    }
                    if (remainingSeconds != 0) {
                        holder.statusText.setText(status());
                        remainingSeconds--;
                    } else {
                        next(ERROR);
                    }
                }
            };
        }

        @Override
        public void msg(int action) {
            waiting = false;
            smsReceiver.unregister();
        }

        @Override
        public void activate() {
            waiting = true;
            remainingSeconds = startSeconds;
            for (int i = 0; i <= startSeconds; i++) {
                if (!waiting) {
                    break;
                }
                TimerTask task = new TimerTask() {
                    @Override
                    public void run() {
                        countdownHandler.post(doA);
                    }
                };
                countdownTimer.schedule(task, i * 1000);
            }
        }

        @Override
        public String status() {
            return "Waiting for OTP message: " + remainingSeconds + " seconds remaining";
        }

    }

    // verifying state

    public class VerifyingState extends State {
        public VerifyingState() {
            super(true, false, false, false, false, true, false);
        }

        @Override
        public String status() {
            return "Verifying OTP Validity...";
        }

        @Override
        public void msg(int action) {

        }

        @Override
        public void activate() {
            makeOtpVerificationRequest();
        }
    }

    private void makeOtpVerificationRequest() {
        VerifyOTPRequest request = new VerifyOTPRequest(otp, new VerifyOTPListener());
        activity.queue(request, false);
    }


    private class VerifyOTPListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            try {
                Log.e("response", response + "    from server");
                if (response.getString("status").equals(Api.STATUS_SUCCESS)) {
                    Log.e("SUCCESS", Api.STATUS_SUCCESS);
                    next(SUCCESS);
                } else {
                    // TODO: implement retry in background
                    throw new AssertionError(response.toString());
                }
            } catch (Exception e) {
                next(VERIFY_ERROR);
                e.printStackTrace();
            }
        }

        @Override
        public void onError() {
            next(VERIFY_ERROR);
        }
    }

    // success state

    public class SuccessState extends State {
        public SuccessState() {
            super(false, false, false, false, false, true, false);
        }

        @Override
        public String status() {
            return "OTP Verification Complete";
        }

        @Override
        public void activate() {
            listener.onSuccess();
        }

    }

    // cancel state

    public class CancelState extends State {
        public CancelState() {
            super(false, false, false, false, false, false, false);
        }

        @Override
        public String status() {
            return "Canceled";
        }

        @Override
        public void activate() {
            listener.onCancel();
        }
    }

    // retry state

    public class RetryState extends State {
        public RetryState() {
            super(false, true, false, false, true, false, false);
        }

        @Override
        public String status() {
            return "Resend OTP message";
        }

        @Override
        public void msg(int action) {

        }
    }

    // enter state

    public class EnterState extends State {
        public EnterState() {
            super(false, true, false, true, true, false, true);
        }

        @Override
        public String status() {
            return "Enter OTP manually";
        }

        @Override
        public void msg(int action) {

        }
    }

    // error state

    public class ErrorState extends State {
        public ErrorState() {
            super(false, true, true, false, true, true, false);
        }

        @Override
        public String status() {
            return "Error Verifying OTP";
        }

        @Override
        public void msg(int action) {

        }

    }
}
