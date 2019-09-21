package in.aaho.android.loads.loads;

/**
 * Created by mani on 6/8/16.
 */

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.widget.CardView;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.loads.R;
import in.aaho.android.loads.RequirementActivity;
import in.aaho.android.loads.common.BaseActivity;
import in.aaho.android.loads.common.Utils;


public class AvailbaleLoadsAdapter extends RecyclerView.Adapter<AvailbaleLoadsAdapter.MyViewHolder> {
    private final BaseActivity activity;
    private List<AvailableLoadRequest> dataList;

    public AvailbaleLoadsAdapter(BaseActivity activity, List<AvailableLoadRequest> availableLoadRequests) {
        this.activity = activity;
        this.dataList = availableLoadRequests;
    }


    public class MyViewHolder extends RecyclerView.ViewHolder {
        public TextView fromShipmentDataTv, fromCityTv, fromStateTv, toCityTv, toStateTv;
        public TextView tvNoOfVehicles,tvTonnage,vehicleTypeTv;
        public TextView tvMaterial,tvPrice;
        public CardView cardView;

        public MyViewHolder(View view) {
            super(view);
            fromShipmentDataTv = view.findViewById(R.id.from_shipment_date_tv);
            fromCityTv = view.findViewById(R.id.from_city_tv);
            fromStateTv = view.findViewById(R.id.from_state_tv);
            toCityTv = view.findViewById(R.id.to_city_tv);
            toStateTv = view.findViewById(R.id.to_state_tv);
            vehicleTypeTv = view.findViewById(R.id.vehicle_type_tv);
            tvNoOfVehicles = view.findViewById(R.id.tvNoOfVehicles);
            tvTonnage = view.findViewById(R.id.tvTonnage);
            tvMaterial = view.findViewById(R.id.tvMaterial);
            tvPrice = view.findViewById(R.id.tvPrice);
            cardView = view.findViewById(R.id.card_view);

            cardView.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    AvailableLoadRequest availableLoad = dataList.get(getAdapterPosition());
                    Bundle bundle = new Bundle();
                    bundle.putString("id",String.valueOf(availableLoad.id));
                    bundle.putString("client",availableLoad.client);
                    bundle.putString("fromShipmentDate",availableLoad.fromShipmentDate!=null?availableLoad.fromShipmentDate.toString():"");
                    bundle.putString("toShipmentDate",availableLoad.toShipmentDate!=null && !availableLoad.toShipmentDate.equalsIgnoreCase("None")?availableLoad.toShipmentDate.toString():null);
                    bundle.putString("fromCity",availableLoad.fromCity);
                    bundle.putString("toCity",availableLoad.toCity);
                    bundle.putString("aahoOffice",availableLoad.aahoOffice);
                    bundle.putString("tonnage",String.valueOf(availableLoad.tonnage!=-1?availableLoad.tonnage:""));
                    bundle.putString("noOfVehicles",String.valueOf(availableLoad.noOfVehicles!=-1?availableLoad.noOfVehicles:""));
                    bundle.putString("material",String.valueOf(availableLoad.material));
                    bundle.putString("typeOfVehicle",String.valueOf(availableLoad.typeOfVehicle));
                    bundle.putString("rate",String.valueOf(availableLoad.rate!=-1?availableLoad.rate:""));
                    bundle.putString("fromCityId",String.valueOf(availableLoad.fromCityId!=-1?availableLoad.fromCityId:""));
                    bundle.putString("toCityId",String.valueOf(availableLoad.toCityId!=-1?availableLoad.toCityId:""));
                    bundle.putString("typeOfVehicleId",String.valueOf(availableLoad.typeOfVehicleId!=-1?availableLoad.typeOfVehicleId:""));
                    bundle.putString("clientId",String.valueOf(availableLoad.clientId!=-1?availableLoad.clientId:""));
                    bundle.putString("officeId",String.valueOf(availableLoad.officeId!=-1?availableLoad.officeId:""));
                    bundle.putString("reqStatus",availableLoad.reqStatus);
                    bundle.putString("remark",availableLoad.remark);
                    bundle.putBoolean("rdOnlyStatus",availableLoad.rdOnlyStatus);
                    bundle.putString("context","CustomerLoads");

                    Intent intent = new Intent(activity, RequirementActivity.class);
                    intent.putExtras(bundle);
                    activity.startActivity(intent);
                }
            });
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

        holder.fromShipmentDataTv.setText(Utils.def(vehicleRequest.fromShipmentDate, ""));
        holder.fromCityTv.setText(Utils.def(vehicleRequest.fromCity, ""));
        holder.toCityTv.setText(Utils.def(vehicleRequest.toCity, ""));
        holder.fromStateTv.setText("");
        holder.toStateTv.setText("");
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
