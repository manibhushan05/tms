package in.aaho.android.employee.other;

import android.app.Dialog;
import android.content.Context;
import android.os.Bundle;
import android.support.design.widget.TextInputEditText;
import android.text.TextUtils;
import android.view.View;
import android.view.Window;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;


import in.aaho.android.employee.R;
import in.aaho.android.employee.common.EditTextWatcher;
import in.aaho.android.employee.common.Utils;

/**
 * Created by aaho on 27/02/19.
 */

public class CustomerPendingPaymentCommentsDialog extends Dialog implements
        View.OnClickListener {

    private Context mContext;
    private Integer smeId;
    private Button btnUpdate;
    private ImageView imgClearComment;
    private TextInputEditText edComment;
    private TextView tvComments;
    private String comments = "";

    private IOnCustomerPendingPaymentCommentUpdateListener mIOnCustomerPendingPaymentCommentUpdateListener;

    public interface IOnCustomerPendingPaymentCommentUpdateListener {
        void onCustomerPendingPaymentCommentUpdateClicked(Integer sme_id, String comment);
    }

    public CustomerPendingPaymentCommentsDialog(Context context, String comments, Integer sme_id,
                                                IOnCustomerPendingPaymentCommentUpdateListener iOnCustomerPendingPaymentCommentUpdateListener) {
        super(context);
        this.smeId = sme_id;
        this.mContext = context;
        this.comments = comments;
        this.mIOnCustomerPendingPaymentCommentUpdateListener = iOnCustomerPendingPaymentCommentUpdateListener;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        setContentView(R.layout.customer_pp_comment_update);
        findViews();
        setupData();
    }

    private void setupData() {

        if(this.comments.isEmpty()){
            tvComments.setText("No Comments Yet!");
        }else {
            tvComments.setText(this.comments);
        }
        edComment.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                if (i == 0) {
                    imgClearComment.setVisibility(View.INVISIBLE);
                }
                if (i2 > 0) {
                    imgClearComment.setVisibility(View.VISIBLE);
                }
            }
        });

    }

    private void findViews() {
        tvComments = findViewById(R.id.tvComments);
        edComment = findViewById(R.id.edComment);
        btnUpdate = findViewById(R.id.btnUpdate);
        btnUpdate.setOnClickListener(this);
        imgClearComment = findViewById(R.id.imgClearComment);
        imgClearComment.setOnClickListener(this);
    }
    @Override
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.btnUpdate:
                if (isValidInputByUser()) {
                    mIOnCustomerPendingPaymentCommentUpdateListener.onCustomerPendingPaymentCommentUpdateClicked(smeId, edComment.getText().toString());
//                    Utils.toast("Update btn clicked:"+edComment.getText().toString());
                    dismiss();
                }
                break;
            case R.id.imgClearComment:
                edComment.setText("");
                break;
            default:
                break;
        }

    }

    /**
     * To check if user input is valid or not
     */
    private boolean isValidInputByUser() {
        // if comment entered return true
        // else false
        if (TextUtils.isEmpty(edComment.getText().toString())) {
            Utils.toast("Please enter comment!");
            return false;
        } else {
            return true;
        }
    }
}
