package in.aaho.android.ownr.loads;

/**
 * Created by mani on 6/8/16.
 */

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.TextView;

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.common.BaseActivity;
import in.aaho.android.ownr.common.ListItemListerner;
import in.aaho.android.ownr.common.Utils;



public class VehicleRequestAdapter extends RecyclerView.Adapter<VehicleRequestAdapter.MyViewHolder> {
    private final BaseActivity activity;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        public TextView fromCityTv, fromStateTv, shipmentDateTv, toCityTv, toStateTv, vehicleCountTv;
        public TextView vehicleTypeTv;

        public LinearLayout launchSendQuoteBtn, sentQuoteLayout;
        public TextView sentQuoteTv;


        public SendQuoteClickListener clickListener;

        public MyViewHolder(View view) {
            super(view);
            fromCityTv = view.findViewById(R.id.from_city_tv);
            fromStateTv = view.findViewById(R.id.from_state_tv);
            toCityTv = view.findViewById(R.id.to_city_tv);
            toStateTv = view.findViewById(R.id.to_state_tv);
            shipmentDateTv = view.findViewById(R.id.shipment_date_tv);
            vehicleTypeTv = view.findViewById(R.id.vehicle_type_tv);
            vehicleCountTv = view.findViewById(R.id.vehicle_count_tv);

            launchSendQuoteBtn = view.findViewById(R.id.launch_send_quote_btn);
            sentQuoteLayout = view.findViewById(R.id.sent_quote_layout);
            sentQuoteTv = view.findViewById(R.id.sent_quote_tv);

            clickListener = new SendQuoteClickListener();

            launchSendQuoteBtn.setOnClickListener(clickListener);
        }

        public void updateListenerPositions(int position) {
            clickListener.updatePosition(position);
        }
    }

    public VehicleRequestAdapter(BaseActivity activity) {
        this.activity = activity;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.vehicle_request_row, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        VehicleRequest vehicleRequest = AvailableLoadsActivity.getRequestList().get(position);
        holder.updateListenerPositions(position);

        holder.fromCityTv.setText(Utils.def(vehicleRequest.fromCity, ""));
        holder.fromStateTv.setText(Utils.def(vehicleRequest.fromState, ""));
        holder.toCityTv.setText(Utils.def(vehicleRequest.toCity, ""));
        holder.toStateTv.setText(Utils.def(vehicleRequest.toState, ""));
        holder.shipmentDateTv.setText(Utils.formatDateSimple(vehicleRequest.shipmentDate));
        holder.vehicleTypeTv.setText(Utils.def(vehicleRequest.getName(), ""));
        holder.vehicleCountTv.setText(String.valueOf(vehicleRequest.quantity));

        if (vehicleRequest.quote == null) {
            holder.launchSendQuoteBtn.setVisibility(View.VISIBLE);
            holder.sentQuoteLayout.setVisibility(View.GONE);
        } else {
            holder.launchSendQuoteBtn.setVisibility(View.GONE);
            holder.sentQuoteLayout.setVisibility(View.VISIBLE);
            holder.sentQuoteTv.setText(vehicleRequest.quote.getQuoteText());
        }
    }

    @Override
    public int getItemCount() {
        return AvailableLoadsActivity.getRequestList().size();
    }

    private class SendQuoteClickListener extends ListItemListerner implements View.OnClickListener {

        @Override
        public void onClick(View v) {
            showEditQuoteDialog(position);
        }
    }

    private void showEditQuoteDialog(final int position) {
        VehicleRequest vehicleRequest = AvailableLoadsActivity.getRequestList().get(position);
        SendQuoteDialogFragment.showNewDialog(activity, vehicleRequest, new SendQuoteDialogFragment.QuoteSentListener() {
            @Override
            public void onSuccess(VehicleRequestQuote quote) {
                AvailableLoadsActivity.getRequestList().get(position).quote = quote;
                notifyItemChanged(position);
            }
        });
    }

}
