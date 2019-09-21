package in.aaho.android.ownr.vehicles;

/**
 * Created by shobhit on 6/8/16.
 */

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.CheckBox;
import android.widget.CompoundButton;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.common.ListItemListerner;


public class DocEmailAdapter extends RecyclerView.Adapter<DocEmailAdapter.MyViewHolder> {

    private final List<DocDetail> list;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        public ItemCheckListener itemCheckListener;
        public TextView title, docId;
        public CheckBox send;

        public MyViewHolder(View view) {
            super(view);
            title = view.findViewById(R.id.doc_title_tv);
            docId = view.findViewById(R.id.doc_id_tv);
            send = view.findViewById(R.id.doc_send_check_box);

            itemCheckListener = new ItemCheckListener();
            send.setOnCheckedChangeListener(itemCheckListener);
        }

        public void updateListenerPositions(int position) {
            itemCheckListener.updatePosition(position);
        }
    }

    public DocEmailAdapter(List<DocDetail> list) {
        this.list = list;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.doc_detail_item, parent, false);

        return new MyViewHolder(itemView);
    }


    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        DocDetail detail = list.get(position);
        holder.updateListenerPositions(position);
        holder.title.setText(detail.getTitle());
        holder.docId.setText(detail.getDocId());
        holder.send.setChecked(detail.shouldSend());
    }

    @Override
    public int getItemCount() {
        return list.size();
    }

    private class ItemCheckListener extends ListItemListerner implements CompoundButton.OnCheckedChangeListener {
        @Override
        public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
            list.get(position).setSend(isChecked);
        }
    }

}
