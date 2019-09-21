package in.aaho.android.aahocustomers.vehicles;

import android.os.Bundle;
import android.support.annotation.Nullable;
import android.support.v7.widget.DefaultItemAnimator;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;

import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

import in.aaho.android.aahocustomers.R;
import in.aaho.android.aahocustomers.common.ApiResponseListener;
import in.aaho.android.aahocustomers.common.BaseActivity;
import in.aaho.android.aahocustomers.common.BaseDialogFragment;
import in.aaho.android.aahocustomers.common.Utils;
import in.aaho.android.aahocustomers.requests.SendDocumentEmailRequest;

/**
 * Created by shobhit on 8/8/16.
 */

public class DocEmailDialogFragment extends BaseDialogFragment {

    private Button doneButton, cancelButton;
    private EditText emailsEditText;
    private View dialogView;
    private long vehicleId;
    private RecyclerView docDetailsContainer;
    private DocEmailAdapter docEmailAdapter;
    private List<DocDetail> list;


    public static void showNewDialog(BaseActivity activity, long vehicleId, List<DocDetail> list) {
        DocEmailDialogFragment dialog = new DocEmailDialogFragment();
        dialog.setVehicleId(vehicleId);
        dialog.setDocList(list);
        dialog.setActivity(activity);
        dialog.show(activity.getSupportFragmentManager(), "doc_email_fragment");
    }

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        docEmailAdapter = new DocEmailAdapter(list);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        dialogView = inflater.inflate(R.layout.doc_email_dialog, container, false);

        setViewVariables();
        setClickListeners();
        setUpAdapters();

        return dialogView;
    }

    private void setUpAdapters() {
        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getActivity().getApplicationContext());
        docDetailsContainer.setLayoutManager(mLayoutManager);
        docDetailsContainer.setItemAnimator(new DefaultItemAnimator());
        docDetailsContainer.setAdapter(docEmailAdapter);

        docEmailAdapter.notifyDataSetChanged();
    }

    private void setClickListeners() {
        doneButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String emailStr = emailsEditText.getText().toString().trim();
                List<String> emails = new ArrayList<>();
                String[] emailStrings = emailStr.split(",");
                for (String email : emailStrings) {
                    if (!Utils.not(email)) {
                        emails.add(email.trim());
                    }
                }

                if (emails.isEmpty()) {
                    emailsEditText.setText("");
                    emailsEditText.setError("No email id entered");
                    return;
                }

                List<String> excluded = getUncheckedDocs();
                if (list.size() == excluded.size()) {
                    toast("At least one document must be selected to send");
                    return;
                }

                makeDocEmailRequest(emails, excluded);
            }
        });
        cancelButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dismiss();
            }
        });
    }

    private void makeDocEmailRequest(List<String> emails, List<String> excluded) {

        SendDocumentEmailRequest request = new SendDocumentEmailRequest(
                vehicleId, emails, excluded, new DocEmailSendListener()
        );
        queue(request);
    }

    private List<String> getUncheckedDocs() {
        List<String> uncheckedTypeList = new ArrayList<>();
        for (DocDetail ddl : list) {
            if (!ddl.shouldSend()) {
                uncheckedTypeList.add(ddl.getType());
            }
        }
        return uncheckedTypeList;
    }

    private void setViewVariables() {
        doneButton = dialogView.findViewById(R.id.owner_add_dialog_add_btn);
        cancelButton = dialogView.findViewById(R.id.owner_add_dialog_cancel_btn);
        emailsEditText = dialogView.findViewById(R.id.emails_edittext);
        docDetailsContainer = dialogView.findViewById(R.id.doc_details_container);
    }

    public void setVehicleId(long vehicleId) {
        this.vehicleId = vehicleId;
    }

    public void setDocList(List<DocDetail> list) {
        this.list = list;
    }

    private class DocEmailSendListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            toast("Email Sent");
            dismiss();
        }

        @Override
        public void onError() {
            dismissProgress();
            dismiss();
        }
    }

}