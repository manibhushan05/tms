package in.aaho.android.loads.loads;

import android.content.Intent;
import android.graphics.Color;
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

/**
 * Created by aaho on 20/05/18.
 */


public class MyLoadsAdapter extends RecyclerView.Adapter<MyLoadsAdapter.MyViewHolder> {
    private final BaseActivity activity;
    private List<MyLoadRequest> dataList;

    public MyLoadsAdapter(BaseActivity activity, List<MyLoadRequest> myLoadRequests) {
        this.activity = activity;
        this.dataList = myLoadRequests;
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
                    MyLoadRequest myLoad = dataList.get(getAdapterPosition());
                    Bundle bundle = new Bundle();
                    bundle.putString("id",String.valueOf(myLoad.id));
                    bundle.putString("client",myLoad.client);
                    bundle.putString("fromShipmentDate",myLoad.fromShipmentDate!=null?myLoad.fromShipmentDate.toString():"");
                    bundle.putString("toShipmentDate",myLoad.toShipmentDate!=null && !myLoad.toShipmentDate.equalsIgnoreCase("None")?myLoad.toShipmentDate.toString():null);
                    bundle.putString("fromCity",myLoad.fromCity);
                    bundle.putString("toCity",myLoad.toCity);
                    bundle.putString("aahoOffice",myLoad.aahoOffice);
                    bundle.putString("tonnage",String.valueOf(myLoad.tonnage!=-1?myLoad.tonnage:""));
                    bundle.putString("noOfVehicles",String.valueOf(myLoad.noOfVehicles!=-1?myLoad.noOfVehicles:""));
                    bundle.putString("material",String.valueOf(myLoad.material));
                    bundle.putString("typeOfVehicle",String.valueOf(myLoad.typeOfVehicle));
                    bundle.putString("rate",String.valueOf(myLoad.rate!=-1?myLoad.rate:""));
                    bundle.putString("fromCityId",String.valueOf(myLoad.fromCityId!=-1?myLoad.fromCityId:""));
                    bundle.putString("toCityId",String.valueOf(myLoad.toCityId!=-1?myLoad.toCityId:""));
                    bundle.putString("typeOfVehicleId",String.valueOf(myLoad.typeOfVehicleId!=-1?myLoad.typeOfVehicleId:""));
                    bundle.putString("clientId",String.valueOf(myLoad.clientId!=-1?myLoad.clientId:""));
                    bundle.putString("officeId",String.valueOf(myLoad.officeId!=-1?myLoad.officeId:""));
                    bundle.putString("reqStatus",myLoad.reqStatus);
                    bundle.putBoolean("rdOnlyStatus",myLoad.rdOnlyStatus);
                    bundle.putString("context","MyLoads");
                    bundle.putString("remark",myLoad.remark);

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
        MyLoadRequest vehicleRequest = dataList.get(position);

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

        String req_status = Utils.def(vehicleRequest.reqStatus, "");
        if(req_status.equalsIgnoreCase("fulfilled") ||
                req_status.equalsIgnoreCase("cancelled") ||
                req_status.equalsIgnoreCase("lapsed")){
//            holder.cardView.setCardBackgroundColor(Color.GRAY);
        }
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }


}

