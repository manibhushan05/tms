package in.aaho.android.driver.common;

import android.os.Bundle;
import android.support.v7.widget.DefaultItemAnimator;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.driver.Aaho;
import in.aaho.android.driver.R;
import in.aaho.android.driver.TermsDialogFragment;
import in.aaho.android.driver.otp.OTPDialogFragment;
import in.aaho.android.driver.requests.Api;
import in.aaho.android.driver.requests.EditDriverDetailsRequest;
import in.aaho.android.driver.requests.RegisterVehicleRequest;

/**
 * Created by shobhit on 8/8/16.
 */

public class LanguageSelectDialogFragment extends BaseDialogFragment {

    private Button cancelButton;
    private RecyclerView langContainer;
    private View dialogView;
    private LangAdapter langAdapter;

    private OnChangeListener listener;

    public static void showNewDialog(BaseActivity activity, OnChangeListener listener) {
        LanguageSelectDialogFragment fragment = new LanguageSelectDialogFragment();
        fragment.setActivity(activity);
        fragment.listener = listener;
        fragment.show(activity.getSupportFragmentManager(), "language_select_dialog");
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        dialogView = inflater.inflate(R.layout.language_dialog, container, false);

        setViewVariables();
        setSavedValues();
        setupAdapters();
        setClickListeners();

        return dialogView;
    }

    private void setupAdapters() {
        langAdapter = new LangAdapter(this, listener);
        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getActivity().getApplicationContext());
        langContainer.setLayoutManager(mLayoutManager);
        langContainer.setItemAnimator(new DefaultItemAnimator());
        langContainer.setAdapter(langAdapter);

        langAdapter.notifyDataSetChanged();
    }

    private void setClickListeners() {
        cancelButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dismiss();
            }
        });
    }

    private void setViewVariables() {
        cancelButton = (Button) dialogView.findViewById(R.id.cancel_btn);
        langContainer = (RecyclerView) dialogView.findViewById(R.id.language_container);
    }

    public void setSavedValues() {

    }

    public interface OnChangeListener {
        void onChange();
    }


}