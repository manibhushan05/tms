package in.aaho.android.ownr.adapter;

import android.content.DialogInterface;
import android.support.v7.app.AlertDialog;
import android.support.v7.widget.RecyclerView;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.RelativeLayout;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.data.PendingTransactionData;
import in.aaho.android.ownr.requests.Api;
import in.aaho.android.ownr.requests.CancelTransactionRequest;
import in.aaho.android.ownr.requests.VendorResponseRequest;

/**
 * Created by mani on 21/7/16.
 */
public class PendingTransactionsAdapter extends RecyclerView.Adapter<PendingTransactionsAdapter.MyViewHolder> {

    private List<PendingTransactionData> dataList;
    private static final String TAG = "AAHO";

    public class MyViewHolder extends RecyclerView.ViewHolder {
        public TextView tvTransactionId;
        public TextView tvpickupFrom;
        public TextView tvdropAt;
        public TextView tvShipmentDate;
        public TextView tvNumberOfVehicle;
        public TextView tvMaterial;
        private Button btnNumberOfQuotes;
        private Button btnCancel;

        public MyViewHolder(View view) {
            super(view);
            tvTransactionId = view.findViewById(R.id.tvPendingTransactionID);
            tvpickupFrom = view.findViewById(R.id.tvNumberOfBookingsValue);
            tvdropAt = view.findViewById(R.id.tvTotalAmountValue);
            tvShipmentDate = view.findViewById(R.id.tvPendingShipmentDate);
            tvNumberOfVehicle = view.findViewById(R.id.tvPendingNumberOfTruck);
            btnNumberOfQuotes = view.findViewById(R.id.btnPendingViewQuotes);
//            tvMaterial = (TextView) view.findViewById(R.id.tvPendingMaterial);
            btnCancel = view.findViewById(R.id.btQRCancel);
            RelativeLayout relativeLayout = view.findViewById(R.id.rlPendingMainContent);
            relativeLayout.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
//                    CompleteTripDetails.getCompleteTripDetails(v, tvTransactionId.getText().toString());
                }
            });
            btnCancel.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    CancelTransactionRequest.cancelTransaction(v, tvTransactionId.getText().toString());
                }
            });
            btnNumberOfQuotes.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    int numberOfQuotation = Integer.parseInt(btnNumberOfQuotes.getText().toString().replaceAll("[\\D]", ""));
                    if (numberOfQuotation == 0) {
                        AlertDialog.Builder builder = new AlertDialog.Builder(v.getContext());
                        builder.setMessage("No Quotes Received")
                                .setPositiveButton("Ok", new DialogInterface.OnClickListener() {
                                    public void onClick(DialogInterface dialog, int id) {
                                        Log.e(Api.TAG, tvNumberOfVehicle.getText().toString());
                                    }
                                });
//                            .setNegativeButton("Dismiss",new DialogInterface.OnClickListener() {
//                                public void onClick(DialogInterface dialog, int id) {
//                                    // User cancelled the dialog
//                                }
//                            });
                        builder.create();
                        builder.show();
                    } else {
                        VendorResponseRequest.getResponseData(v, tvTransactionId.getText().toString());
                    }

                }
            });
        }
    }

    public PendingTransactionsAdapter(List<PendingTransactionData> dataList) {
        this.dataList = dataList;
    }


    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.pending_transaction_row, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        PendingTransactionData pendingTransactionData = dataList.get(position);
        holder.tvTransactionId.setText(pendingTransactionData.getTransactionId());
        holder.tvpickupFrom.setText(pendingTransactionData.getpickupFrom());
        holder.tvdropAt.setText(pendingTransactionData.getdropAt());
        holder.tvShipmentDate.setText(pendingTransactionData.getShipmentDate());
        holder.tvNumberOfVehicle.setText(pendingTransactionData.getNumberOfVehicle());
        holder.btnNumberOfQuotes.setText("View Responses (" + pendingTransactionData.getNumberOfQuotes() + ")");
//        holder.tvMaterial.setText(pendingTransactionData.getMaterial());
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }
}