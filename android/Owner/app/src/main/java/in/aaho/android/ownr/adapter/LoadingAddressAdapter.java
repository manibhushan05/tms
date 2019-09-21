package in.aaho.android.ownr.adapter;

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.data.AddressData;

/**
 * Created by mani on 3/8/16.
 */
public class LoadingAddressAdapter extends  RecyclerView.Adapter<LoadingAddressAdapter.MyViewHolder>{

    private List<AddressData> dataList;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        private TextView tvAddress;
        private TextView tvCity;

        public MyViewHolder(View view) {
            super(view);
            tvAddress = view.findViewById(R.id.tvLaddCity);
            tvCity = view.findViewById(R.id.tvLaddAddress);
        }
    }


    public LoadingAddressAdapter(List<AddressData> dataList) {
        this.dataList = dataList;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.loading_address_rows, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        AddressData addressData = dataList.get(position);
        holder.tvAddress.setText(addressData.getAddress());
        holder.tvCity.setText(addressData.getCity());
           }

    @Override
    public int getItemCount() {
        return dataList.size();
    }
}


