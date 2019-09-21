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
import android.widget.TextView;

import in.aaho.android.aahocustomers.R;
import in.aaho.android.aahocustomers.common.BaseActivity;
import in.aaho.android.aahocustomers.common.BaseDialogFragment;

/**
 * Created by shobhit on 8/8/16.
 */

public class AccountSelectDialogFragment extends BaseDialogFragment {

    private RecyclerView accountDialogContainer;
    private Button addAccountBtn, cancelBtn;
    private View dialogView;

    private AccountChangeListener listener;

    private AccountDialogAdapter accountDialogAdapter;
    private TextView emptyView;

    public static void showNewDialog(BaseActivity activity, AccountChangeListener listener) {
        AccountSelectDialogFragment dialog = new AccountSelectDialogFragment();
        dialog.setChangeListener(listener);
        dialog.setActivity(activity);
        dialog.show(activity.getSupportFragmentManager(), "account_select_fragment");
    }

    public void setChangeListener(AccountChangeListener listener) {
        this.listener = listener;
    }

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        accountDialogAdapter = new AccountDialogAdapter(this, listener);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        dialogView = inflater.inflate(R.layout.vehicle_account_select_dialog, container, false);

        setViewVariables();
        setClickListeners();
        setupAdapters();

        if (BankAccount.accountList.size() == 0) {
            emptyView.setVisibility(View.VISIBLE);
        } else {
            emptyView.setVisibility(View.GONE);
        }

        return dialogView;
    }

    private void setupAdapters() {
        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getActivity().getApplicationContext());
        accountDialogContainer.setLayoutManager(mLayoutManager);
        accountDialogContainer.setItemAnimator(new DefaultItemAnimator());
        accountDialogContainer.setAdapter(accountDialogAdapter);

        accountDialogAdapter.notifyDataSetChanged();
    }

    private void setClickListeners() {
        addAccountBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                launchAddAccountDialog();
            }
        });
        cancelBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dismiss();
            }
        });
    }

    private void launchAddAccountDialog() {
        AccountAddDialogFragment.showNewDialog(getBaseActivity(), null, new AccountAddDialogFragment.AccountAddListener() {

            @Override
            public void onAccountAdd(BankAccount account) {
                if (account != null) {
                    BankAccount.accountList.add(account);
                    accountDialogAdapter.notifyDataSetChanged();
                }
            }
        });
    }

    private void setViewVariables() {
        accountDialogContainer = dialogView.findViewById(R.id.select_owner_dialog_container);
        addAccountBtn = dialogView.findViewById(R.id.select_owner_dialog_add_btn);
        cancelBtn = dialogView.findViewById(R.id.select_owner_dialog_cancel_btn);
        emptyView = dialogView.findViewById(R.id.empty_view);
    }

    public interface AccountChangeListener {
        void onChange(BankAccount bankAccount);
    }

}