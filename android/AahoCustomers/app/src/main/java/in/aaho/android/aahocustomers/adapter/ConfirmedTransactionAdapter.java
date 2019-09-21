package in.aaho.android.aahocustomers.adapter;

import android.app.Activity;
import android.app.ProgressDialog;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.os.SystemClock;
import android.support.v7.widget.RecyclerView;
import android.text.TextUtils;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.RelativeLayout;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

import in.aaho.android.aahocustomers.ObjectFileUtil;
import in.aaho.android.aahocustomers.POD_DOCS;
import in.aaho.android.aahocustomers.PathMapActivity;
import in.aaho.android.aahocustomers.R;
import in.aaho.android.aahocustomers.UploadActivity;
import in.aaho.android.aahocustomers.ViewPODActivity;
import in.aaho.android.aahocustomers.common.ApiResponseListener;
import in.aaho.android.aahocustomers.common.BaseActivity;
import in.aaho.android.aahocustomers.common.MainApplication;
import in.aaho.android.aahocustomers.common.Utils;
import in.aaho.android.aahocustomers.data.ConfirmedTransactionData;
import in.aaho.android.aahocustomers.map.TrackSelectListener;
import in.aaho.android.aahocustomers.transaction.PODPendingFragment;
import in.aaho.android.aahocustomers.transaction.TransactionActivity;
import in.aaho.android.aahocustomers.transaction.TripDetailsActivity;
import in.aaho.android.aahocustomers.requests.VehiclePathDataRequest;
/**
 * Created by mani on 21/7/16.
 */
public class ConfirmedTransactionAdapter extends RecyclerView.Adapter<ConfirmedTransactionAdapter.MyViewHolder> {
    private final Context context = null;
    private Activity activity;
    public List<ConfirmedTransactionData> mDataList,filteredList;
    private PODPendingFragment.IOnUploadPodClickedListener iOnViewPodClickedListener;

    private ProgressDialog progress;
    private static JSONObject jsonVehiclePathData;

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
//        private TextView tvTotalAmount;
//        private TextView tvBalance;
//        private TextView tvPaid;
        private TextView tvTotalAmountL;
        private TextView tvBalanceL;
        private TextView tvPaidL;
        private TextView tvLastLocation;
        private TextView tvVehicleNumber;
        private TextView tvPOD;
        private TextView tvViewPOD;
        public LinearLayout item;
        private LinearLayout trackBtn;
        private LinearLayout last_location;

        public MyViewHolder(View view) {
            super(view);
//            item = (LinearLayout) view;
//            tvTransactionId = (TextView) view.findViewById(R.id.tvCnfTransactionID);
            trackBtn = view.findViewById(R.id.track_btn);
            tvPickUpFrom = view.findViewById(R.id.tvNumberOfBookingsValue);
            tvDropAt = view.findViewById(R.id.tvTotalAmountValue);
            tvShipmentDate = view.findViewById(R.id.tvCnfShipmentDate);
            tvLrNumber = view.findViewById(R.id.tvCnfLrNumber);
            tvLastLocation = view.findViewById(R.id.track_card_location_details_tv);
//            tvTotalAmount = view.findViewById(R.id.tvConfirmedAmount);
//            tvBalance = view.findViewById(R.id.tvConfirmedBalance);
//            tvPaid = view.findViewById(R.id.tvConfirmedPaid);
            tvVehicleNumber = view.findViewById(R.id.tvConfirmVehicleNumber);
            tvPOD = view.findViewById(R.id.tvPOD);
            tvViewPOD = view.findViewById(R.id.tvViewPOD);
            trackBtn = view.findViewById(R.id.track_btn);
            last_location = view.findViewById(R.id.last_location);
            RelativeLayout relativeLayout = view.findViewById(R.id.rlCnfMainContent);
            relativeLayout.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    Intent intent = new Intent(v.getContext(), TripDetailsActivity.class);
                    intent.putExtra("trans_id", trans_id);
                    v.getContext().startActivity(intent);
                }
            });

            tvViewPOD.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    // code to view uploaded POD
                    Intent intent = new Intent(view.getContext(), ViewPODActivity.class);
                    /*intent.putExtra("Pod_Docs_List",
                            filteredList.get(getAdapterPosition()).getPod_docsArrayList());*/

                    ObjectFileUtil<ArrayList<POD_DOCS>> objectFileUtil = new ObjectFileUtil<>(view.getContext(),
                            "PodDocList");
                    objectFileUtil.put(filteredList.get(getAdapterPosition()).getPod_docsArrayList());
                    activity.startActivity(intent);
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

//            tvTotalAmountL = view.findViewById(R.id.tvConfirmedAmountLabel);
//            tvBalanceL = view.findViewById(R.id.tvConfirmedBalanceLabel);
//            tvPaidL = view.findViewById(R.id.tvConfirmedPaidLabel);
//            tvTotalAmountL.setVisibility(View.GONE);
//            tvBalanceL.setVisibility(View.GONE);
//            tvPaidL.setVisibility(View.GONE);

            // Adding track button on vehicles
//            trackBtn.setOnClickListener(new TripHistoryClickListener());
            trackBtn.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    String vehicleNumber = String.valueOf(filteredList.get(getAdapterPosition()).getAllocatedVehicleId());
                    Log.e("Calling Api","Time = "+ SystemClock.currentThreadTimeMillis());
                    VehiclePathDataRequest appDataRequest = new VehiclePathDataRequest(
                            vehicleNumber, new VehiclePathDataResponseListener());
                    MainApplication.queueRequest(appDataRequest);
                    progress = new ProgressDialog(activity);
                    progress.setTitle(R.string.progress_title);
                    progress.setMessage("Waiting for server to respond...");
                    progress.show();
                }
            });
//            tvTrackCaption.setText("Trip Route");
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
//        holder.trans_id = confirmedTransactionData.getAllocatedVehicleId();
        holder.trans_id = confirmedTransactionData.getTransactionId();
        holder.tvPickUpFrom.setText(confirmedTransactionData.getpickupFrom());
        holder.tvDropAt.setText(confirmedTransactionData.getdropAt());
        holder.tvShipmentDate.setText(confirmedTransactionData.getShipmentDate());
        // do not show if lr number if lr number is broker
        holder.tvLrNumber.setText(confirmedTransactionData.getLrNumber()
                .startsWith("BROKER")?"-":confirmedTransactionData.getLrNumber());
//        holder.tvTotalAmount.setText(confirmedTransactionData.getTotalAmount());
//        holder.tvBalance.setText(confirmedTransactionData.getBalance());
//        holder.tvPaid.setText(confirmedTransactionData.getPaid());
        holder.tvVehicleNumber.setText(confirmedTransactionData.getVehicleNumber());
        holder.tvLastLocation.setText(confirmedTransactionData.getLastLocation());
        // making financial details non visible to customer
//        holder.tvTotalAmount.setVisibility(View.GONE);
//        holder.tvBalance.setVisibility(View.GONE);
//        holder.tvPaid.setVisibility(View.GONE);


        String podStatus = confirmedTransactionData.getPodStatus();
        if(podStatus.equalsIgnoreCase(in.aaho.android.aahocustomers.parser.BookingDataParser.POD_PENDING)) {
            // Allow user to upload pod
            // Making POD non visible for customer
            holder.tvPOD.setVisibility(View.GONE);
            holder.tvViewPOD.setVisibility(View.GONE);
        } else if(podStatus.equalsIgnoreCase(in.aaho.android.aahocustomers.parser.BookingDataParser.POD_UNVERIFIED)) {
            // Allow user to upload pod
            holder.tvPOD.setVisibility(View.GONE);
            holder.tvViewPOD.setVisibility(View.GONE);
        } else if(podStatus.equalsIgnoreCase(in.aaho.android.aahocustomers.parser.BookingDataParser.POD_DELIVERED)) {
            // Don't allow user to upload pod
            holder.tvPOD.setVisibility(View.GONE);
            // Allow user to view POD which was uploaded
            holder.tvViewPOD.setVisibility(View.VISIBLE);
            holder.last_location.setVisibility(View.GONE);
            holder.trackBtn.setVisibility(View.GONE);
        } else {
            // No way to come here
            holder.tvPOD.setVisibility(View.GONE);
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

    // Do Search...
    public ConfirmedTransactionAdapter filterQ(final String text) {
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
        return this;
    }


    private class TripHistoryClickListener implements View.OnClickListener {

        @Override
        public void onClick(View v) {
//            loadVehiclePathDataFromServer();
            String vehicleNumber = String.valueOf(1717);
            Log.e("Calling Api","Time = "+ SystemClock.currentThreadTimeMillis());
            VehiclePathDataRequest appDataRequest = new VehiclePathDataRequest(
                    vehicleNumber, new VehiclePathDataResponseListener());
            MainApplication.queueRequest(appDataRequest);
//            queue(appDataRequest);
        }


    }

//    private void loadVehiclePathDataFromServer() {
//        String vehicleNumber = String.valueOf(selectedVehicleData.getVehicleId());
//        Log.e("Calling Api","Time = "+ SystemClock.currentThreadTimeMillis());
//        VehiclePathDataRequest appDataRequest = new VehiclePathDataRequest(
//                vehicleNumber, new VehiclePathDataResponseListener());
//        queue(appDataRequest);
//    }

    private class VehiclePathDataResponseListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
//            dismissProgress();
            progress.dismiss();
            String resp = response.toString();
            try {
                Log.e("Response Api","Time = "+ SystemClock.currentThreadTimeMillis());
                JSONObject jsonObject = new JSONObject(resp);
                jsonVehiclePathData = jsonObject.getJSONObject("data");
                if(jsonVehiclePathData == null) {
                    Toast.makeText(activity,
                            "No Trip Data available at this moment!", Toast.LENGTH_SHORT).show();
                } else {
                    JSONArray jsonArray = jsonVehiclePathData.getJSONArray("gps_data");
                    if(jsonArray == null || jsonArray.length() == 0) {
                        Toast.makeText(activity,
                                "No Trip Data available at this moment!", Toast.LENGTH_SHORT).show();
                    } else {
                        Intent intent = new Intent(activity, PathMapActivity.class);
                        intent.putExtra("vehicle_data", jsonVehiclePathData.toString());
                        activity.startActivity(intent);
                    }
                }

                //JSONArray jsonArray = jsonVehiclePathData.getJSONArray("gps_data");

                //JSONArray jsonArray = jsonObject.getJSONArray("data");


                /*if(jsonArray != null && jsonArray.length() > 0) {
                    ArrayList<VehicleGpsData> vehicleGpsDataArrayList = VehicleGpsData.getListFromJsonArray(jsonArray);
                    // write vehicleGpsData to file
                    ObjectFileUtil<ArrayList<VehicleGpsData>> objectFileUtil = new ObjectFileUtil<>(MapActivity.this,
                            "VehicleGpsData");
                    objectFileUtil.put(vehicleGpsDataArrayList);

                    Intent intent = new Intent(MapActivity.this, PathMapActivity.class);
                    //commented because list size is too large to pass in bundle
                    //intent.putExtra("VehicleGpsDataList",vehicleGpsDataArrayList);
                    MapActivity.this.startActivity(intent);
                } else {
                    Toast.makeText(MapActivity.this,
                            "No Trip Data available at this moment!", Toast.LENGTH_SHORT).show();
                }*/

            } catch (JSONException e) {
                e.printStackTrace();
                Utils.toast("error reading response data:\n" + resp);
            }
        }

//        @Override
//        public void onError() {
//            dismissProgress();
//        }
    }

    /** To get the vehicle gps data */
    public static JSONObject getJsonVehiclePathData() {
        return jsonVehiclePathData;
    }

}