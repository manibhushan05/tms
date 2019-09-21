package in.aaho.android.ownr;

import android.app.Dialog;
import android.content.Context;
import android.graphics.Paint;
import android.os.Bundle;
import android.text.TextUtils;
import android.view.View;
import android.view.Window;
import android.widget.Button;
import android.widget.TextView;

public class CustomInfoDialog extends Dialog implements
        android.view.View.OnClickListener {
    /*public Dialog d;*/
    public Button yes;
    private TextView tvMsg, tvToggle, tvMsgDetail;

    private String msg, msgDetail;

    public CustomInfoDialog(Context context, String msg, String msgDetail) {
        super(context);
        this.msg = msg;
        this.msgDetail = msgDetail;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        setContentView(R.layout.custom_info_dialog);
        yes = findViewById(R.id.btnOk);
        yes.setOnClickListener(this);
        tvToggle = findViewById(R.id.tvToggle);
        tvToggle.setOnClickListener(this);
        tvMsg = findViewById(R.id.tvMsg);
        tvMsgDetail = findViewById(R.id.tvMsgDetail);
        // Initially set detailed message as collapsed
        tvMsgDetail.setVisibility(View.GONE);

        // Set underline and color for toggle text
        tvToggle.setPaintFlags(tvToggle.getPaintFlags() | Paint.UNDERLINE_TEXT_FLAG);
        tvToggle.setTextColor(getContext().getResources().getColor(R.color.btn_primary_bg));

        // Set text
        tvMsg.setText(msg);
        tvMsgDetail.setText(msgDetail);

        if (TextUtils.isEmpty(msgDetail)) {
            tvToggle.setVisibility(View.GONE);
        } else {
            tvToggle.setVisibility(View.VISIBLE);
        }
    }

    @Override
    public void onClick(View v) {
        switch (v.getId()) {
            case R.id.btnOk:
                /*activity.finish();*/
                dismiss();
                break;
            case R.id.tvToggle:
                if (tvToggle.getVisibility() == View.VISIBLE) {
                    if (tvToggle.getText().toString().equalsIgnoreCase("Show more")) {
                        tvToggle.setText("Show less");
                        tvMsgDetail.setVisibility(View.VISIBLE);
                    } else {
                        tvToggle.setText("Show more");
                        tvMsgDetail.setVisibility(View.GONE);
                    }
                }
                break;
            default:
                break;
        }
    }
}
