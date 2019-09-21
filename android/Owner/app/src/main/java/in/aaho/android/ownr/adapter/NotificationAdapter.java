package in.aaho.android.ownr.adapter;

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.ArrayList;

import in.aaho.android.ownr.Notification;
import in.aaho.android.ownr.R;

public class NotificationAdapter extends RecyclerView.Adapter<NotificationAdapter.MyViewHolder> {

    private ArrayList<Notification> mDatalist = new ArrayList<>();

    public NotificationAdapter(ArrayList<Notification> mDatalist) {
        this.mDatalist = mDatalist;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).
                inflate(R.layout.row_notification,parent,false);
        return new MyViewHolder(view);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        Notification notification = mDatalist.get(position);

        holder.tvTitle.setText(notification.getTitle());
        holder.tvDescription.setText(notification.getDescription());
    }

    @Override
    public int getItemCount() {
        return mDatalist.size();
    }

    protected class MyViewHolder extends RecyclerView.ViewHolder {

        private TextView tvTitle,tvDescription;

        public MyViewHolder(View itemView) {
            super(itemView);
            tvTitle = itemView.findViewById(R.id.tvTitle);
            tvDescription = itemView.findViewById(R.id.tvDescription);
        }
    }
}
