package in.aaho.android.ownr.profile;

/**
 * Created by mani on 6/8/16.
 */

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import in.aaho.android.ownr.common.ListItemListerner;
import in.aaho.android.ownr.vehicles.AccountSelectDialogFragment;
import in.aaho.android.ownr.vehicles.BankAccount;


public class AccountProfileAdapter extends RecyclerView.Adapter<AccountProfileAdapter.MyViewHolder> {

    private ItemClickListener itemClickListener;
    private AccountSelectListener listener;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        public TextView name;

        public MyViewHolder(View view) {
            super(view);
            name = view.findViewById(android.R.id.text1);
            itemClickListener = new ItemClickListener();
            name.setOnClickListener(itemClickListener);
        }

        public void updateListenerPositions(int position) {
            itemClickListener.updatePosition(position);
        }
    }

    public AccountProfileAdapter(AccountSelectListener listener) {
        this.listener = listener;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(android.R.layout.simple_list_item_1, parent, false);

        return new MyViewHolder(itemView);
    }


    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        BankAccount account = BankAccount.accountList.get(position);
        holder.updateListenerPositions(position);
        holder.name.setText(account.title());
    }

    @Override
    public int getItemCount() {
        return BankAccount.accountList.size();
    }

    private class ItemClickListener extends ListItemListerner implements View.OnClickListener {

        @Override
        public void onClick(View v) {
            BankAccount account = BankAccount.accountList.get(position);
            if (listener != null) {
                listener.onSelect(account);
            }
        }
    }

    interface AccountSelectListener {
        void onSelect(BankAccount account);
    }
}
