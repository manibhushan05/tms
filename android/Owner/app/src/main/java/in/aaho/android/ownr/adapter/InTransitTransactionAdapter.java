package in.aaho.android.ownr.adapter;

import android.app.Activity;
import android.content.Intent;
import android.support.v7.widget.RecyclerView;
import android.text.TextUtils;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.RelativeLayout;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.List;

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.ViewPODActivity;
import in.aaho.android.ownr.common.Utils;
import in.aaho.android.ownr.data.InTransitTransactionData;
import in.aaho.android.ownr.transaction.TripDetailsActivity;

/**
 * Created by mani on 21/7/16.
 */
public class InTransitTransactionAdapter extends RecyclerView.Adapter<InTransitTransactionAdapter.MyViewHolder> {

    private Activity activity;
    private List<InTransitTransactionData> dataList,filteredList;

    public InTransitTransactionAdapter(Activity activity,
                                       List<InTransitTransactionData> dataList) {
        this.activity = activity;
        this.filteredList = new ArrayList<InTransitTransactionData>();
        this.dataList = dataList;
        // we copy the original list to the filter list and use it for setting row values
        this.filteredList.addAll(this.dataList);
    }

    public class MyViewHolder extends RecyclerView.ViewHolder {
        String trans_id;
        private TextView tvPickUpFrom;
        private TextView tvDropAt;
        private TextView tvShipmentDate;
        private TextView tvLrNumber;
        private TextView tvTotalAmount;
        private TextView tvBalance;
        private TextView tvPaid;
        private TextView tvVehicleNumber;
        private TextView tvViewPOD;

        public MyViewHolder(View view) {
            super(view);
//            tvTransactionId = (TextView) view.findViewById(R.id.tvInTransitTransactionId);
            tvPickUpFrom = view.findViewById(R.id.tvNumberOfBookingsValue);
            tvDropAt = view.findViewById(R.id.tvTotalAmountValue);
            tvShipmentDate = view.findViewById(R.id.tvInTransitShipmentDate);
            tvLrNumber = view.findViewById(R.id.tvInTransitLrNumbers);
            tvTotalAmount = view.findViewById(R.id.tvInTransitAmount);
            tvBalance = view.findViewById(R.id.tvInTransitBalance);
//            tvPaid = (TextView) view.findViewById(R.id.tvInTransitPaid);
            tvVehicleNumber = view.findViewById(R.id.tvConfirmVehicleNumber);
//            tvMaterial = (TextView) view.findViewById(R.id.tvInTransitMaterial);
            tvViewPOD = view.findViewById(R.id.tvViewPOD);
            RelativeLayout relativeLayout = view.findViewById(R.id.rlInTransitMainContent);
            relativeLayout.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    Intent intent = new Intent(v.getContext(), TripDetailsActivity.class);
                    intent.putExtra("trans_id", filteredList.get(getAdapterPosition()).getId());
                    /*intent.putExtra("trans_id", trans_id);*/
                    v.getContext().startActivity(intent);
//                    CompleteTripDetails.getCompleteTripDetails(v, tvTransactionId.getText().toString());
                }
            });

            tvViewPOD.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    if(filteredList.get(getAdapterPosition()).getPod_docsArrayList() != null &&
                            filteredList.get(getAdapterPosition()).getPod_docsArrayList().size() > 0) {
                        // code to view uploaded POD
                        Intent intent = new Intent(view.getContext(), ViewPODActivity.class);
                        intent.putExtra("Pod_Docs_List",
                                filteredList.get(getAdapterPosition()).getPod_docsArrayList());
                        activity.startActivity(intent);
                    } else {
                        Utils.toast("No POD available to display!");
                    }
                }
            });
        }
    }


    /*public InTransitTransactionAdapter(List<InTransitTransactionData> dataList) {
        this.dataList = dataList;
    }*/

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.intransit_transaction_rows, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        InTransitTransactionData inTransitTransactionData = filteredList.get(position);
//        holder.tvTransactionId.setText(inTransitTransactionData.getBookingId());
        holder.trans_id = inTransitTransactionData.getBookingId();
        holder.tvPickUpFrom.setText(inTransitTransactionData.getpickupFrom());
        holder.tvDropAt.setText(inTransitTransactionData.getdropAt());
        holder.tvShipmentDate.setText(inTransitTransactionData.getShipmentDate());
        // holder.tvLrNumber.setText(inTransitTransactionData.getLrNumber());
        /*// do not show if lr number if lr number is broker
        holder.tvLrNumber.setText(inTransitTransactionData.getLrNumber()
                .startsWith("BROKER")?"-":inTransitTransactionData.getLrNumber());*/
        String lrNumber = inTransitTransactionData.getLrNumber();
        if(TextUtils.isEmpty(lrNumber)) {
            lrNumber = inTransitTransactionData.getBookingId();
        }
        holder.tvLrNumber.setText(lrNumber);


        holder.tvTotalAmount.setText(inTransitTransactionData.getTotalAmount());
        String latestPayment = inTransitTransactionData.getLatestPaymentDate();
        if(TextUtils.isEmpty(latestPayment)) {
            latestPayment = "-";
        }
        holder.tvBalance.setText(latestPayment);
//        holder.tvPaid.setText(inTransitTransactionData.getPaid());
        holder.tvVehicleNumber.setText(inTransitTransactionData.getVehicleNumber());
//        holder.tvMaterial.setText(inTransitTransactionData.getMaterial());
    }

    @Override
    public int getItemCount() {
        return (null != filteredList ? filteredList.size() : 0);
//        return dataList.size();
    }

    // Do Search...
    public void filter(final String text) {

        // Searching could be complex..so we will dispatch it to a different thread...
        new Thread(new Runnable() {
            @Override
            public void run() {

                // Clear the filter list
                filteredList.clear();

                // If there is no search value, then add all original list items to filter list
                if (TextUtils.isEmpty(text)) {
                    if (dataList != null)
                        filteredList.addAll(dataList);

                } else {
                    if (dataList != null) {
                        // Iterate in the original List and add it to filter list...
                        for (InTransitTransactionData item : dataList) {
                            if (item.getdropAt().toLowerCase().contains(text.toLowerCase())
                                    || item.getLrNumber().toLowerCase().contains(text.toLowerCase())
                                    || item.getVehicleNumber().toLowerCase().contains(text.toLowerCase())) {
                                // Adding Matched items
                                filteredList.add(item);
                            }
                        }
                    }
                }

                // Set on UI Thread
                (activity).runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        // Notify the List that the DataSet has changed...
                        if (filteredList.size() == 0) {
                            //Utils.toast("No data found");
                        }
                        notifyDataSetChanged();
                    }
                });

            }
        }).start();

    }

}