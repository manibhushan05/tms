package in.aaho.android.employee.loads;

/**
 * Created by mani on 6/8/16.
 */

import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.support.v4.content.ContextCompat;
import android.support.v7.widget.CardView;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.employee.R;
import in.aaho.android.employee.RequirementActivity;
import in.aaho.android.employee.activity.PendingLRActivity;
import in.aaho.android.employee.activity.RequirementQuoteActivity;
import in.aaho.android.employee.common.BaseActivity;
import in.aaho.android.employee.common.Utils;


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
                    // If role is sales then open for edit
                    // else if role is traffic open req quote activity
                    String status = "";
                    if(view.getContext() instanceof AvailableLoadsActivity){
                        status = ((AvailableLoadsActivity)view.getContext()).getStatus();
                    }

                    if(status.equalsIgnoreCase("") ||
                            status.equalsIgnoreCase("unverified")) {
                        AvailableLoadRequest availableLoad = dataList.get(getAdapterPosition());
                        Bundle bundle = new Bundle();
                        bundle.putBoolean("isUpdate", true);
                        bundle.putString("id", String.valueOf(availableLoad.id));
                        bundle.putString("client", availableLoad.client);
                        bundle.putString("fromShipmentDate", availableLoad.fromShipmentDate != null ? availableLoad.fromShipmentDate.toString() : "");
                        bundle.putString("toShipmentDate", availableLoad.toShipmentDate != null && !availableLoad.toShipmentDate.equalsIgnoreCase("None") ? availableLoad.toShipmentDate.toString() : null);
                        bundle.putString("fromCity", availableLoad.fromCity);
                        bundle.putString("toCity", availableLoad.toCity);
                        bundle.putString("aahoOffice", availableLoad.aahoOffice);
                        bundle.putString("tonnage", String.valueOf(availableLoad.tonnage != null ? availableLoad.tonnage : ""));
                        bundle.putString("noOfVehicles", String.valueOf(availableLoad.noOfVehicles != null ? availableLoad.noOfVehicles : ""));
                        bundle.putString("material", String.valueOf(availableLoad.material));
                        bundle.putString("typeOfVehicle", String.valueOf(availableLoad.typeOfVehicle));
                        bundle.putString("rate", String.valueOf(availableLoad.rate != null ? availableLoad.rate : ""));
                        bundle.putString("fromCityId", String.valueOf(availableLoad.fromCityId != null ? availableLoad.fromCityId : ""));
                        bundle.putString("toCityId", String.valueOf(availableLoad.toCityId != null ? availableLoad.toCityId : ""));
                        bundle.putString("typeOfVehicleId", String.valueOf(availableLoad.typeOfVehicleId != null ? availableLoad.typeOfVehicleId : ""));
                        bundle.putString("clientId", String.valueOf(availableLoad.clientId != null ? availableLoad.clientId : ""));
                        bundle.putString("officeId", String.valueOf(availableLoad.officeId != null ? availableLoad.officeId : ""));
                        bundle.putString("reqStatus", availableLoad.reqStatus);
                        bundle.putBoolean("rdOnlyStatus", availableLoad.rdOnlyStatus);
                        bundle.putString("context", "CustomerLoads");
                        bundle.putString("remark", availableLoad.remark);
                        bundle.putString("cancelReason", availableLoad.cancelReason);
                        bundle.putString("toolbarName","Inquiry No "+availableLoad.id);

                        Intent intent = new Intent(activity, RequirementActivity.class);
                        intent.putExtras(bundle);
                        activity.startActivity(intent);
                    } else {
                        Intent intent = new Intent(activity, RequirementQuoteActivity.class);
                        AvailableLoadRequest availableLoad = dataList.get(getAdapterPosition());
                        Bundle bundle = new Bundle();
                        bundle.putString("reqId", String.valueOf(availableLoad.id));
                        intent.putExtras(bundle);
                        activity.startActivity(intent);
                    }
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
        if(noOfVehicle == null || noOfVehicle.equalsIgnoreCase("null")) {
            noOfVehicle = "-";
        }
        holder.tvNoOfVehicles.setText(noOfVehicle);

        // set tonnage field
        String tonnage = String.valueOf(vehicleRequest.tonnage);
        if(tonnage == null || tonnage.equalsIgnoreCase("null")) {
            tonnage = "-";
        }
        holder.tvTonnage.setText(tonnage);

        // set vehicle field
        String typeOfVehicle = String.valueOf(vehicleRequest.typeOfVehicle);
        if(typeOfVehicle == null || typeOfVehicle.equalsIgnoreCase("")) {
            typeOfVehicle = "-";
        }
        holder.vehicleTypeTv.setText(typeOfVehicle);


        holder.tvMaterial.setText(Utils.def(vehicleRequest.material, ""));

        // set no of vehicle field
        String rate = String.valueOf(vehicleRequest.rate);
        if(rate == null || rate.equalsIgnoreCase("null")) {
            rate = "-";
        }
        holder.tvPrice.setText(rate);

        holder.fromStateTv.setText(Utils.def(vehicleRequest.fromState, ""));
        holder.toStateTv.setText(Utils.def(vehicleRequest.toState, ""));

        String req_status = Utils.def(vehicleRequest.reqStatus, "");
        if(req_status.equalsIgnoreCase("fulfilled")) {
            holder.cardView.setCardBackgroundColor(
                    ContextCompat.getColor(activity,R.color.colorLightGreen));
        } else if(req_status.equalsIgnoreCase("cancelled")) {
            holder.cardView.setCardBackgroundColor(
                    ContextCompat.getColor(activity,R.color.colorLightRed));
        } else if(req_status.equalsIgnoreCase("lapsed")) {
            holder.cardView.setCardBackgroundColor(
                    ContextCompat.getColor(activity,R.color.colorLightGray));
        } else if(req_status.equalsIgnoreCase("unverified")) {
            holder.cardView.setCardBackgroundColor(
                    ContextCompat.getColor(activity,R.color.colorLightYellow));
        } else if(req_status.equalsIgnoreCase("open")) {
            holder.cardView.setCardBackgroundColor(Color.WHITE);
        } else {
            holder.cardView.setCardBackgroundColor(Color.WHITE);
        }

        ((AvailableLoadsActivity)activity).setMoveToTopVisibility(position);
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }


}
