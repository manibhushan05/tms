package in.aaho.android.ownr.adapter;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.support.v7.widget.RecyclerView;
import android.text.TextUtils;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.RelativeLayout;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.List;

import in.aaho.android.ownr.ObjectFileUtil;
import in.aaho.android.ownr.POD_DOCS;
import in.aaho.android.ownr.R;
import in.aaho.android.ownr.UploadActivity;
import in.aaho.android.ownr.VehicleGpsData;
import in.aaho.android.ownr.ViewPODActivity;
import in.aaho.android.ownr.common.Utils;
import in.aaho.android.ownr.data.ConfirmedTransactionData;
import in.aaho.android.ownr.map.MapActivity;
import in.aaho.android.ownr.transaction.PODPendingFragment;
import in.aaho.android.ownr.transaction.TripDetailsActivity;

/**
 * Created by mani on 21/7/16.
 */
public class ConfirmedTransactionAdapter extends RecyclerView.Adapter<ConfirmedTransactionAdapter.MyViewHolder> {
    private final Context context = null;
    private Activity activity;
    private List<ConfirmedTransactionData> mDataList,filteredList;
    private PODPendingFragment.IOnUploadPodClickedListener iOnViewPodClickedListener;

    public ConfirmedTransactionAdapter(Activity activity,
                                       List<ConfirmedTransactionData> dataList,
                                       PODPendingFragment.IOnUploadPodClickedListener iOnViewPodClickedListener) {
        this.activity = activity;
        this.filteredList = new ArrayList<ConfirmedTransactionData>();
        this.mDataList = dataList;
        // we copy the original list to the filter list and use it for setting row values
        this.filteredList.addAll(this.mDataList);
        this.iOnViewPodClickedListener = iOnViewPodClickedListener;
    }

    public class MyViewHolder extends RecyclerView.ViewHolder {
        private TextView tvTransactionId;
        String trans_id;
        private TextView tvPickUpFrom;
        private TextView tvDropAt;
        private TextView tvShipmentDate;
        private TextView tvLrNumber;
        private TextView tvTotalAmount;
        private TextView tvBalance;
        private TextView tvPaid;
        private TextView tvVehicleNumber;
        private TextView tvPOD;
        private TextView tvViewPOD;
        public LinearLayout item;

        public MyViewHolder(View view) {
            super(view);
//            item = (LinearLayout) view;
//            tvTransactionId = (TextView) view.findViewById(R.id.tvCnfTransactionID);
            tvPickUpFrom = view.findViewById(R.id.tvNumberOfBookingsValue);
            tvDropAt = view.findViewById(R.id.tvTotalAmountValue);
            tvShipmentDate = view.findViewById(R.id.tvCnfShipmentDate);
            tvLrNumber = view.findViewById(R.id.tvCnfLrNumber);
            tvTotalAmount = view.findViewById(R.id.tvConfirmedAmount);
            tvBalance = view.findViewById(R.id.tvConfirmedBalance);
            tvPaid = view.findViewById(R.id.tvConfirmedPaid);
            tvVehicleNumber = view.findViewById(R.id.tvConfirmVehicleNumber);
            tvPOD = view.findViewById(R.id.tvPOD);
            tvViewPOD = view.findViewById(R.id.tvViewPOD);
            RelativeLayout relativeLayout = view.findViewById(R.id.rlCnfMainContent);
            relativeLayout.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    Intent intent = new Intent(v.getContext(), TripDetailsActivity.class);
                    intent.putExtra("trans_id", filteredList.get(getAdapterPosition()).getId());
                    v.getContext().startActivity(intent);
                }
            });

            tvViewPOD.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {

                    if(filteredList.get(getAdapterPosition()).getPod_docsArrayList() != null &&
                            filteredList.get(getAdapterPosition()).getPod_docsArrayList().size() > 0) {
                        // code to view uploaded POD
                        Intent intent = new Intent(view.getContext(), ViewPODActivity.class);
                    /*intent.putExtra("Pod_Docs_List",
                            filteredList.get(getAdapterPosition()).getPod_docsArrayList());*/

                        ObjectFileUtil<ArrayList<POD_DOCS>> objectFileUtil = new ObjectFileUtil<>(view.getContext(),
                                "PodDocList");
                        objectFileUtil.put(filteredList.get(getAdapterPosition()).getPod_docsArrayList());
                        activity.startActivity(intent);
                    } else {
                        Utils.toast("No POD available to display!");
                    }
                }
            });

            tvPOD.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    if(iOnViewPodClickedListener == null) {
                        Intent intent = new Intent(view.getContext(), UploadActivity.class);
                        Bundle bundle = new Bundle();
                        bundle.putString("LR_LIST",filteredList.get(getAdapterPosition()).getLrNumber());
                        bundle.putString("vehicle_no",filteredList.get(getAdapterPosition()).getVehicleNumber());
                        bundle.putString("booking_id",filteredList.get(getAdapterPosition()).getBookingId());
                        intent.putExtras(bundle);
                        activity.startActivity(intent);
                    } else {
                        iOnViewPodClickedListener.onUploadPodClicked(
                                filteredList.get(getAdapterPosition()));
                    }
                }
            });
        }
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.confirmed_transaction_rows, parent, false);
        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        ConfirmedTransactionData confirmedTransactionData = filteredList.get(position);
        holder.trans_id = confirmedTransactionData.getAllocatedVehicleId();
        holder.tvPickUpFrom.setText(confirmedTransactionData.getpickupFrom());
        holder.tvDropAt.setText(confirmedTransactionData.getdropAt());
        holder.tvShipmentDate.setText(confirmedTransactionData.getShipmentDate());
        /*// do not show if lr number if lr number is broker
        holder.tvLrNumber.setText(confirmedTransactionData.getLrNumber()
                .startsWith("BROKER")?"-":confirmedTransactionData.getLrNumber());*/
        String lrNumber = confirmedTransactionData.getLrNumber();
        if(TextUtils.isEmpty(lrNumber)) {
            lrNumber = confirmedTransactionData.getBookingId();
        }
        holder.tvLrNumber.setText(lrNumber);


        holder.tvTotalAmount.setText(confirmedTransactionData.getTotalAmount());
        holder.tvBalance.setText(confirmedTransactionData.getBalance());
        holder.tvPaid.setText(confirmedTransactionData.getPaid());
        holder.tvVehicleNumber.setText(confirmedTransactionData.getVehicleNumber());

        String podStatus = confirmedTransactionData.getPodStatus();
        if(podStatus.equalsIgnoreCase(in.aaho.android.ownr.parser.BookingDataParser.POD_PENDING)) {
            // Allow user to upload pod
            holder.tvPOD.setVisibility(View.VISIBLE);
            holder.tvViewPOD.setVisibility(View.GONE);
        } else if(podStatus.equalsIgnoreCase(in.aaho.android.ownr.parser.BookingDataParser.POD_UNVERIFIED)) {
            // Allow user to upload pod
            holder.tvPOD.setVisibility(View.VISIBLE);
            holder.tvViewPOD.setVisibility(View.VISIBLE);
        } else if(podStatus.equalsIgnoreCase(in.aaho.android.ownr.parser.BookingDataParser.POD_DELIVERED)) {
            // Don't allow user to upload pod
            holder.tvPOD.setVisibility(View.GONE);
            // Allow user to view POD which was uploaded
            holder.tvViewPOD.setVisibility(View.VISIBLE);
        } else {
            // No way to come here
            holder.tvPOD.setVisibility(View.VISIBLE);
            holder.tvViewPOD.setVisibility(View.GONE);
        }
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
                    if (mDataList != null)
                        filteredList.addAll(mDataList);

                } else {
                    if (mDataList != null) {
                        // Iterate in the original List and add it to filter list...
                        for (ConfirmedTransactionData item : mDataList) {
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