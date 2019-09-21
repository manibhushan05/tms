package in.aaho.android.driver.tracking;

/**
 * Created by shobhit on 6/8/16.
 */

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.List;


public class StatusAdapter extends RecyclerView.Adapter<StatusAdapter.MyViewHolder> {

    private List<String> statusList;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        public TextView status;

        public MyViewHolder(View view) {
            super(view);
            status = (TextView) view.findViewById(android.R.id.text1);
        }
    }

    public StatusAdapter(List<String> statusList) {
        this.statusList = statusList;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(android.R.layout.simple_list_item_1, parent, false);

        return new MyViewHolder(itemView);
    }


    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        String status = statusList.get(position);
        if (status != null) {
            holder.status.setText(status);
        }
    }

    @Override
    public int getItemCount() {
        return statusList.size();
    }

}
