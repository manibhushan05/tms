package in.aaho.android.ownr.vehicles;

/**
 * Created by shobhit on 6/8/16.
 */

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import in.aaho.android.ownr.common.ListItemListerner;


public class OwnerDialogAdapter extends RecyclerView.Adapter<OwnerDialogAdapter.MyViewHolder> {

    private OwnerSelectDialogFragment fragment;
    private OwnerSelectDialogFragment.OwnerChangeListener listener;

    private ItemClickListener itemClickListener;

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

    public OwnerDialogAdapter(OwnerSelectDialogFragment fragment, OwnerSelectDialogFragment.OwnerChangeListener listener) {
        this.fragment = fragment;
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
        VehicleOwner owner = VehicleOwner.ownerList.get(position);
        holder.updateListenerPositions(position);
        holder.name.setText(owner.title());
    }

    @Override
    public int getItemCount() {
        return VehicleOwner.ownerList.size();
    }

    private class ItemClickListener extends ListItemListerner implements View.OnClickListener {

        @Override
        public void onClick(View v) {
            VehicleOwner owner = VehicleOwner.ownerList.get(position);
            if (listener != null) {
                listener.onChange(owner);
            }
            if (fragment != null) {
                fragment.dismiss();
            }
        }
    }

}
