package in.aaho.android.ownr.loads;

/**
 * Created by mani on 6/8/16.
 */

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.common.BaseActivity;
import in.aaho.android.ownr.common.Utils;


public class AvailbaleLoadsAdapter extends RecyclerView.Adapter<AvailbaleLoadsAdapter.MyViewHolder> {
    private final BaseActivity activity;
    private List<AvailableLoadRequest> dataList;

    public AvailbaleLoadsAdapter(BaseActivity activity, List<AvailableLoadRequest> availableLoadRequests) {
        this.activity = activity;
        this.dataList = availableLoadRequests;
    }


    public class MyViewHolder extends RecyclerView.ViewHolder {
        /*public TextView fromShipmentDateTv, toShipmentDateTv;*/
        public TextView fromCityTv, fromStateTv, toCityTv, toStateTv;
        public TextView tvNoOfVehicles,tvTonnage,vehicleTypeTv;
        public TextView tvMaterial,tvPrice;

        public MyViewHolder(View view) {
            super(view);
//            fromShipmentDateTv = view.findViewById(R.id.from_shipment_date_tv);
//            toShipmentDateTv = view.findViewById(R.id.to_shipment_date_tv);
            fromCityTv = view.findViewById(R.id.from_city_tv);
            fromStateTv = view.findViewById(R.id.from_state_tv);
            toCityTv = view.findViewById(R.id.to_city_tv);
            toStateTv = view.findViewById(R.id.to_state_tv);
            vehicleTypeTv = view.findViewById(R.id.vehicle_type_tv);
            tvNoOfVehicles = view.findViewById(R.id.tvNoOfVehicles);
            tvTonnage = view.findViewById(R.id.tvTonnage);
            tvMaterial = view.findViewById(R.id.tvMaterial);
            tvPrice = view.findViewById(R.id.tvPrice);
        }

    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.row_available_load, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        AvailableLoadRequest vehicleRequest = dataList.get(position);

        // NOTE: As discussed we are hiding 'from data' because showing date on toolbar
        /*String to_ship_date = String.valueOf(vehicleRequest.toShipmentDate);
        if(to_ship_date.equals("None")){
            holder.fromShipmentDateTv.setText(Utils.def(vehicleRequest.fromShipmentDate, ""));
        }else{
            holder.fromShipmentDateTv.setVisibility(View.GONE);
        }*/

        //holder.toShipmentDateTv.setText(Utils.def(vehicleRequest.toShipmentDate, ""));

        holder.fromCityTv.setText(Utils.def(vehicleRequest.fromCity, ""));
        holder.toCityTv.setText(Utils.def(vehicleRequest.toCity, ""));

        // set no of vehicle field
        String noOfVehicle = String.valueOf(vehicleRequest.noOfVehicles);
        if(noOfVehicle == null || noOfVehicle.equalsIgnoreCase("-1")) {
            noOfVehicle = "-";
        }
        holder.tvNoOfVehicles.setText(noOfVehicle);

        // set tonnage field
        String tonnage = String.valueOf(vehicleRequest.tonnage);
        if(tonnage == null || tonnage.equalsIgnoreCase("-1")) {
            tonnage = "-";
        }
        holder.tvTonnage.setText(tonnage);
        holder.vehicleTypeTv.setText(Utils.def(vehicleRequest.typeOfVehicle, ""));
        holder.tvMaterial.setText(Utils.def(vehicleRequest.material, ""));

        // set no of vehicle field
        String rate = String.valueOf(vehicleRequest.rate);
        if(rate == null || rate.equalsIgnoreCase("-1")) {
            rate = "-";
        }
        holder.tvPrice.setText(rate);
        holder.fromStateTv.setText(Utils.def(vehicleRequest.fromState, ""));
        holder.toStateTv.setText(Utils.def(vehicleRequest.toState, ""));
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }


}
