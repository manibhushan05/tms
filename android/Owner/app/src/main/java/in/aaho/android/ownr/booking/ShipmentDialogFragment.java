package in.aaho.android.ownr.booking;

import android.os.Bundle;
import android.support.annotation.Nullable;
import android.support.v7.widget.DefaultItemAnimator;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.List;

import in.aaho.android.ownr.common.BaseDialogFragment;
import in.aaho.android.ownr.R;

/**
 * Created by mani on 8/8/16.
 */

public class ShipmentDialogFragment extends BaseDialogFragment {

    private RecyclerView shipDialogContainer, customShipDialogContainer;
    private TextView addCustomShipBtn;
    private Button doneButton;
    private TextView truckCountTextView;
    private View dialogView;
    // private NestedScrollView scrollView;

    private BookingActivity bookingActivity;

    private ShipDialogAdapter shipDialogAdapter;
    private CustomShipDialogAdapter customShipDialogAdapter;
    private List<Shipment> shipList = new ArrayList<>();
    private List<CustomShipment> customShipList = new ArrayList<>();

    public void setShipments(List<Shipment> shipments) {
        this.shipList = shipments;
    }

    public void setCustomShipments(List<CustomShipment> customShips) {
        this.customShipList = customShips;
    }

    public void setBookingActivity(BookingActivity bookingActivity) {
        this.bookingActivity = bookingActivity;
    }

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        shipDialogAdapter = new ShipDialogAdapter(shipList, this);
        customShipDialogAdapter = new CustomShipDialogAdapter(customShipList, this);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        dialogView = inflater.inflate(R.layout.booking_ship_dialog, container, false);

        setViewVariables();
        setClickListeners();
        setupAdapters();

        return dialogView;
    }

    private void setupAdapters() {
        setupShipDialogAdapter();
        setupCustomShipDialogAdapter();
    }

    private void setupShipDialogAdapter() {
        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getActivity().getApplicationContext());
        shipDialogContainer.setLayoutManager(mLayoutManager);
        shipDialogContainer.setItemAnimator(new DefaultItemAnimator());
        shipDialogContainer.setAdapter(shipDialogAdapter);

        shipDialogAdapter.notifyDataSetChanged();
    }

    private void setupCustomShipDialogAdapter() {
        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getActivity().getApplicationContext());
        customShipDialogContainer.setLayoutManager(mLayoutManager);
        customShipDialogContainer.setItemAnimator(new DefaultItemAnimator());
        customShipDialogContainer.setAdapter(customShipDialogAdapter);

        customShipDialogAdapter.notifyDataSetChanged();
    }


    private void setClickListeners() {
        doneButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                bookingActivity.updateAllDisplayShipments();
                ShipmentDialogFragment.this.dismiss();
            }
        });
        addCustomShipBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                customShipList.add(new CustomShipment());
                customShipDialogAdapter.notifyItemInserted(customShipList.size() - 1);
                //scrollView.post(new Runnable() {
                //    public void run() {
                //        scrollView.fullScroll(scrollView.FOCUS_DOWN);
                //    }
                //});
            }
        });
    }

    private void setViewVariables() {
        // scrollView = (NestedScrollView) dialogView.findViewById(R.id.ship_dialog_scroll_view);
        shipDialogContainer = dialogView.findViewById(R.id.ship_dialog_container);
        customShipDialogContainer = dialogView.findViewById(R.id.custom_ship_dialog_container);
        truckCountTextView = dialogView.findViewById(R.id.ship_dialog_shipment_msg_count);
        addCustomShipBtn = dialogView.findViewById(R.id.custom_ship_add_btn);
        doneButton = dialogView.findViewById(R.id.ship_dialog_done_btn);
    }

    public void updateTruckCount() {
        int count = 0;
        for (Shipment ship: shipList) {
            count = count + ship.getCount();
        }
        for (CustomShipment ship: customShipList) {
            count = count + ship.getCount();
        }
        updateTruckCountUI(count);
    }

    private void updateTruckCountUI(int count) {
        if (truckCountTextView != null) {
            truckCountTextView.setText(String.valueOf(count));
        }
    }
}