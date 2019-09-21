package in.aaho.android.employee.adapter;

import android.content.Context;
import android.support.v7.widget.RecyclerView;
import android.text.TextUtils;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.ArrayList;

import in.aaho.android.employee.R;
import in.aaho.android.employee.activity.NotificationActivity;
import in.aaho.android.employee.notification.MyNotification;

public class NotificationAdapter extends RecyclerView.Adapter<NotificationAdapter.MyViewHolder> {

    private Context mContext;
    private ArrayList<MyNotification> mDataList;

    public NotificationAdapter(Context context,ArrayList<MyNotification> mDataList) {
        this.mContext = context;
        this.mDataList = mDataList;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).
                inflate(R.layout.row_notification,parent,false);
        return new MyViewHolder(view);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        MyNotification notification = mDataList.get(position);

        String title = notification.title;
        if(TextUtils.isEmpty(notification.title)) {
            title = "-";
        }
        holder.tvTitle.setText(title);

        String body = notification.body;
        if(TextUtils.isEmpty(body)) {
            body = "-";
        }
        holder.tvDescription.setText(body);

        String receivedTime = notification.receivedTime;
        if(TextUtils.isEmpty(receivedTime)) {
            receivedTime = "-";
        }
        holder.tvReceivedTime.setText(receivedTime);

        // set move to top visibility
        ((NotificationActivity)mContext).setMoveToTopVisibility(position);
    }

    @Override
    public int getItemCount() {
        return mDataList.size();
    }

    protected class MyViewHolder extends RecyclerView.ViewHolder {

        private TextView tvTitle,tvDescription,tvReceivedTime;

        public MyViewHolder(View itemView) {
            super(itemView);
            tvTitle = itemView.findViewById(R.id.tvTitle);
            tvDescription = itemView.findViewById(R.id.tvDescription);
            tvReceivedTime = itemView.findViewById(R.id.tvReceivedTime);
        }
    }
}
