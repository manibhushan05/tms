package in.aaho.android.driver.tracking;

import android.os.Bundle;
import android.support.annotation.Nullable;
import android.support.v7.widget.DefaultItemAnimator;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;

import java.text.DateFormat;
import java.util.Date;
import java.util.LinkedList;

import in.aaho.android.driver.R;
import in.aaho.android.driver.common.BaseDialogFragment;

/**
 * Created by shobhit on 8/8/16.
 */

public class StatusDialog extends BaseDialogFragment {

    private static final int LIMIT = 100;
    private static final LinkedList<String> messages = new LinkedList<String>();

    private static StatusAdapter statusAdapter;

    private RecyclerView statusDialogContainer;
    private Button okButton;


    private View dialogView;

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        statusAdapter = new StatusAdapter(messages);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        dialogView = inflater.inflate(R.layout.status_dialog, container, false);

        setViewVariables();
        setClickListeners();
        setupAdapters();

        return dialogView;
    }

    private void setupAdapters() {
        setupStatusDialogAdapter();
    }

    private void setupStatusDialogAdapter() {
        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getActivity().getApplicationContext());
        statusDialogContainer.setLayoutManager(mLayoutManager);
        statusDialogContainer.setItemAnimator(new DefaultItemAnimator());
        statusDialogContainer.setAdapter(statusAdapter);

        statusAdapter.notifyDataSetChanged();
    }

    private void setClickListeners() {
        okButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                StatusDialog.this.dismiss();
            }
        });
    }

    private void setViewVariables() {
        statusDialogContainer = (RecyclerView) dialogView.findViewById(R.id.dialog_status_container);
        okButton = (Button) dialogView.findViewById(R.id.dialog_ok_btn);
    }

    private static void notifyAdapters() {
        if (statusAdapter != null) {
            statusAdapter.notifyDataSetChanged();
        }
    }

    public static void addMessage(String message) {
        Log.e("[StatusDialog]", message);
        DateFormat format = DateFormat.getTimeInstance(DateFormat.SHORT);
        message = format.format(new Date()) + " - " + message;
        messages.add(message);
        while (messages.size() > LIMIT) {
            messages.removeFirst();
        }
        notifyAdapters();
    }

    public static void clearMessages() {
        messages.clear();
        notifyAdapters();
    }

}