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

public class InTransitUpdateDialog extends Dialog implements
        View.OnClickListener {
    private Context mContext;
    private Spinner spinner;
    private Button btnUpdate;
    private ImageView imgSuggetions, imgClearComment, imgClearLocation;
    private TextInputEditText edComment, edLocation;
    private ArrayList<String> mStatusList;
    private String[] commentList = {
            "Waiting as Unloading point", "Unloading ongoing",
            "Delivered"
    };
    private IOnInTransitUpdateListener mIOnInTransitUpdateListener;
    private IOnInTransitLocationListener mIOnInTransitLocationListener;

    public interface IOnInTransitUpdateListener {
        void onInTransitUpdateClicked(String status, String comment);
    }

    public interface IOnInTransitLocationListener {
        void onInTransitLocationClicked(String location);
    }

    public InTransitUpdateDialog(Context context, ArrayList<String> statusList,
                                 IOnInTransitUpdateListener iOnInTransitUpdateListener,
                                 IOnInTransitLocationListener iOnInTransitLocationListener) {
        super(context);
        this.mContext = context;
        this.mStatusList = statusList;
        this.mIOnInTransitUpdateListener = iOnInTransitUpdateListener;
        this.mIOnInTransitLocationListener = iOnInTransitLocationListener;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        setContentView(R.layout.in_transit_update_dialog);
        findViews();
        setFocusChangedListener();
        setupData();
    }

    private void setFocusChangedListener() {
        edLocation.setOnFocusChangeListener(new View.OnFocusChangeListener() {
            @Override
            public void onFocusChange(View v, boolean hasFocus) {
                if (hasFocus) {
                    mIOnInTransitLocationListener.onInTransitLocationClicked(edLocation.getText().toString());
                }
            }
        });
    }

    private void setupData() {
        ArrayAdapter<String> adapter = new ArrayAdapter<>(mContext,
                android.R.layout.simple_spinner_item, mStatusList);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinner.setAdapter(adapter);

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
        edLocation.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                if (i == 0) {
                    imgClearLocation.setVisibility(View.INVISIBLE);
                }
                if (i2 > 0) {
                    imgClearLocation.setVisibility(View.VISIBLE);
                }
            }
        });
    }

    private void findViews() {
        spinner = findViewById(R.id.spinner);
        edComment = findViewById(R.id.edComment);
        edLocation = findViewById(R.id.edLocation);
        edLocation.setOnClickListener(this);
        btnUpdate = findViewById(R.id.btnUpdate);
        btnUpdate.setOnClickListener(this);
        imgSuggetions = findViewById(R.id.imgSuggetions);
        imgSuggetions.setOnClickListener(this);
        imgClearComment = findViewById(R.id.imgClearComment);
        imgClearComment.setOnClickListener(this);
        imgClearLocation = findViewById(R.id.imgClearLocation);
        imgClearLocation.setOnClickListener(this);
    }

    @Override
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.btnUpdate:
                if (isValidInputByUser()) {
                    mIOnInTransitUpdateListener.onInTransitUpdateClicked(
                            String.valueOf(spinner.getSelectedItem()),
                            edComment.getText().toString());
                    dismiss();
                }
                break;
            case R.id.imgSuggetions:
                showCommentSuggestionsListDialog();
                break;
            case R.id.imgClearComment:
                edComment.setText("");
                break;
            case R.id.imgClearLocation:
                edLocation.setText("");
                break;
            case R.id.edLocation:
                mIOnInTransitLocationListener.onInTransitLocationClicked(edLocation.getText().toString());
                break;
            default:
                break;
        }
    }

    /**
     * To check if user input is valid or not
     */
    private boolean isValidInputByUser() {
        // Check if spinner value has changed if yes return true
        // else  if comment entered return true
        // else if check if location entered return true
        // else false
        if (spinner.getSelectedItemPosition() == 0) {
            if (TextUtils.isEmpty(edComment.getText().toString())) {
                if (isValidInputLocation()) {
                    return true;
                } else {
                    Utils.toast("Please enter either comment or location!");
                    return false;
                }
            } else {
                return true;
            }
        } else {
            return true;
        }
    }

    /**
     * To check if user location input is valid or not
     */
    private boolean isValidInputLocation() {
        return !TextUtils.isEmpty(edLocation.getText().toString());
    }

    /**
     * Show comment suggestions list dialog to pick one of the suggestion as comment
     */
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

    /**
     * Set location
     */
    public void setLocationText(String text) {
        if (edLocation != null) {
            edLocation.setText(text);
        }
    }

    /**
     * Set focus of location
     */
    public void setLocationEditTextFocus(boolean hasFocus) {
        if (edLocation != null) {
            if (hasFocus) {
                edLocation.requestFocus();
            } else {
                edLocation.clearFocus();
            }
        }
    }
}
