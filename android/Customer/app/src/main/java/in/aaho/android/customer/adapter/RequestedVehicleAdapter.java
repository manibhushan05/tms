package in.aaho.android.customer.adapter;

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.customer.R;
import in.aaho.android.customer.data.RequestedVehicleData;

/**
 * Created by mani on 3/8/16.
 */
public class RequestedVehicleAdapter extends RecyclerView.Adapter<RequestedVehicleAdapter.MyViewHolder> {
    private List<RequestedVehicleData> dataList;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        private TextView tvTypeOfVehicle;
        private TextView tvNumberOfVehicle;

        public MyViewHolder(View view) {
            super(view);
            tvTypeOfVehicle = (TextView) view.findViewById(R.id.tvRvTypeOfVehicle);
            tvNumberOfVehicle = (TextView) view.findViewById(R.id.tvRvNumberOfTrucks);
        }
    }


    public RequestedVehicleAdapter(List<RequestedVehicleData> dataList) {
        this.dataList = dataList;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.requested_vehicle_info_rows, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        RequestedVehicleData requestedVehicleData = dataList.get(position);
        holder.tvTypeOfVehicle.setText(requestedVehicleData.getVehicleType());
        holder.tvNumberOfVehicle.setText(requestedVehicleData.getNumberOfVehicle());
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }
}
