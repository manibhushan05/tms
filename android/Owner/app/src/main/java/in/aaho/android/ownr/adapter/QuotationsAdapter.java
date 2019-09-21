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
import in.aaho.android.ownr.data.QuotationsData;
import in.aaho.android.ownr.requests.Api;
import in.aaho.android.ownr.requests.CancelTransactionRequest;
//import in.aaho.android.ownr.requests.CompleteTripDetails;
import in.aaho.android.ownr.requests.VendorResponseRequest;

/**
 * Created by mani on 10/8/16.
 */
public class QuotationsAdapter extends RecyclerView.Adapter<QuotationsAdapter.MyViewHolder> {
    private List<QuotationsData> quotationsDataList;

    public QuotationsAdapter(List<QuotationsData> quotationsDataList) {
        this.quotationsDataList = quotationsDataList;
    }

    public class MyViewHolder extends RecyclerView.ViewHolder {
        private TextView tvTransactionID;
        private TextView tvPickupFrom;
        private TextView tvDropAt;
        private TextView tvNumberOfTrucks;
        private TextView tvShipmentDate;
        private Button btnNumberOfQuotes;
        private Button btnCancel;
        private RelativeLayout relativeLayoutMainContent;

        public MyViewHolder(View view) {
            super(view);
            tvTransactionID = view.findViewById(R.id.tvQuotationTransactionID);
            tvPickupFrom = view.findViewById(R.id.tvNumberOfBookingsValue);
            tvDropAt = view.findViewById(R.id.tvTotalAmountValue);
            tvNumberOfTrucks = view.findViewById(R.id.tvQuotationNumberOfTruck);
            tvShipmentDate = view.findViewById(R.id.tvQuotationShipmentDate);
            btnNumberOfQuotes = view.findViewById(R.id.btQuotationNumberOfQuotions);
            btnCancel = view.findViewById(R.id.btQuotationCancel);
            relativeLayoutMainContent = view.findViewById(R.id.rlQuotationMainContent);
            relativeLayoutMainContent.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
//                    CompleteTripDetails.getCompleteTripDetails(v, tvTransactionID.getText().toString());
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
                                        Log.e(Api.TAG, tvNumberOfTrucks.getText().toString());
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
                        VendorResponseRequest.getResponseData(v, tvTransactionID.getText().toString());
                    }

                }
            });
            btnCancel.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    Log.e("CAN", "CLICKED CANCLE");
                    CancelTransactionRequest.cancelTransaction(v, tvTransactionID.getText().toString());

                }
            });
        }

    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext()).inflate(R.layout.quotation_rows, parent, false);
        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        QuotationsData quotationsData = quotationsDataList.get(position);
        holder.tvTransactionID.setText(quotationsData.getTransactionId());
        holder.tvPickupFrom.setText(quotationsData.getPickUpFrom());
        holder.tvDropAt.setText(quotationsData.getDropAt());
        holder.tvNumberOfTrucks.setText(quotationsData.getNumberOfTruck());
        holder.tvShipmentDate.setText(quotationsData.getShipmentDate());
        holder.btnNumberOfQuotes.setText("View Responses (" + quotationsData.getNumberOfQuote() + ")");

    }

    @Override
    public int getItemCount() {
        return quotationsDataList.size();
    }
}
