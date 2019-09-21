package in.aaho.android.aahocustomers.map;

/**
 * Created by mani on 6/8/16.
 */

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.aahocustomers.R;
import in.aaho.android.aahocustomers.common.BaseActivity;
import in.aaho.android.aahocustomers.common.ListItemListerner;
import in.aaho.android.aahocustomers.common.Utils;
import in.aaho.android.aahocustomers.drivers.BrokerDriver;


public class TrackVehiclesAdapter extends RecyclerView.Adapter<TrackVehiclesAdapter.MyViewHolder> {

    private TrackSelectListener listener;
    private List<TrackingData> trackList;
    private BaseActivity activity;

    public TrackVehiclesAdapter(BaseActivity activity, List<TrackingData> trackList, TrackSelectListener listener) {
        this.trackList = trackList;
        this.listener = listener;
        this.activity = activity;
    }

    public class MyViewHolder extends RecyclerView.ViewHolder {
        public LinearLayout callDriverBtn, trackBtn;
        public TextView trackCardDriverNameTv, trackCardDriverNumberTv, trackCardLocationDetailsTv;
        public TextView trackCardTruckNoTv;

        public TrackClickListener trackClickListener;
        public CallDriverClickListener callClickListener;

        public MyViewHolder(View view) {
            super(view);
            callDriverBtn = view.findViewById(R.id.call_driver_btn);
            trackBtn = view.findViewById(R.id.track_btn);
            trackCardDriverNameTv = view.findViewById(R.id.track_card_driver_name_tv);
            trackCardDriverNumberTv = view.findViewById(R.id.track_card_driver_number_tv);
            trackCardLocationDetailsTv = view.findViewById(R.id.track_card_location_details_tv);
            trackCardTruckNoTv = view.findViewById(R.id.track_card_truck_no_tv);

            trackClickListener = new TrackClickListener();
            callClickListener = new CallDriverClickListener();

            trackBtn.setOnClickListener(trackClickListener);
            callDriverBtn.setOnClickListener(callClickListener);
        }

        public void updateListenerPositions(int position) {
            trackClickListener.updatePosition(position);
            callClickListener.updatePosition(position);
        }
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.vehicle_track_detail_card, parent, false);
        return new MyViewHolder(itemView);
    }


    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        TrackingData data = trackList.get(position);
        holder.updateListenerPositions(position);
        holder.trackCardDriverNameTv.setText(
                data.getDriver() == null ? "-" : Utils.def(data.getDriver().getName(), "-")
        );
        holder.trackCardDriverNumberTv.setText(
                data.getDriver() == null ? "-" : Utils.def(data.getDriver().getPhone(), "-")
        );
        holder.trackCardTruckNoTv.setText(Utils.def(data.getVehicleNumber(), "-"));
        holder.trackCardLocationDetailsTv.setText(
                data.getLastLocation() == null ? "-" : data.getLastLocation().text()
        );

    }

    @Override
    public int getItemCount() {
        return trackList.size();
    }

    private class CallDriverClickListener extends ListItemListerner implements View.OnClickListener {

        @Override
        public void onClick(View v) {
            TrackingData data = trackList.get(position);
            BrokerDriver driver = data.getDriver();
            if (driver == null) {
                Utils.toast("driver not set");
                return;
            }
            activity.launchDialer(driver.getPhone());
        }
    }

    private class TrackClickListener extends ListItemListerner implements View.OnClickListener {

        @Override
        public void onClick(View v) {
            TrackingData data = trackList.get(position);
            if (listener != null) {
                listener.onSelect(data);
            }
        }
    }
}
