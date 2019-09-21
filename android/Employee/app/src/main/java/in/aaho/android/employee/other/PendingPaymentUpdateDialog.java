package in.aaho.android.employee.other;

import android.annotation.TargetApi;
import android.app.AlertDialog;
import android.app.Dialog;
import android.content.Context;
import android.content.DialogInterface;
import android.os.Build;
import android.os.Bundle;
import android.support.design.widget.TextInputEditText;
import android.text.TextUtils;
import android.view.View;
import android.view.Window;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.Spinner;

import java.util.ArrayList;

import in.aaho.android.employee.R;
import in.aaho.android.employee.common.EditTextWatcher;
import in.aaho.android.employee.common.Utils;

public class PendingPaymentUpdateDialog extends Dialog implements
        View.OnClickListener {
    private Context mContext;
    private Spinner spinner;
    private Button btnUpdate;
    private ImageView imgSuggetions,imgClearComment;
    private TextInputEditText edComment;
    private ArrayList<String> mStatusList;
    private String[] commentList =  {
            "Call after 7 days","Call after 15 days",
            "Call after 30 days","issues in billing"
    };
    private IOnStatusUpdateListener mIOnStatusUpdateListener;

    public interface IOnStatusUpdateListener {
        void onStatusUpdateListener(String status, String comment);
    }

    public PendingPaymentUpdateDialog(Context context, ArrayList<String> statusList,
                                      IOnStatusUpdateListener iOnStatusUpdateListener) {
        super(context);
        this.mContext = context;
        this.mStatusList = statusList;
        this.mIOnStatusUpdateListener = iOnStatusUpdateListener;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        setContentView(R.layout.status_update_dialog);
        findViews();
        setupData();
    }

    private void setupData() {
        ArrayAdapter<String> adapter = new ArrayAdapter<>(mContext,
                android.R.layout.simple_spinner_item, mStatusList);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinner.setAdapter(adapter);

        edComment.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                if(i == 0) {
                    //mRateTextInputLayout.setError(null);
                    imgClearComment.setVisibility(View.INVISIBLE);
                }
                if(i2 > 0) {
                    imgClearComment.setVisibility(View.VISIBLE);
                }
            }
        });
    }

    private void findViews() {
        spinner = findViewById(R.id.spinner);
        edComment = findViewById(R.id.edComment);
        btnUpdate = findViewById(R.id.btnUpdate);
        btnUpdate.setOnClickListener(this);
        imgSuggetions = findViewById(R.id.imgSuggetions);
        imgSuggetions.setOnClickListener(this);
        imgClearComment = findViewById(R.id.imgClearComment);
        imgClearComment.setOnClickListener(this);
    }

    @Override
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.btnUpdate:
                if(isValidInputByUser()) {
                    mIOnStatusUpdateListener.onStatusUpdateListener(
                            String.valueOf(spinner.getSelectedItem()),
                            edComment.getText().toString().trim());
                    dismiss();
                }
                break;
            case R.id.imgSuggetions:
                showCommentSuggestionsListDialog();
                break;
            case R.id.imgClearComment:
                edComment.setText("");
                break;
            default:
                break;
        }
    }

    /** To check if user input is valid or not */
    private boolean isValidInputByUser() {
        if(TextUtils.isEmpty(edComment.getText().toString().trim())) {
            if(spinner.getSelectedItemPosition() == 0) {
                Utils.toast("Comment can not be left blank!");
                return false;
            } else {
                return true;
            }
        } else {
            return true;
        }
    }

    /** Show comment suggestions list dialog to pick one of the suggestion as comment */
    @TargetApi(Build.VERSION_CODES.JELLY_BEAN_MR1)
    private void showCommentSuggestionsListDialog() {
        AlertDialog.Builder alertbox = new AlertDialog.Builder(mContext);
        alertbox.setTitle("Pick one suggestions for comment")
                .setItems(commentList, new OnClickListener() {
                    public void onClick(DialogInterface dialog, int pos) {
                        //pos will give the selected item position
                        edComment.setText(commentList[pos]);
                    }
                })
                .setOnDismissListener(new OnDismissListener() {
                    @Override
                    public void onDismiss(DialogInterface dialogInterface) {

                    }
                });
        alertbox.show();
    }
}
