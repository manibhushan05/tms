package in.aaho.android.ownr.adapter;

import android.support.v7.widget.RecyclerView;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;

import com.squareup.picasso.Callback;
import com.squareup.picasso.Picasso;

import java.util.ArrayList;

import in.aaho.android.ownr.PODListFragment;
import in.aaho.android.ownr.POD_DOCS;
import in.aaho.android.ownr.R;


public class PODListAdapter extends RecyclerView.Adapter<PODListAdapter.MyViewHolder> {

    private ArrayList<POD_DOCS> dataList;
    private PODListFragment.IOnListItemSelectionListener iOnListItemSelectionListener;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        private ImageView imageView;
        private TextView tvTitle;
        private ProgressBar progressBar;

        public MyViewHolder(View view) {
            super(view);
            imageView = view.findViewById(R.id.imageView);
            tvTitle = view.findViewById(R.id.tvTitle);
            progressBar = view.findViewById(R.id.progressBar);

            // click listener for imageview
            imageView.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    iOnListItemSelectionListener.onListItemSelected(dataList.get(getAdapterPosition()));
                }
            });
        }
    }

    public PODListAdapter(ArrayList<POD_DOCS> dataList,
                          PODListFragment.IOnListItemSelectionListener iOnListItemSelectionListener) {
        this.dataList = dataList;
        this.iOnListItemSelectionListener = iOnListItemSelectionListener;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.row_pod_list, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(final MyViewHolder holder, int position) {
        POD_DOCS pod_docs = dataList.get(position);
        holder.tvTitle.setText(pod_docs.getLr_number());
        Picasso.with(holder.imageView.getContext())
                .load(pod_docs.getUrl())
                .into(holder.imageView, new Callback() {
                    @Override
                    public void onSuccess() {
                        holder.progressBar.setVisibility(View.GONE);
                    }

                    @Override
                    public void onError() {
                        holder.progressBar.setVisibility(View.GONE);
                        Log.e("PODListAdapter","Failed to load image!");
                    }
                });
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }
}