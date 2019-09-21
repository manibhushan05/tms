package in.aaho.android.employee.adapter;

/**
 * Created by mani on 6/8/16.
 */

import android.support.v7.widget.CardView;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.employee.AvailableQuoteData;
import in.aaho.android.employee.R;
import in.aaho.android.employee.common.BaseActivity;
import in.aaho.android.employee.common.Utils;
import in.aaho.android.employee.loads.AvailableLoadRequest;


public class AvailableQuotesAdapter extends RecyclerView.Adapter<AvailableQuotesAdapter.MyViewHolder> {
    private final BaseActivity activity;
    private List<AvailableQuoteData> dataList;

    public AvailableQuotesAdapter(BaseActivity activity, List<AvailableQuoteData> availableQuoteData) {
        this.activity = activity;
        this.dataList = availableQuoteData;
    }


    public class MyViewHolder extends RecyclerView.ViewHolder {
        public TextView tvBidNo, tvTransporterName, tvNoOfVehicles,
                tvBidPrice, tvTonnage;
        public ImageView imgCall;
        public CardView cardView;

        public MyViewHolder(View view) {
            super(view);
            tvBidNo = view.findViewById(R.id.tvBidNo);
            tvTransporterName = view.findViewById(R.id.tvTransporterName);
            tvNoOfVehicles = view.findViewById(R.id.tvNoOfVehicles);
            tvBidPrice = view.findViewById(R.id.tvBidPrice);
            tvTonnage = view.findViewById(R.id.tvTonnage);
            cardView = view.findViewById(R.id.card_view);
            imgCall = view.findViewById(R.id.imgCall);

            cardView.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {

                }
            });

            imgCall.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    String phoneNo = dataList.get(getAdapterPosition()).brokerPhone;
                    Utils.launchDialer(view.getContext(),"+91"+phoneNo);
                }
            });
        }

    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.row_available_quote, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        AvailableQuoteData availableQuoteData = dataList.get(position);

        int bidNo = position +1;
        holder.tvBidNo.setText("BID "+bidNo);
        holder.tvTransporterName.setText(Utils.def(availableQuoteData.brokerName, ""));
        holder.tvNoOfVehicles.setText(Utils.def(availableQuoteData.noOfVehicles+"", ""));
        holder.tvBidPrice.setText(Utils.def(availableQuoteData.rate+"", ""));
        holder.tvTonnage.setText(Utils.def(availableQuoteData.tonnage+"", ""));

        // set no of vehicle field
        String noOfVehicle = String.valueOf(availableQuoteData.noOfVehicles);
        if(noOfVehicle == null || noOfVehicle.equalsIgnoreCase("-1")) {
            noOfVehicle = "-";
        }
        holder.tvNoOfVehicles.setText(noOfVehicle);
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }


}
